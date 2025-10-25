"""
アンモニア在庫レベル予測システム - 予測モジュール
発電量に基づくアンモニア消費予測の高精度化
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
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

class AmmoniaPredictionSystem:
    def __init__(self):
        self.models = {}
        self.weights = {}
        self.scaler = None
        self.features = []
        self.consumption_rate_median = 0.025  # m³/MWh
        self.consumption_rate_std = 0.005
        self.refill_threshold = 500.0  # 人間運用: 500m³で発注
        self.refill_amount = 500.0     # 人間運用: 500m³補給
        # 補給後に到達させたい目標水準 (None の場合は無視)
        self.refill_target_post_level = None
        self.model_loaded = False
        
    def load_model(self, filepath):
        """学習済みモデル読み込み"""
        try:
            model_data = joblib.load(filepath)
            self.models = model_data['models']
            self.weights = model_data['weights']
            self.scaler = model_data['scaler']
            self.features = model_data['features']
            self.consumption_rate_median = model_data.get('consumption_rate_median', 0.025)
            self.consumption_rate_std = model_data.get('consumption_rate_std', 0.005)
            # 運用方針: 予測実行時は運用固定値を優先して使用する
            # （モデル保存値があっても無視して常に運用閾値を適用）
            self.refill_threshold = 500.0  # 運用固定: 発注閾値
            self.refill_amount = 500.0     # 運用固定: 補給量
            
            # 消費率の修正（間違った変換を修正）
            if self.consumption_rate_median < 0.001:
                self.consumption_rate_median = 0.025  # 正しい物理ベース値
                print("消費率を物理ベース値に修正しました")
            
            self.model_loaded = True
            print(f"モデルを {filepath} から読み込みました")
            print(f"消費率: {self.consumption_rate_median:.6f} m³/MWh")
            print(f"人間運用ルール適用: 発注閾値={self.refill_threshold}m³, 補給量={self.refill_amount}m³")
            return True
        except Exception as e:
            print(f"モデル読み込みエラー: {e}")
            return False
    
    def calculate_physical_consumption(self, power_kw):
        """物理ベースアンモニア消費計算"""
        if power_kw <= 0:
            return 0.0
        
        power_mwh = power_kw / 1000  # kWをMWhに変換
        consumption = power_mwh * self.consumption_rate_median
        return max(0.0, consumption)
    
    def create_time_features(self, df):
        """時系列特徴量の生成"""
        df = df.copy()
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # 季節性
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        df['day_sin'] = np.sin(2 * np.pi * df['day'] / 31)
        df['day_cos'] = np.cos(2 * np.pi * df['day'] / 31)
        
        return df
    
    def create_lag_features(self, df, max_lag=7):
        """ラグ特徴量の生成"""
        df = df.copy()
        
        # アンモニアのラグ
        for lag in [1, 2, 3, 7]:
            if lag <= max_lag:
                df[f'ammonia_lag{lag}'] = df['actual_ammonia'].shift(lag)
        
        # 発電量のラグ
        for lag in [1, 2, 3]:
            df[f'power_lag{lag}'] = df['actual_power'].shift(lag)
        
        # 移動平均
        for window in [3, 7]:
            df[f'ammonia_ma{window}'] = df['actual_ammonia'].rolling(window=window, min_periods=1).mean()
            df[f'power_ma{window}'] = df['actual_power'].rolling(window=window, min_periods=1).mean()
            df[f'ammonia_std{window}'] = df['actual_ammonia'].rolling(window=window, min_periods=1).std()
        
        # 差分
        df['ammonia_diff1'] = df['actual_ammonia'].diff(1)
        df['power_diff1'] = df['actual_power'].diff(1)
        
        return df
    
    def create_consumption_features(self, df):
        """消費率関連特徴量"""
        df = df.copy()
        
        df['daily_consumption'] = 0.0
        df['consumption_rate'] = 0.0
        df['theoretical_consumption'] = 0.0
        df['consumption_efficiency'] = 1.0
        
        for i in range(len(df)):
            curr_power = df.iloc[i]['actual_power']
            
            # 理論消費量
            theoretical_consumption = self.calculate_physical_consumption(curr_power)
            df.iloc[i, df.columns.get_loc('theoretical_consumption')] = theoretical_consumption
            
            if i > 0 and df.iloc[i]['is_refill'] == 0:
                prev_ammonia = df.iloc[i-1]['actual_ammonia']
                curr_ammonia = df.iloc[i]['actual_ammonia']
                
                if (not pd.isna(prev_ammonia) and not pd.isna(curr_ammonia) and 
                    curr_power > 0):
                    
                    actual_consumption = prev_ammonia - curr_ammonia
                    if actual_consumption > 0:
                        df.iloc[i, df.columns.get_loc('daily_consumption')] = actual_consumption
                        
                        power_mwh = curr_power / 1000
                        consumption_rate = actual_consumption / power_mwh
                        
                        if 0 < consumption_rate < 0.5:
                            df.iloc[i, df.columns.get_loc('consumption_rate')] = consumption_rate
                        
                        if theoretical_consumption > 0:
                            efficiency = actual_consumption / theoretical_consumption
                            df.iloc[i, df.columns.get_loc('consumption_efficiency')] = min(2.0, max(0.1, efficiency))
        
        df['consumption_rate_ma3'] = df['consumption_rate'].rolling(window=3, min_periods=1).mean()
        df['consumption_rate_ma7'] = df['consumption_rate'].rolling(window=7, min_periods=1).mean()
        
        return df
    
    def predict_single(self, features):
        """単一データポイントの予測"""
        if not self.model_loaded:
            return None
            
        try:
            features_clean = np.nan_to_num(features, nan=0.0)
            features_scaled = self.scaler.transform(features_clean.reshape(1, -1))
            
            ensemble_pred = 0.0
            for name, model in self.models.items():
                if name == 'ridge':
                    pred = model.predict(features_scaled)[0]
                else:
                    pred = model.predict(features_clean.reshape(1, -1))[0]
                
                ensemble_pred += self.weights[name] * pred
            
            return ensemble_pred
        except Exception as e:
            return None
    
    def detect_refill_timing(self, predicted_ammonia, days_since_refill):
        """補給タイミング自動検出（人間運用ベース）"""
        # 基本条件: 設定された発注閾値以下で補給判定（READMEと整合）
        # 例: README では在庫500m³以下で緊急補給判定となっているので
        # self.refill_threshold を 500 に設定していればここでそれが適用されます
        if predicted_ammonia <= self.refill_threshold:
            return True
        
        # 緊急条件: 15日経過 + 発注閾値以下で緊急補給判定（閾値は refill_threshold と同一）
        if days_since_refill >= 15 and predicted_ammonia <= self.refill_threshold:
            return True
            
        return False
    
    def predict(self, data_path, output_path='data/predictions.csv'):
        """予測実行（空白期間自動検出）"""
        print("=== アンモニア在庫予測開始 ===")
        
        # データ準備
        df = load_data(data_path)
        # 欠損値処理はパワーのみ（アンモニアの空白は予測対象なので保持）
        df['actual_power'] = df['actual_power'].interpolate(method='linear')
        df = detect_refill_events(df, threshold=50)
        df = self.create_time_features(df)
        df = self.create_lag_features(df)
        df = self.create_consumption_features(df)
        
        print(f"予測期間: {len(df)}日")
        
        # 結果データフレーム準備
        result_df = df[['date', 'actual_power']].copy()
        
        # actual_ammoniaの処理（空白期間は予測対象）
        actual_ammonia = []
        is_refill = []
        forecast_count = 0
        
        for i in range(len(df)):
            actual_val = df.iloc[i]['actual_ammonia']
            if not pd.isna(actual_val):
                actual_ammonia.append(actual_val)
                is_refill.append(df.iloc[i]['is_refill'])
            else:
                # 予測対象期間（空白期間）
                actual_ammonia.append(np.nan)
                is_refill.append(0)
                forecast_count += 1
        
        print(f"予測対象期間（空白）: {forecast_count}日")
        print(f"実績期間: {len(df) - forecast_count}日")
        
        result_df['actual_ammonia'] = actual_ammonia
        result_df['is_refill'] = is_refill
        result_df['predicted_ammonia'] = 0.0
        
        # 初期値設定
        last_actual_idx = None
        for i in range(len(result_df)-1, -1, -1):
            if not pd.isna(result_df.iloc[i]['actual_ammonia']):
                last_actual_idx = i
                break
        
        if last_actual_idx is not None:
            initial_ammonia = result_df.iloc[last_actual_idx]['actual_ammonia']
            print(f"初期アンモニア在庫: {initial_ammonia:.1f} m^3")
        else:
            initial_ammonia = 800.0
            print(f"初期アンモニア在庫: {initial_ammonia:.1f} m^3 (デフォルト値)")
        
        # 予測ループ
        for i in range(len(result_df)):
            current_date = result_df.iloc[i]['date']
            current_power = result_df.iloc[i]['actual_power']
            
            if i == 0:
                if not pd.isna(result_df.iloc[i]['actual_ammonia']):
                    predicted_ammonia = result_df.iloc[i]['actual_ammonia']
                else:
                    predicted_ammonia = initial_ammonia
            else:
                prev_predicted = result_df.iloc[i-1]['predicted_ammonia']
                
                if (not pd.isna(result_df.iloc[i]['actual_ammonia']) and 
                    result_df.iloc[i]['is_refill'] == 1):
                    # 実際の補給データ
                    predicted_ammonia = result_df.iloc[i]['actual_ammonia']
                    result_df.iloc[i, result_df.columns.get_loc('is_refill')] = 1
                else:
                    # 予測対象期間かどうかの判定
                    is_forecast_period = pd.isna(result_df.iloc[i]['actual_ammonia'])
                    
                    # 物理ベース予測
                    consumption = self.calculate_physical_consumption(current_power)
                    physics_pred = max(0, prev_predicted - consumption)
                    
                    if is_forecast_period:
                        # 予測対象期間：物理ベース100%
                        predicted_ammonia = physics_pred
                        print(f"{current_date.strftime('%m/%d')}[予測期間]: 発電{current_power/1000:6.1f}MWh → 消費{consumption:.2f}m³ → 在庫{physics_pred:.1f}m³")
                    else:
                        # 実績期間：ML + 物理ベースのハイブリッド
                        ml_pred = None
                        if self.model_loaded:
                            try:
                                current_idx = df[df['date'] == current_date].index
                                if len(current_idx) > 0:
                                    idx = current_idx[0]
                                    if idx < len(df):
                                        features = df.iloc[idx][self.features].values
                                        ml_pred = self.predict_single(features)
                            except Exception as e:
                                pass
                        
                        if ml_pred is not None and not np.isnan(ml_pred):
                            predicted_ammonia = 0.7 * ml_pred + 0.3 * physics_pred
                        else:
                            predicted_ammonia = physics_pred
                
                # 物理制約
                predicted_ammonia = max(0, min(predicted_ammonia, 1200))
                
                # 補給タイミング自動検出（人間運用に合わせて前日終値で判定）
                if i > 0:
                    prev_predicted = result_df.iloc[i-1]['predicted_ammonia']
                    # 直近の補給日からの経過日数を計算（補給が無ければ開始日からの経過日数）
                    if i == 0:
                        days_since_refill = 0
                    else:
                        prev_slice = result_df.iloc[:i]
                        refill_indices = prev_slice[prev_slice['is_refill'] == 1].index
                        if len(refill_indices) > 0:
                            last_refill_idx = int(refill_indices[-1])
                            days_since_refill = i - last_refill_idx
                        else:
                            # 補給履歴が無い場合は先頭からの経過日数を使用
                            days_since_refill = i
                    if self.detect_refill_timing(prev_predicted, days_since_refill):
                        # 通常は refill_amount を加算するが、目標ポスト水準が指定されていれば
                        # その水準を満たすまで補給量を調整する
                        if self.refill_target_post_level is not None:
                            needed = self.refill_target_post_level - predicted_ammonia
                            add_amount = max(self.refill_amount, needed)
                            # 必要がなければ最低補給量を適用
                            predicted_ammonia += max(self.refill_amount, needed)
                        else:
                            predicted_ammonia += self.refill_amount
                        predicted_ammonia = min(predicted_ammonia, 1200)
                        result_df.iloc[i, result_df.columns.get_loc('is_refill')] = 1
                        print(f"{current_date.strftime('%m/%d')}: 自動補給実行（前日終値{prev_predicted:.1f}→補給後{predicted_ammonia:.1f}）")
            
            result_df.iloc[i, result_df.columns.get_loc('predicted_ammonia')] = predicted_ammonia
        
        # 誤差計算
        result_df['prediction_error'] = np.nan
        result_df['prediction_error_pct'] = np.nan
        
        valid_mask = ~pd.isna(result_df['actual_ammonia'])
        if valid_mask.any():
            valid_actual = result_df.loc[valid_mask, 'actual_ammonia']
            valid_predicted = result_df.loc[valid_mask, 'predicted_ammonia']
            
            result_df.loc[valid_mask, 'prediction_error'] = valid_actual - valid_predicted
            
            non_zero_mask = valid_mask & (result_df['actual_ammonia'] != 0)
            if non_zero_mask.any():
                result_df.loc[non_zero_mask, 'prediction_error_pct'] = (
                    result_df.loc[non_zero_mask, 'prediction_error'] / 
                    result_df.loc[non_zero_mask, 'actual_ammonia'] * 100
                )
        
        # 保存
        result_df.to_csv(output_path, index=False)
        print(f"予測結果を {output_path} に保存しました")
        
        # 精度計算
        if valid_mask.any():
            mae = np.abs(result_df.loc[valid_mask, 'prediction_error']).mean()
            rmse = np.sqrt((result_df.loc[valid_mask, 'prediction_error'] ** 2).mean())
            
            print(f"\n=== 予測精度 ===")
            print(f"MAE: {mae:.2f} m^3")
            print(f"RMSE: {rmse:.2f} m^3")
            print(f"予測対象日数: {len(result_df)}日")
            print(f"実測値有り: {valid_mask.sum()}日")
        
        # 予測期間の確認
        forecast_data = result_df.tail(20).reset_index(drop=True)
        print(f"\n=== 予測期間の発電対応アンモニア消費確認 ===")
        for idx, row in forecast_data.iterrows():
            date_str = row['date'].strftime('%m/%d')
            power_mwh = row['actual_power'] / 1000
            predicted = row['predicted_ammonia']
            is_forecast = pd.isna(row['actual_ammonia'])
            
            if idx > 0:
                prev_predicted = forecast_data.iloc[idx-1]['predicted_ammonia']
                consumption = prev_predicted - predicted
                consumption_str = f"消費{consumption:.1f}m^3" if consumption > 0 else f"増加{abs(consumption):.1f}m^3"
            else:
                consumption_str = "初期値"
            
            period_type = "[予測期間]" if is_forecast else "[実績期間]"
            print(f"{date_str}{period_type}: 発電{power_mwh:6.1f}MWh → アンモニア{predicted:6.1f}m^3 ({consumption_str})")
        
        return result_df

if __name__ == '__main__':
    print("=== 高精度アンモニア在庫予測システム - 予測モジュール ===")
    
    prediction_system = AmmoniaPredictionSystem()
    
    # 学習済みモデル読み込み
    if prediction_system.load_model('models/ammonia_prediction_model.pkl'):
        print("=== アンモニア在庫予測開始 ===")
        
        # 相対パスをプロジェクトルートから解決
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        data_path = os.path.join(project_root, 'data', 'training_data.csv')
        output_path = os.path.join(project_root, 'data', 'predictions.csv')

        # CLI 引数 (閾値・補給量) を受け取り適用
        import argparse
        parser = argparse.ArgumentParser(description='アンモニア在庫予測')
        parser.add_argument('--refill_threshold', type=float, default=prediction_system.refill_threshold,
                            help='自動補給判定閾値 (m3)')
        parser.add_argument('--refill_amount', type=float, default=prediction_system.refill_amount,
                            help='自動補給で加算する量 (m3)')
        parser.add_argument('--refill_target_post_level', type=float, default=None,
                            help='補給後に最低限到達させたい水準 (m3)。指定すると補給量が調整される')
        parser.add_argument('--data_path', type=str, default=data_path, help='入力データパス')
        parser.add_argument('--output_path', type=str, default=output_path, help='出力CSVパス')
        args = parser.parse_args()

        prediction_system.refill_threshold = args.refill_threshold
        prediction_system.refill_amount = args.refill_amount
        prediction_system.refill_target_post_level = args.refill_target_post_level

        # 予測実行
        result_df = prediction_system.predict(
            data_path=args.data_path,
            output_path=args.output_path
        )

        print("\n[完了] 予測完了！")
        print("- 発電量に基づくアンモニア消費を正確に反映")
        print("- 空白のactual_ammoniaは予測対象として処理")
        print("- 補給タイミング自動検出機能付き")
        print("- 高精度物理ベース予測アルゴリズム適用")
    else:
        print("モデル読み込みに失敗しました")