# -*- coding: utf-8 -*-
"""
電力需要予測AIモデル - PyCaret翌日予測モジュール

学習済みPyCaretモデルを使用して明日の電力需要を予測し、
結果をCSVファイルとグラフで出力するモジュール。
"""

import datetime
import glob
import os
import traceback
import time
import gc
import psutil
from dataclasses import dataclass
from functools import wraps
from typing import Optional, Tuple, Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pycaret.regression import load_model, predict_model
from sklearn.metrics import mean_squared_error, r2_score

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
class PycaretTomorrowConfig:
    """Pycaret翌日予測設定クラス"""
    # 入力データ関連
    XTRAIN_CSV: str = r"data/Xtrain.csv"
    XTEST_CSV: str = r"data/Xtest.csv"
    YTRAIN_CSV: str = r"data/Ytrain.csv"
    YTEST_CSV: str = r"tomorrow/Ytest.csv"
    XTOMORROW_CSV: str = r"tomorrow/tomorrow.csv"
    
    # モデル関連
    MODEL_SAV: str = r'train/Pycaret/Pycaret_model'
    
    # 出力関連
    YPRED_CSV: str = r'tomorrow/Pycaret/Pycaret_Ypred.csv'
    YPRED_PNG: str = r'tomorrow/Pycaret/Pycaret_Ypred.png'
    YPRED_7D_PNG: str = r'tomorrow/Pycaret/Pycaret_Ypred_7d.png'
    YTOMORROW_CSV: str = r'tomorrow/Pycaret/Pycaret_tomorrow.csv'
    YTOMORROW_PNG: str = r'tomorrow/Pycaret/Pycaret_tomorrow.png'
    
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


@robust_model_operation("テスト・翌日データ読み込み")
def load_test_and_tomorrow_data(config: PycaretTomorrowConfig) -> Tuple[np.ndarray, np.ndarray]:
    """テストデータと翌日データを読み込み"""
    if not os.path.exists(config.YTEST_CSV):
        raise FileNotFoundError(f"テストデータファイルが見つかりません: {config.YTEST_CSV}")
    if not os.path.exists(config.XTOMORROW_CSV):
        raise FileNotFoundError(f"予測用データファイルが見つかりません: {config.XTOMORROW_CSV}")
    
    y_test = pd.read_csv(config.YTEST_CSV).values.astype('int32').flatten()
    x_tomorrow = pd.read_csv(config.XTOMORROW_CSV).to_numpy().astype('float32')
    
    print(f"データ読み込み完了 - y_test: {y_test.shape}, x_tomorrow: {x_tomorrow.shape}")
    return y_test, x_tomorrow

@robust_model_operation("Pycaretモデル読み込み")
def load_pycaret_model(config: PycaretTomorrowConfig):
    """Pycaretモデルを読み込み"""
    if not os.path.exists(f"{config.MODEL_SAV}.pkl"):
        raise FileNotFoundError(f"Pycaretモデルファイルが見つかりません: {config.MODEL_SAV}.pkl")
    
    model = load_model(model_name=config.MODEL_SAV)
    print(f"Pycaretモデル読み込み完了: {config.MODEL_SAV}")
    return model

@robust_model_operation("Pycaret予測実行")
def predict_with_pycaret_model(config: PycaretTomorrowConfig, model, x_tomorrow: np.ndarray) -> np.ndarray:
    """Pycaretモデルを使用して予測を実行"""
    if x_tomorrow.shape[1] != len(config.X_COLS):
        raise ValueError(f"入力データの特徴量数が不正です。期待値: {len(config.X_COLS)}, 実際値: {x_tomorrow.shape[1]}")
    
    # DataFrameに変換してPycaretに渡す
    x_df = pd.DataFrame(x_tomorrow, columns=list(config.X_COLS))
    
    # 予測実行
    prediction_result = predict_model(model, data=x_df)
    
    # 'prediction_label'列から予測値を取得
    if 'prediction_label' not in prediction_result.columns:
        raise ValueError("予測結果に'prediction_label'列が見つかりません")
    
    y_tomorrow = prediction_result['prediction_label'].values.flatten()
    
    print(f"予測完了 - 予測結果形状: {y_tomorrow.shape}")
    return y_tomorrow

@robust_model_operation("予測結果保存")
def save_prediction_results(config: PycaretTomorrowConfig, y_tomorrow: np.ndarray) -> None:
    """予測結果をCSVファイルに保存"""
    os.makedirs(os.path.dirname(config.YTOMORROW_CSV), exist_ok=True)
    
    y_tomorrow_df = pd.DataFrame(y_tomorrow, columns=list(config.Y_COLS))
    y_tomorrow_df.to_csv(config.YTOMORROW_CSV, index=False)
    
    print(f"予測結果保存完了: {config.YTOMORROW_CSV} ({len(y_tomorrow_df)}行)")

