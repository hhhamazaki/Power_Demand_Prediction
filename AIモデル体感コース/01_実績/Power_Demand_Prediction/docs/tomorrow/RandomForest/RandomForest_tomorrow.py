# -*- coding: utf-8 -*-
"""
電力需要予測AIモデル - RandomForest翌日予測モジュール

学習済みRandomForestモデルを使用して明日の電力需要を予測し、
結果をCSVファイルとグラフで出力するモジュール。
"""

import datetime
import glob
import os
import pickle
import traceback
import time
import gc
import psutil
from dataclasses import dataclass
from functools import wraps
from typing import Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

# matplotlib日本語フォント設定
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 100
plt.rcParams['savefig.bbox'] = 'tight'
plt.rcParams['savefig.pad_inches'] = 0.1
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['lines.linewidth'] = 1.5
plt.rcParams['axes.linewidth'] = 0.8

@dataclass
class RandomForestTomorrowConfig:
    """RandomForest翌日予測設定クラス"""
    # 入力データ関連
    XTRAIN_CSV: str = r"data/Xtrain.csv"
    XTEST_CSV: str = r"data/Xtest.csv"
    YTRAIN_CSV: str = r"data/Ytrain.csv"
    YTEST_CSV: str = r"tomorrow/Ytest.csv"
    XTOMORROW_CSV: str = r"tomorrow/tomorrow.csv"
    
    # モデル関連
    MODEL_SAV: str = r'train/RandomForest/RandomForest_model.sav'
    
    # 出力関連
    YPRED_CSV: str = r'tomorrow/RandomForest/RandomForest_Ypred.csv'
    YPRED_PNG: str = r'tomorrow/RandomForest/RandomForest_Ypred.png'
    YPRED_7D_PNG: str = r'tomorrow/RandomForest/RandomForest_Ypred_7d.png'
    YTOMORROW_CSV: str = r'tomorrow/RandomForest/RandomForest_tomorrow.csv'
    YTOMORROW_PNG: str = r'tomorrow/RandomForest/RandomForest_tomorrow.png'
    
    # 設定パラメータ
    PAST_DAYS: int = 7
    LEARNING_RATE: float = 0.0
    EPOCHS: int = 0
    VALIDATION_SPLIT: float = 0.0
    HISTORY_PNG: str = ""
    
    # データ列
    X_COLS: tuple = ("MONTH", "WEEK", "HOUR", "TEMP")
    Y_COLS: tuple = ("KW",)

