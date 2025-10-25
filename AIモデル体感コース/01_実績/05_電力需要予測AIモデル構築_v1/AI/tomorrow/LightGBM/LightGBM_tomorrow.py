# -*- coding: utf-8 -*-
"""
電力需要予測AIモデル - LightGBM明日予測モジュール

学習済みLightGBMモデルを使用して明日の電力需要を予測し、
結果をCSVファイルとグラフで出力するモジュール。
"""

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import pickle
from sklearn.metrics import mean_squared_error
import traceback
import os
import datetime
import time
import gc
import psutil
from dataclasses import dataclass
from functools import wraps
from typing import Tuple, Optional, Dict, Any

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
class LightGBMTomorrowConfig:
    """LightGBM翌日予測設定クラス"""
    # 入力データ関連
    XTRAIN_CSV: str = r"data/Xtrain.csv"
    XTEST_CSV: str = r"data/Xtest.csv"
    YTRAIN_CSV: str = r"data/Ytrain.csv"
    YTEST_CSV: str = r"tomorrow/Ytest.csv"
    XTOMORROW_CSV: str = r"tomorrow/tomorrow.csv"
    
    # モデル関連
    MODEL_SAV: str = r'train/LightGBM/LightGBM_model.sav'
    
    # 出力関連
    YPRED_CSV: str = r'tomorrow/LightGBM/LightGBM_Ypred.csv'
    YPRED_PNG: str = r'tomorrow/LightGBM/LightGBM_Ypred.png'
    YPRED_7D_PNG: str = r'tomorrow/LightGBM/LightGBM_Ypred_7d.png'
    YTOMORROW_CSV: str = r'tomorrow/LightGBM/LightGBM_tomorrow.csv'
    YTOMORROW_PNG: str = r'tomorrow/LightGBM/LightGBM_tomorrow.png'
    
    # 設定パラメータ
    PAST_DAYS: str = '7'
    LEARNING_RATE: str = ''
    EPOCHS: str = ''
    VALIDATION_SPLIT: str = ''
    HISTORY_PNG: str = ''
    
    # データ列
    X_COLS: tuple = ("MONTH","WEEK","HOUR","TEMP")
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

@robust_model_operation("学習データ読み込み")
def load_training_data(config: LightGBMTomorrowConfig) -> Tuple[pd.DataFrame, StandardScaler]:
    """学習データを読み込み、標準化スケーラーを作成"""
    X_train = pd.read_csv(config.XTRAIN_CSV)
    
    # 標準化スケーラーを作成・学習
    scaler = StandardScaler()
    scaler.fit(X_train)
    X_train_scaled = pd.DataFrame(scaler.transform(X_train), columns=X_train.columns)
    
    print(f"学習データ形状: {X_train_scaled.shape}")
    return X_train_scaled, scaler

@robust_model_operation("テスト・翌日データ読み込み")
def load_test_and_tomorrow_data(config: LightGBMTomorrowConfig, scaler: StandardScaler) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """テストデータと翌日データを読み込み、標準化"""
    y_test = pd.read_csv(config.YTEST_CSV).values.astype('int32').flatten()
    Xtomorrow = pd.read_csv(config.XTOMORROW_CSV)
    
    # 翌日データを標準化
    Xtomorrow_scaled = pd.DataFrame(scaler.transform(Xtomorrow), columns=Xtomorrow.columns)
    
    print(f"テストデータ形状: {y_test.shape}")
    print(f"翌日データ形状: {Xtomorrow_scaled.shape}")
    return y_test, Xtomorrow_scaled

@robust_model_operation("モデル読み込み")
def load_model(config: LightGBMTomorrowConfig):
    """保存済みモデルを読み込み"""
    with open(config.MODEL_SAV, 'rb') as f:
        model = pickle.load(f)
    print(f"モデル読み込み完了: {config.MODEL_SAV}")
    return model

@robust_model_operation("予測実行")
def predict_with_model(model, Xtomorrow_scaled: pd.DataFrame, y_test: pd.DataFrame) -> Tuple[pd.DataFrame, float, float, float]:
    """モデルを使用して予測を実行し、精度指標を計算"""
    # 予測実行
    Ytomorrow = model.predict(Xtomorrow_scaled)
    
    # データ長を合わせる
    min_length = min(len(Xtomorrow_scaled), len(y_test))
    
    # 精度計算
    try:
        accuracy = model.score(Xtomorrow_scaled[:min_length], y_test[:min_length])
        print(f'テスト精度: {accuracy:.4f}')
    except Exception as e:
        print(f'精度計算でエラーが発生: {e}')
        accuracy = 0.0
    
    # RMSE・スコア計算
    mse = mean_squared_error(y_test[:min_length], Ytomorrow[:min_length])
    REG_RMSE = mse ** 0.5
    REG_SCORE = 1.0 - mse ** 0.5 / y_test[:min_length].mean()
    
    print(f"REG RMSE : {REG_RMSE:.2f} kW")
    print(f"REG SCORE: {REG_SCORE:.2f}")
    
    return Ytomorrow, REG_RMSE, REG_SCORE, accuracy