@robust_model_operation("精度指標計算")
def calculate_metrics(y_test: np.ndarray, y_tomorrow: np.ndarray) -> Tuple[float, float]:
    """予測精度指標を計算"""
    min_length = min(len(y_test), len(y_tomorrow))
    if min_length == 0:
        raise ValueError("比較するデータがありません")
    
    y_test_trimmed = y_test[:min_length]
    y_tomorrow_trimmed = y_tomorrow[:min_length]
    
    # RMSE計算
    rmse = mean_squared_error(y_test_trimmed, y_tomorrow_trimmed, squared=False)
    
    # R²スコア計算
    r2_score_value = r2_score(y_test_trimmed, y_tomorrow_trimmed)
    # MAEも計算してダッシュボードが拾えるようにする
    try:
        from sklearn.metrics import mean_absolute_error
        mae = mean_absolute_error(y_test_trimmed, y_tomorrow_trimmed)
        print(f"MAE: {mae:.3f}")
    except Exception:
        try:
            import numpy as _np
            mae = float(_np.mean(_np.abs(y_test_trimmed - y_tomorrow_trimmed)))
            print(f"MAE: {mae:.3f}")
        except Exception:
            pass

    print(f"RMSE: {rmse:.2f} kW, R2スコア: {r2_score_value:.3f}")
    return rmse, r2_score_value

@robust_model_operation("グラフ生成")
def create_prediction_visualization(config: PycaretTomorrowConfig, y_test: np.ndarray, y_tomorrow: np.ndarray) -> None:
    """予測結果の可視化グラフを作成"""
    os.makedirs(os.path.dirname(config.YTOMORROW_PNG), exist_ok=True)
    
    min_length = min(len(y_test), len(y_tomorrow))
    
    # データフレームに変換
    df_result1 = pd.DataFrame({"Predict[kW]": y_tomorrow.ravel()})
    df_result2 = pd.DataFrame({"Actual[kW]": y_test.ravel()})
    
    # 日時インデックス設定
    # JST (UTC+9) を明示して日付インデックスを作成
    jst_now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    past_days_ago = (jst_now - datetime.timedelta(days=config.PAST_DAYS)).date()
    
    # 他モデルと同一ロジックに揃える（freq='h' を使用）
    df_result1.index = pd.date_range(start=past_days_ago, periods=len(df_result1), freq='h')
    df_result2.index = pd.date_range(start=past_days_ago, periods=len(df_result2), freq='h')
    # インデックス名を明示（年月日表示）
    df_result1.index.name = 'Date'
    df_result2.index.name = 'Date'
    
    # グラフ描画
    plt.figure(figsize=(16, 9))
    plt.plot(df_result1.index, df_result1['Predict[kW]'], label='Predict[kW]')
    plt.plot(df_result2.index[:min_length], df_result2['Actual[kW]'][:min_length], label='Actual[kW]')
    
    # タイトル設定
    model_name = os.path.splitext(os.path.basename(config.MODEL_SAV))[0]
    plt.title(model_name, fontsize=12)
    # x軸は年月日で表示
    plt.xlabel('Date', fontsize=12)
    # 他モデルと同様の挙動に合わせ、DateFormatterは使用せず標準のxticksを用いる
    plt.ylabel('Power [kW]', fontsize=12)
    plt.legend(fontsize=11)
    plt.xticks(fontsize=10)
    # 明示的に回転をゼロにして、どの環境でも縦回転が入らないようにする
    try:
        ax = plt.gca()
        ax.tick_params(axis='x', labelrotation=0)
    except Exception:
        pass
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
    config = PycaretTomorrowConfig(
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

@robust_model_operation("Pycaret翌日予測メイン処理")
def execute_tomorrow_prediction(config: PycaretTomorrowConfig) -> Optional[Tuple[float, float]]:
    """統一されたPycaret翌日予測処理"""
    # 1. データ読み込み
    y_test, x_tomorrow = load_test_and_tomorrow_data(config)
    if y_test is None or x_tomorrow is None:
        return None, None
    
    # 2. モデル読み込み
    model = load_pycaret_model(config)
    if model is None:
        return None, None
    
    # 3. 予測実行
    y_tomorrow = predict_with_pycaret_model(config, model, x_tomorrow)
    if y_tomorrow is None:
        return None, None
    
    # 4. 予測結果保存
    save_prediction_results(config, y_tomorrow)
    
    # 5. 精度指標計算
    rmse, r2_score_value = calculate_metrics(y_test, y_tomorrow)
    if rmse is None or r2_score_value is None:
        return None, None
    
    # 6. 可視化作成
    create_prediction_visualization(config, y_test, y_tomorrow)
    
    return rmse, r2_score_value


if __name__ == "__main__":
    # 設定初期化
    config = PycaretTomorrowConfig()
    
    # 起動時に監査ログとして AI_TARGET_YEARS を出力
    import os as _os
    print(f"AI_TARGET_YEARS={_os.environ.get('AI_TARGET_YEARS')}")

    print("=" * 60)
    print("Pycaret翌日電力需要予測 開始")
    print("=" * 60)
    
    start_time = time.time()
    
    # 翌日予測実行
    result = execute_tomorrow_prediction(config)
    
    total_time = time.time() - start_time
    
    print("=" * 60)
    print("Pycaret翌日電力需要予測 完了")
    if result is not None and result != (None, None):
        rmse, r2_score_value = result
        print(f"最終結果 - RMSE: {rmse:.2f} kW, R2スコア: {r2_score_value:.3f}")
    else:
        print("予測処理が失敗しました")
    print(f"総実行時間: {total_time:.3f}秒")
    print("=" * 60)