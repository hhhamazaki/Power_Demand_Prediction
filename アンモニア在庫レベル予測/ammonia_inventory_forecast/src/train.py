"""
アンモニア在庫レベル予測システム - 学習モジュール
発電量に基づくアンモニア消費予測の高精度化
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import sys
import os
import warnings
warnings.filterwarnings('ignore')

# エンコーディング設定
import locale
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.preprocess import load_data, handle_missing_values, detect_refill_events

class AmmoniaTrainingSystem:
    def __init__(self):
        self.models = {}
        self.weights = {}
        self.scaler = None
        self.features = []
        self.consumption_rate_median = 0.0
        self.consumption_rate_std = 0.0
        self.feature_importance = {}
        self.refill_threshold = 500.0  # 自動補給閾値（運用固定値に合わせる）
        self.refill_amount = 500.0     # 補給量（学習時にモデルへ保存）
        
    def create_time_features(self, df):
        """時系列特徴量の生成"""
        df = df.copy()
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # 季節性（円形特徴量）
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        df['day_sin'] = np.sin(2 * np.pi * df['day'] / 31)
        df['day_cos'] = np.cos(2 * np.pi * df['day'] / 31)
        
        return df
    
    def create_lag_features(self, df, max_lag=7):
        """改良されたラグ特徴量"""
        df = df.copy()
        
        # アンモニアのラグ（安全なラグ生成）
        for lag in [1, 2, 3, 7]:
            if lag <= max_lag:
                df[f'ammonia_lag{lag}'] = df['actual_ammonia'].shift(lag)
        
        # 発電量のラグ
        for lag in [1, 2, 3]:
            df[f'power_lag{lag}'] = df['actual_power'].shift(lag)
        
        # 移動平均（前方向きウィンドウ）
        for window in [3, 7]:
            df[f'ammonia_ma{window}'] = df['actual_ammonia'].rolling(window=window, min_periods=1).mean()
            df[f'power_ma{window}'] = df['actual_power'].rolling(window=window, min_periods=1).mean()
            df[f'ammonia_std{window}'] = df['actual_ammonia'].rolling(window=window, min_periods=1).std()
        
        # 差分
        df['ammonia_diff1'] = df['actual_ammonia'].diff(1)
        df['power_diff1'] = df['actual_power'].diff(1)
        
        return df
    
    def calculate_consumption_rate(self, df):
        """発電量に基づく消費率計算（物理ベース）"""
        df = df.copy()
        
        # 日次消費量と消費率
        df['daily_consumption'] = 0.0
        df['consumption_rate'] = 0.0
        
        valid_rates = []
        
        for i in range(1, len(df)):
            if df.iloc[i]['is_refill'] == 0:  # 補給日以外
                prev_ammonia = df.iloc[i-1]['actual_ammonia']
                curr_ammonia = df.iloc[i]['actual_ammonia']
                curr_power = df.iloc[i]['actual_power']
                
                # 有効なデータのみ処理
                if (not pd.isna(prev_ammonia) and not pd.isna(curr_ammonia) and 
                    curr_power > 0 and prev_ammonia > curr_ammonia):
                    
                    consumption = prev_ammonia - curr_ammonia
                    df.iloc[i, df.columns.get_loc('daily_consumption')] = consumption
                    
                    # 消費率計算（m³/MWh）
                    rate = consumption / (curr_power / 1000)  # kWh → MWh変換
                    if 0 < rate < 0.5:  # 異常値除外
                        df.iloc[i, df.columns.get_loc('consumption_rate')] = rate
                        valid_rates.append(rate)
        
        return df, valid_rates
    
    def create_consumption_features(self, df):
        """消費率関連特徴量（物理ベース強化版）"""
        df, valid_rates = self.calculate_consumption_rate(df)
        
        # 消費率統計値を保存
        if valid_rates:
            self.consumption_rate_median = np.median(valid_rates)
            self.consumption_rate_std = np.std(valid_rates)
        else:
            self.consumption_rate_median = 0.021  # デフォルト値（m³/MWh）
            self.consumption_rate_std = 0.005
        
        print(f"計算された消費率: {self.consumption_rate_median:.6f} ± {self.consumption_rate_std:.6f} m^3/MWh")
        
        # 消費率の統計量
        df['consumption_rate_ma3'] = df['consumption_rate'].rolling(window=3, min_periods=1).mean()
        df['consumption_rate_ma7'] = df['consumption_rate'].rolling(window=7, min_periods=1).mean()
        df['consumption_rate_std3'] = df['consumption_rate'].rolling(window=3, min_periods=1).std()
        
        # 動的消費率特徴量を追加（発電量に応じた効率）
        df['dynamic_consumption_rate'] = 0.0
        df['power_efficiency'] = 1.0
        
        for i in range(len(df)):
            curr_power = df.iloc[i]['actual_power']
            if curr_power > 0:
                power_mwh = curr_power / 1000
                # 発電量に応じた効率係数（固定値なし）
                power_factor = 1.0 + (power_mwh - 400) / 1000  # 400MWh基準
                df.iloc[i, df.columns.get_loc('power_efficiency')] = power_factor
                
                if df.iloc[i]['consumption_rate'] > 0:
                    dynamic_rate = df.iloc[i]['consumption_rate'] * power_factor
                    df.iloc[i, df.columns.get_loc('dynamic_consumption_rate')] = dynamic_rate
        
        # 動的消費率の統計量
        df['dynamic_consumption_rate_ma3'] = df['dynamic_consumption_rate'].rolling(window=3, min_periods=1).mean()
        df['dynamic_consumption_rate_ma7'] = df['dynamic_consumption_rate'].rolling(window=7, min_periods=1).mean()
        df['power_efficiency_ma3'] = df['power_efficiency'].rolling(window=3, min_periods=1).mean()
        df['consumption_rate_ma7'] = df['consumption_rate'].rolling(window=7, min_periods=1).mean()
        df['consumption_rate_std3'] = df['consumption_rate'].rolling(window=3, min_periods=1).std()
        
        # 累積発電量（補給サイクル内）
        df['cumulative_power'] = 0.0
        cumul_power = 0
        
        for i in range(len(df)):
            if df.iloc[i]['is_refill'] == 1:
                cumul_power = 0
            else:
                cumul_power += df.iloc[i]['actual_power']
            df.iloc[i, df.columns.get_loc('cumulative_power')] = cumul_power
        
        # 補給後日数
        df['days_since_refill'] = 0
        days_count = 0
        
        for i in range(len(df)):
            if df.iloc[i]['is_refill'] == 1:
                days_count = 0
            else:
                days_count += 1
            df.iloc[i, df.columns.get_loc('days_since_refill')] = days_count
        
        # 発電量ベースの理論消費量（特徴量追加）
        df['theoretical_consumption'] = df['actual_power'] / 1000 * self.consumption_rate_median
        df['consumption_efficiency'] = df['daily_consumption'] / (df['theoretical_consumption'] + 1e-8)  # ゼロ除算回避
        
        return df
    
    def train(self, data_path):
        """モデル学習"""
        print("=== データ読み込み ===")
        df = load_data(data_path)
        df = handle_missing_values(df, method='interpolate')
        df = detect_refill_events(df, threshold=50)
        
        print("=== 特徴量生成 ===")
        df = self.create_time_features(df)
        df = self.create_lag_features(df)
        df = self.create_consumption_features(df)
        
        # 特徴量選択
        candidate_features = [
            'actual_power', 'day_of_week', 'month', 'is_weekend',
            'month_sin', 'month_cos', 'day_sin', 'day_cos',
            'ammonia_lag1', 'ammonia_lag2', 'ammonia_lag3', 'ammonia_lag7',
            'power_lag1', 'power_lag2', 'power_lag3',
            'ammonia_ma3', 'ammonia_ma7', 'power_ma3', 'power_ma7',
            'ammonia_std3', 'ammonia_std7', 'ammonia_diff1', 'power_diff1',
            'daily_consumption', 'consumption_rate', 'consumption_rate_ma3',
            'consumption_rate_ma7', 'consumption_rate_std3',
            'dynamic_consumption_rate', 'dynamic_consumption_rate_ma3', 'dynamic_consumption_rate_ma7',
            'power_efficiency', 'power_efficiency_ma3',
            'cumulative_power', 'days_since_refill',
            'theoretical_consumption', 'consumption_efficiency'  # 新規特徴量
        ]
        
        self.features = [col for col in candidate_features if col in df.columns]
        print(f"使用特徴量数: {len(self.features)}")
        
        # 学習データ準備（実際のアンモニア値が存在するデータのみを使用）
        train_mask = (
            (df.index >= 10) &  # 十分なラグ
            (df['is_refill'] == 0) &  # 補給日以外
            (~df['actual_ammonia'].isna()) &  # ターゲット値有効
            (df['actual_ammonia'] > 0) &  # 正の値
            (df['actual_ammonia'] < 1200)  # 異常値除外
        )
        
        train_data = df[train_mask].copy()
        
        if len(train_data) < 50:
            print("Error: 学習データが不足しています")
            return False
        
        print(f"学習データ数: {len(train_data)}")
        
        # 特徴量とターゲット
        X = train_data[self.features].copy()
        y = train_data['actual_ammonia'].copy()
        
        # 欠損値処理
        imputer = SimpleImputer(strategy='median')
        X_imputed = pd.DataFrame(
            imputer.fit_transform(X),
            columns=X.columns,
            index=X.index
        )
        
        # 異常値処理
        for col in X_imputed.columns:
            q99 = X_imputed[col].quantile(0.99)
            q01 = X_imputed[col].quantile(0.01)
            X_imputed[col] = X_imputed[col].clip(q01, q99)
        
        # 標準化
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X_imputed)
        
        # モデル定義（より保守的なパラメータ）
        models_config = {
            'rf': RandomForestRegressor(
                n_estimators=50,
                max_depth=8,
                min_samples_split=10,
                min_samples_leaf=5,
                random_state=42
            ),
            'gbm': GradientBoostingRegressor(
                n_estimators=50,
                max_depth=4,
                learning_rate=0.1,
                min_samples_split=10,
                min_samples_leaf=5,
                random_state=42
            ),
            'ridge': Ridge(alpha=10.0)
        }
        
        # モデル学習と評価
        print("\n=== モデル学習結果 ===")
        for name, model in models_config.items():
            if name == 'ridge':
                model.fit(X_scaled, y)
                pred = model.predict(X_scaled)
            else:
                model.fit(X_imputed, y)
                pred = model.predict(X_imputed)
            
            mae = mean_absolute_error(y, pred)
            r2 = r2_score(y, pred)
            
            print(f"{name}: MAE={mae:.2f}, R2={r2:.4f}")
            
            self.models[name] = model
            self.weights[name] = 1 / (mae + 1)
        
        # 重み正規化
        total_weight = sum(self.weights.values())
        self.weights = {k: v/total_weight for k, v in self.weights.items()}
        
        print(f"\n=== モデル重み ===")
        for name, weight in self.weights.items():
            print(f"{name}: {weight:.3f}")
        
        # 消費率の中央値を保存
        self.consumption_rate_median = df['consumption_rate'].replace(0, np.nan).median()
        if pd.isna(self.consumption_rate_median):
            self.consumption_rate_median = 0.00002088  # デフォルト値
        
        return True
    
    def save_model(self, filepath):
        """モデル保存"""
        model_data = {
            'models': self.models,
            'weights': self.weights,
            'scaler': self.scaler,
            'features': self.features,
            'consumption_rate_median': self.consumption_rate_median,
            'consumption_rate_std': self.consumption_rate_std,
            'refill_threshold': self.refill_threshold,
            'refill_amount': self.refill_amount
        }
        # 保存先ディレクトリが存在しない場合は作成
        dirpath = os.path.dirname(filepath)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)

        joblib.dump(model_data, filepath)
        print(f"モデルを {filepath} に保存しました")
        
    def load_model(self, filepath):
        """モデル読み込み"""
        try:
            model_data = joblib.load(filepath)
            self.models = model_data['models']
            self.weights = model_data['weights']
            self.scaler = model_data['scaler']
            self.features = model_data['features']
            self.consumption_rate_median = model_data.get('consumption_rate_median', 0.021)
            self.consumption_rate_std = model_data.get('consumption_rate_std', 0.005)
            self.refill_threshold = model_data.get('refill_threshold', 80.0)
            print(f"モデルを {filepath} から読み込みました")
            return True
        except Exception as e:
            print(f"モデル読み込みエラー: {e}")
            return False

if __name__ == '__main__':
    print("=== アンモニア在庫予測システム - 学習モジュール ===")
    
    # 学習システム初期化
    training_system = AmmoniaTrainingSystem()
    
    # モデル学習
    # 相対パス 'data/...' をスクリプトのプロジェクトルートから解決する
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_path = os.path.join(project_root, 'data', 'training_data.csv')
    if training_system.train(data_path):
        
        # モデル保存
        training_system.save_model('models/ammonia_prediction_model.pkl')
        
        print("\n[完了] 学習完了！")
        print(f"消費率: {training_system.consumption_rate_median:.6f} m^3/MWh")
        print(f"補給閾値: {training_system.refill_threshold} m^3")
        print("予測を実行するには predict.py を使用してください")
        
    else:
        print("[エラー] 学習に失敗しました")