@robust_model_operation("翌日予測結果保存")
def save_tomorrow_predictions(config: LightGBMTomorrowConfig, Ytomorrow: pd.DataFrame) -> None:
    """翌日予測結果をCSVファイルに保存"""
    y_tomorrow_csv = pd.DataFrame(Ytomorrow, columns=list(config.Y_COLS))
    y_tomorrow_csv.to_csv(config.YTOMORROW_CSV, index=False)
    print(f"予測結果保存完了: {config.YTOMORROW_CSV} ({len(y_tomorrow_csv)}行)")

@robust_model_operation("グラフ生成")
def generate_prediction_graph(config: LightGBMTomorrowConfig, Ytomorrow: pd.DataFrame, y_test: pd.DataFrame) -> None:
    """予測結果のグラフを生成"""
    # データフレーム作成
    df_result1 = pd.DataFrame({"Predict[kW]": Ytomorrow.ravel()})
    df_result2 = pd.DataFrame({"Actual[kW]": y_test.ravel()})
    
    # 日時インデックス作成
    now = datetime.datetime.now()
    past_days_int = int(config.PAST_DAYS)
    past_days_ago = now - datetime.timedelta(days=past_days_int)
    past_days_ago = past_days_ago.date()
    
    df_result1.index = pd.date_range(start=past_days_ago, periods=len(df_result1), freq='h')
    df_result2.index = pd.date_range(start=past_days_ago, periods=len(df_result2), freq='h')
    
    # グラフ描画
    plt.figure(figsize=(16, 9))
    plt.plot(df_result1, label='Predict[kW]')
    plt.plot(df_result2, label='Actual[kW]')
    
    filename = os.path.splitext(os.path.basename(config.MODEL_SAV))[0]
    plt.title(filename, fontsize=12)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Power [kW]', fontsize=12)
    plt.legend(fontsize=11)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.tight_layout()
    plt.savefig(config.YTOMORROW_PNG)
    plt.close()
    
    print(f"グラフ保存完了: {config.YTOMORROW_PNG}")

def tomorrow(Xtrain_csv, Xtest_csv, Ytrain_csv, Ytest_csv, model_sav, Ypred_csv, Ypred_png, Ypred_7d_png, learning_rate, epochs, validation_split, history_png, Xtomorrow_csv, Ytomorrow_csv, Ytomorrow_png, past_days):
    """レガシー関数：下位互換性のため保持"""
    config = LightGBMTomorrowConfig(
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

@robust_model_operation("LightGBM翌日予測メイン処理")
def execute_tomorrow_prediction(config: LightGBMTomorrowConfig) -> Tuple[float, float]:
    """統一されたLightGBM翌日予測処理"""
    # 1. 学習データ読み込み・標準化スケーラー作成
    X_train_scaled, scaler = load_training_data(config)
    if X_train_scaled is None or scaler is None:
        return None, None
    
    # 2. テスト・翌日データ読み込み・標準化
    y_test, Xtomorrow_scaled = load_test_and_tomorrow_data(config, scaler)
    if y_test is None or Xtomorrow_scaled is None:
        return None, None
    
    # 3. モデル読み込み
    model = load_model(config)
    if model is None:
        return None, None
    
    # 4. 予測実行・精度計算
    Ytomorrow, REG_RMSE, REG_SCORE, accuracy = predict_with_model(model, Xtomorrow_scaled, y_test)
    if Ytomorrow is None:
        return None, None
    
    # 5. 翌日予測結果保存
    save_tomorrow_predictions(config, Ytomorrow)
    
    # 6. グラフ生成
    generate_prediction_graph(config, Ytomorrow, y_test)
    
    return REG_RMSE, REG_SCORE

if __name__ == "__main__":
    # 設定初期化
    config = LightGBMTomorrowConfig()
    
    print("=" * 60)
    print("LightGBM翌日電力需要予測 開始")
    print("=" * 60)
    
    start_time = time.time()
    
    # 翌日予測実行
    rmse, score = execute_tomorrow_prediction(config)
    
    total_time = time.time() - start_time
    
    print("=" * 60)
    print("LightGBM翌日電力需要予測 完了")
    if rmse is not None and score is not None:
        print(f"最終結果 - RMSE: {rmse:.2f} kW, スコア: {score:.2f}")
    print(f"総実行時間: {total_time:.3f}秒")
    print("=" * 60)