def robust_model_operation(operation_name: str):
    """モデル操作の堅牢性を保証するデコレータ"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            try:
                print(f"実行開始: {operation_name}")
                result = func(*args, **kwargs)
                
                # メモリ使用量とガベージコレクション
                collected = gc.collect()
                final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                execution_time = time.time() - start_time
                
                print(f"実行完了: {operation_name}")
                print(f"実行時間: {execution_time:.3f}秒")
                print(f"メモリ使用量: {initial_memory:.1f}MB → {final_memory:.1f}MB (差分: {final_memory-initial_memory:+.1f}MB)")
                print(f"ガベージコレクション: {collected}個のオブジェクトを回収")
                
                return result
                
            except Exception as e:
                print(f"エラー発生 in {operation_name}: {e}")
                print(f"トレースバック:\n{traceback.format_exc()}")
                return None
                
        return wrapper
    return decorator


@robust_model_operation("学習・テスト・翌日データ読み込み")
def load_training_and_test_data(config: RandomForestTomorrowConfig) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """学習データ、テストデータ、翌日データを読み込み"""
    if not os.path.exists(config.XTRAIN_CSV):
        raise FileNotFoundError(f"学習用データファイルが見つかりません: {config.XTRAIN_CSV}")
    if not os.path.exists(config.YTEST_CSV):
        raise FileNotFoundError(f"テストデータファイルが見つかりません: {config.YTEST_CSV}")
    if not os.path.exists(config.XTOMORROW_CSV):
        raise FileNotFoundError(f"予測用データファイルが見つかりません: {config.XTOMORROW_CSV}")
    
    x_train = pd.read_csv(config.XTRAIN_CSV).to_numpy().astype('float32')
    y_test = pd.read_csv(config.YTEST_CSV).values.astype('int32').flatten()
    x_tomorrow = pd.read_csv(config.XTOMORROW_CSV).to_numpy().astype('float32')
    
    print(f"データ読み込み完了 - x_train: {x_train.shape}, y_test: {y_test.shape}, x_tomorrow: {x_tomorrow.shape}")
    return x_train, y_test, x_tomorrow

@robust_model_operation("データ標準化")
def standardize_data(x_train: np.ndarray, x_tomorrow: np.ndarray) -> Tuple[np.ndarray, np.ndarray, StandardScaler]:
    """データの標準化を実行"""
    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_tomorrow_scaled = scaler.transform(x_tomorrow)
    
    print(f"データ標準化完了 - 学習データ: {x_train_scaled.shape}, 翌日データ: {x_tomorrow_scaled.shape}")
    return x_train_scaled, x_tomorrow_scaled, scaler

@robust_model_operation("RandomForestモデル読み込み")
def load_random_forest_model(config: RandomForestTomorrowConfig):
    """RandomForestモデルを読み込み"""
    if not os.path.exists(config.MODEL_SAV):
        raise FileNotFoundError(f"RandomForestモデルファイルが見つかりません: {config.MODEL_SAV}")
    
    with open(config.MODEL_SAV, 'rb') as f:
        model = pickle.load(f)
    
    print(f"RandomForestモデル読み込み完了: {config.MODEL_SAV}")
    return model

@robust_model_operation("RandomForest予測実行")
def predict_with_model(model, x_tomorrow: np.ndarray, y_test: np.ndarray) -> np.ndarray:
    """RandomForestモデルを使用して予測を実行"""
    min_length = min(len(x_tomorrow), len(y_test))
    
    # テスト精度を確認（参考値）
    if min_length > 0:
        test_accuracy = model.score(x_tomorrow[:min_length], y_test[:min_length])
        print(f"テスト精度（R²スコア参考値）: {test_accuracy:.3f}")
    
    # 予測実行
    y_tomorrow = model.predict(x_tomorrow)
    
    print(f"予測完了 - 予測結果形状: {y_tomorrow.shape}")
    return y_tomorrow

@robust_model_operation("予測結果保存")
def save_prediction_results(config: RandomForestTomorrowConfig, y_tomorrow: np.ndarray) -> None:
    """予測結果をCSVファイルに保存"""
    os.makedirs(os.path.dirname(config.YTOMORROW_CSV), exist_ok=True)
    
    y_tomorrow_df = pd.DataFrame(y_tomorrow, columns=list(config.Y_COLS))
    y_tomorrow_df.to_csv(config.YTOMORROW_CSV, index=False)
    
    print(f"予測結果保存完了: {config.YTOMORROW_CSV} ({len(y_tomorrow_df)}行)")

@robust_model_operation("精度指標計算")
def calculate_metrics(y_test: np.ndarray, y_tomorrow: np.ndarray) -> Tuple[float, float]:
    """予測精度指標を計算（統一フォーマット対応）"""
    min_length = min(len(y_test), len(y_tomorrow))
    if min_length == 0:
        raise ValueError("比較するデータがありません")
    
    y_test_trimmed = y_test[:min_length]
    y_tomorrow_trimmed = y_tomorrow[:min_length]
    
    # RMSE計算
    rmse = mean_squared_error(y_test_trimmed, y_tomorrow_trimmed, squared=False)
    
    # R²スコア計算
    r2_score_value = r2_score(y_test_trimmed, y_tomorrow_trimmed)
    
    # MAE計算（ダッシュボード抽出用統一フォーマット）
    try:
        from sklearn.metrics import mean_absolute_error
        mae = mean_absolute_error(y_test_trimmed, y_tomorrow_trimmed)
    except Exception:
        import numpy as _np
        mae = float(_np.mean(_np.abs(y_test_trimmed - y_tomorrow_trimmed)))
    
    # 統一フォーマットで出力（ダッシュボード extractMetric が確実に抽出できる）
    print(f"最終結果 - RMSE: {rmse:.3f} kW, R2スコア: {r2_score_value:.4f}, MAE: {mae:.3f} kW")
    
    return rmse, r2_score_value

@robust_model_operation("グラフ生成")
def create_prediction_visualization(config: RandomForestTomorrowConfig, y_test: np.ndarray, y_tomorrow: np.ndarray) -> None:
    """予測結果の可視化グラフを作成"""
    os.makedirs(os.path.dirname(config.YTOMORROW_PNG), exist_ok=True)
    
    min_length = min(len(y_test), len(y_tomorrow))
    
    # データフレームに変換
    df_result1 = pd.DataFrame({"Predict[kW]": y_tomorrow.ravel()})
    df_result2 = pd.DataFrame({"Actual[kW]": y_test.ravel()})
    
    # 日時インデックス設定
    # JSTを明示してインデックスを作成（UTC->JST）
    jst_now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    past_days_ago = (jst_now - datetime.timedelta(days=config.PAST_DAYS)).date()
    
    df_result1.index = pd.date_range(start=past_days_ago, periods=len(df_result1), freq='h')
    df_result2.index = pd.date_range(start=past_days_ago, periods=len(df_result2), freq='h')
    # インデックス名を明示（年月日表示、回転は行わない）
    df_result1.index.name = 'Date'
    df_result2.index.name = 'Date'
    
    # グラフ描画
    plt.figure(figsize=(16, 9))
    plt.plot(df_result1.index, df_result1['Predict[kW]'], label='Predict[kW]')
    plt.plot(df_result2.index[:min_length], df_result2['Actual[kW]'][:min_length], label='Actual[kW]')
    
    # タイトル設定
    model_name = os.path.splitext(os.path.basename(config.MODEL_SAV))[0]
    plt.title(model_name, fontsize=12)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Power [kW]', fontsize=12)
    plt.legend(fontsize=11)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.tight_layout()
    
    plt.savefig(config.YTOMORROW_PNG)
    plt.close()
    
    print(f"グラフ保存完了: {config.YTOMORROW_PNG}")

def tomorrow(
    Xtrain_csv: str,
    Xtest_csv: str,
    Ytrain_csv: str,
    Ytest_csv: str,
    model_sav: str,
    Ypred_csv: str,
    Ypred_png: str,
    Ypred_7d_png: str,
    learning_rate: float,
    epochs: int,
    validation_split: float,
    history_png: str,
    Xtomorrow_csv: str,
    Ytomorrow_csv: str,
    Ytomorrow_png: str,
    past_days: int
) -> Optional[Tuple[float, float]]:
    """レガシー関数：下位互換性のため保持"""
    config = RandomForestTomorrowConfig(
        XTRAIN_CSV=Xtrain_csv,
        XTEST_CSV=Xtest_csv,
        YTRAIN_CSV=Ytrain_csv,
        YTEST_CSV=Ytest_csv,
        MODEL_SAV=model_sav,
        YPRED_CSV=Ypred_csv,
        YPRED_PNG=Ypred_png,
        YPRED_7D_PNG=Ypred_7d_png,
        XTOMORROW_CSV=Xtomorrow_csv,
        YTOMORROW_CSV=Ytomorrow_csv,
        YTOMORROW_PNG=Ytomorrow_png,
        PAST_DAYS=past_days,
        LEARNING_RATE=learning_rate,
        EPOCHS=epochs,
        VALIDATION_SPLIT=validation_split,
        HISTORY_PNG=history_png
    )
    return execute_tomorrow_prediction(config)

@robust_model_operation("RandomForest翌日予測メイン処理")
def execute_tomorrow_prediction(config: RandomForestTomorrowConfig) -> Optional[Tuple[float, float]]:
    """統一されたRandomForest翌日予測処理"""
    # 1. データ読み込み
    x_train, y_test, x_tomorrow = load_training_and_test_data(config)
    if x_train is None or y_test is None or x_tomorrow is None:
        return None, None
    
    # 2. データ標準化
    x_train_scaled, x_tomorrow_scaled, scaler = standardize_data(x_train, x_tomorrow)
    if x_train_scaled is None or x_tomorrow_scaled is None:
        return None, None
    
    # 3. モデル読み込み
    model = load_random_forest_model(config)
    if model is None:
        return None, None
    
    # 4. 予測実行
    y_tomorrow = predict_with_model(model, x_tomorrow_scaled, y_test)
    if y_tomorrow is None:
        return None, None
    
    # 5. 予測結果保存
    save_prediction_results(config, y_tomorrow)
    
    # 6. 精度指標計算
    rmse, r2_score_value = calculate_metrics(y_test, y_tomorrow)
    if rmse is None or r2_score_value is None:
        return None, None
    
    # 7. 可視化作成
    create_prediction_visualization(config, y_test, y_tomorrow)
    
    return rmse, r2_score_value


if __name__ == "__main__":
    # 設定初期化
    config = RandomForestTomorrowConfig()
    # 起動時に監査ログとして AI_TARGET_YEARS を出力
    import os as _os
    print(f"AI_TARGET_YEARS={_os.environ.get('AI_TARGET_YEARS')}")

    print("=" * 60)
    print("RandomForest翌日電力需要予測 開始")
    print("=" * 60)
    
    start_time = time.time()
    
    # 翌日予測実行
    result = execute_tomorrow_prediction(config)
    
    total_time = time.time() - start_time
    
    print("=" * 60)
    print("RandomForest翌日電力需要予測 完了")
    if result is not None and result != (None, None):
        rmse, r2_score_value = result
        # 統一フォーマット出力は既に calculate_metrics 内で行われているため、ここでは簡略表示
        print(f"(簡略表示) RMSE: {rmse:.2f} kW, R2スコア: {r2_score_value:.3f}")
    else:
        print("予測処理が失敗しました")
    print(f"総実行時間: {total_time:.3f}秒")
    print("=" * 60)