# -*- coding: utf-8 -*-
"""
電力需要予測AIモデル - Keras学習モジュール

深層ニューラルネットワークを構築し電力需要で学習を行い、
電力消費予測のための予測モデルを作成するモジュール。
"""

# 標準ライブラリインポート
import os
import sys
import time
import traceback
import warnings
import gc
from typing import List, Tuple, Optional, Dict, Any, Union
from dataclasses import dataclass, field

# サードパーティライブラリインポート
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle

# 機械学習ライブラリインポート
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

# Keras/TensorFlowインポート
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import Adam
from keras import regularizers
from tensorflow.python.keras.callbacks import EarlyStopping

# 再現性確保のためのランダムシード固定
import random
import tensorflow as tf
random.seed(42)
np.random.seed(42) 
tf.random.set_seed(42)

# パフォーマンス最適化設定（統合版）
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # TensorFlow警告抑制
np.set_printoptions(suppress=True, precision=4)

# pandas高速化設定（バージョン互換性対応）
try:
    pd.set_option('mode.copy_on_write', True)
except Exception:
    pass  # 古いバージョンでは無視

# matplotlib最適化設定（16:9統一、可視化）
plt.rcParams['figure.figsize'] = (16, 9)  # 16:9アスペクト比統一
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 100
plt.rcParams['savefig.bbox'] = 'tight'
plt.rcParams['savefig.pad_inches'] = 0.1
try:
    from matplotlib import font_manager
    preferred_fonts = ['Meiryo', 'Yu Gothic', 'Noto Sans CJK JP', 'IPAexGothic', 'DejaVu Sans']
    available = {f.name for f in font_manager.fontManager.ttflist}
    chosen = None
    for fname in preferred_fonts:
        if fname in available:
            chosen = fname
            break
    if chosen:
        plt.rcParams['font.family'] = [chosen, 'DejaVu Sans']
    else:
        plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.unicode_minus'] = False
except Exception:
    plt.rcParams['font.family'] = 'DejaVu Sans'

plt.rcParams['font.size'] = 12  # タイトル用
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 11
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['lines.linewidth'] = 1.5
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['figure.max_open_warning'] = 10

print("Keras: 統一パフォーマンス最適化設定を適用しました")

# 統一設定クラス（統合版）
@dataclass(frozen=True)
class KerasConfig:
    """Keras学習設定クラス（設定値統一管理）"""
    DEFAULT_FEATURE_COLUMNS: List[str] = field(default_factory=lambda: ["MONTH", "WEEK", "HOUR", "TEMP"])
    DEFAULT_TARGET_COLUMNS: List[str] = field(default_factory=lambda: ["KW"])
    DEFAULT_LEARNING_RATE: float = 0.001
    DEFAULT_EPOCHS: int = 500
    DEFAULT_BATCH_SIZE: int = 64  # バッチサイズを64に最適化（32→64）
    DEFAULT_VALIDATION_SPLIT: float = 0.2
    DEFAULT_PATIENCE: int = 20  # 早期終了の忍耐度を適切に設定
    NEURAL_NETWORK_UNITS: int = 128  # ユニット数を128に増加
    RANDOM_STATE: int = 42
    
    # 正則化設定（軽微な正則化で過学習防止）
    DROPOUT_RATE: float = 0.1  # 軽微なドロップアウト
    L2_REGULARIZATION: float = 0.001  # 軽微なL2正則化
    
    # メモリ最適化設定
    DTYPE_CONFIG: Dict[str, str] = field(default_factory=lambda: {
        'float_dtype': 'float32',
        'int_dtype': 'int32'
    })

# 統一設定インスタンス
config = KerasConfig()

def robust_model_operation(operation: str):
    """
    モデル操作エラーハンドリングデコレータ（統一パターン）
    
    Args:
        operation: 操作名（ログ出力用）
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                print(f"=== {operation}開始 ===")
                result = func(*args, **kwargs)
                print(f"=== {operation}完了 ===")
                return result
            except FileNotFoundError as e:
                error_msg = f"{operation}失敗 - ファイルが見つかりません: {e}"
                print(error_msg)
                raise FileNotFoundError(error_msg)
            except ValueError as e:
                error_msg = f"{operation}失敗 - データ形式エラー: {e}"
                print(error_msg)
                raise ValueError(error_msg)
            except Exception as e:
                error_msg = f"{operation}失敗 - 予期しないエラー: {e}"
                print(error_msg)
                traceback.print_exc()
                raise
        return wrapper
    return decorator

def ensure_directory_exists(file_path: str) -> None:
    """
    ファイルパスのディレクトリが存在しない場合は作成する（統一パターン）
    
    Args:
        file_path: ファイルパス
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        print(f"ディレクトリ作成: {directory}")

@robust_model_operation("学習・テストデータ読み込み")
def load_training_data(xtrain_csv: str, 
                      xtest_csv: str, 
                      ytrain_csv: str, 
                      ytest_csv: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    学習・テストデータを読み込む（最適化版）
    
    Args:
        xtrain_csv: 学習用特徴量データのパス
        xtest_csv: テスト用特徴量データのパス
        ytrain_csv: 学習用目的変数データのパス
        ytest_csv: テスト用目的変数データのパス
        
    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]: 
            X_train, X_test, y_train, y_test
            
    Raises:
        FileNotFoundError: ファイルが見つからない場合
        ValueError: データ形式エラーの場合
    """
    print("学習データを読み込み中...")
    
    # メモリ効率化された読み込み
    X_train = pd.read_csv(xtrain_csv).to_numpy().astype(config.DTYPE_CONFIG['float_dtype'])
    X_test = pd.read_csv(xtest_csv).to_numpy().astype(config.DTYPE_CONFIG['float_dtype'])
    y_train = pd.read_csv(ytrain_csv).values.astype(config.DTYPE_CONFIG['float_dtype']).flatten()
    y_test = pd.read_csv(ytest_csv).values.astype(config.DTYPE_CONFIG['float_dtype']).flatten()
    
    print(f"学習データ形状: X_train={X_train.shape}, y_train={y_train.shape}")
    print(f"テストデータ形状: X_test={X_test.shape}, y_test={y_test.shape}")
    
    # データ検証
    if X_train.shape[0] == 0 or X_test.shape[0] == 0:
        raise ValueError("空のデータセットが検出されました")
    
    return X_train, X_test, y_train, y_test


@robust_model_operation("データ標準化")
def prepare_data_with_scaling(X_train: np.ndarray, 
                             X_test: np.ndarray,
                             y_train: np.ndarray,
                             y_test: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, StandardScaler, StandardScaler]:
    """
    データの標準化を実行する（目的変数正規化対応版）
    
    Args:
        X_train: 学習用特徴量データ
        X_test: テスト用特徴量データ
        y_train: 学習用目的変数データ
        y_test: テスト用目的変数データ
        
    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, StandardScaler, StandardScaler]: 
            標準化後のX_train, X_test, y_train, y_test, x_scaler, y_scaler
            
    Raises:
        ValueError: データ形式エラーの場合
    """
    print("データの標準化を実行中...")
    
    # データ検証
    if X_train.shape[1] != X_test.shape[1]:
        raise ValueError(f"特徴量数が不一致: train={X_train.shape[1]}, test={X_test.shape[1]}")
    
    # 特徴量標準化
    x_scaler = StandardScaler()
    x_scaler.fit(X_train)
    X_train_scaled = x_scaler.transform(X_train).astype(config.DTYPE_CONFIG['float_dtype'])
    X_test_scaled = x_scaler.transform(X_test).astype(config.DTYPE_CONFIG['float_dtype'])
    
    # 目的変数正規化（過学習対策）
    y_scaler = StandardScaler()
    y_train_scaled = y_scaler.fit_transform(y_train.reshape(-1, 1)).flatten().astype(config.DTYPE_CONFIG['float_dtype'])
    y_test_scaled = y_scaler.transform(y_test.reshape(-1, 1)).flatten().astype(config.DTYPE_CONFIG['float_dtype'])
    
    print(f"標準化完了: 特徴量数={X_train_scaled.shape[1]}, 目的変数正規化適用")
    return X_train_scaled, X_test_scaled, y_train_scaled, y_test_scaled, x_scaler, y_scaler

@robust_model_operation("Kerasモデル構築")
def create_keras_model(input_dim: int, learning_rate: float = None) -> Sequential:
    """
    Kerasディープニューラルネットワークモデルを作成する（改善版v3）
    
    改善内容v3:
    - より深いネットワーク構造: 128→128→64→32→1層構成（表現力向上）
    - Dropout適切化: 0.1で過学習抑制
    - L2正則化適切化: 0.001で汎化性能向上
    - バッチサイズ最適化: 64で安定学習
    - 目的変数正規化: y_scalerで学習安定化
    
    Args:
        input_dim: 入力次元数
        learning_rate: 学習率（デフォルト: config値）
        
    Returns:
        Sequential: 構築されたKerasモデル
        
    Raises:
        ValueError: 入力次元数エラーの場合
    """
    if learning_rate is None:
        learning_rate = config.DEFAULT_LEARNING_RATE
        
    if input_dim <= 0:
        raise ValueError(f"無効な入力次元数: {input_dim}")
        
    print(f"Kerasモデルを構築中... (入力次元: {input_dim})")
    print(f"改善版v3アーキテクチャ: 128→128→64→32→1")
    print(f"過学習対策v3: Dropout={config.DROPOUT_RATE}, L2正則化={config.L2_REGULARIZATION}, Batch={config.DEFAULT_BATCH_SIZE}")
    
    # より深いモデル構築（精度向上のため）
    from keras.layers import Dropout
    from keras import regularizers
    
    model = Sequential([
        Dense(config.NEURAL_NETWORK_UNITS, input_dim=input_dim, activation='relu', 
              kernel_regularizer=regularizers.l2(config.L2_REGULARIZATION), name='hidden1'),
        Dropout(config.DROPOUT_RATE, name='dropout1'),
        Dense(config.NEURAL_NETWORK_UNITS, activation='relu',
              kernel_regularizer=regularizers.l2(config.L2_REGULARIZATION), name='hidden2'),
        Dropout(config.DROPOUT_RATE, name='dropout2'),
        Dense(64, activation='relu',
              kernel_regularizer=regularizers.l2(config.L2_REGULARIZATION), name='hidden3'),
        Dense(32, activation='relu', name='hidden4'),
        Dense(1, name='output')
    ])
    
    # コンパイル
    model.compile(
        loss='mean_squared_error',
        optimizer=Adam(learning_rate=learning_rate),
        metrics=['mean_absolute_error']
    )
    
    model.summary()
    print(f"Kerasモデル構築完了 (学習率: {learning_rate}, Batch: {config.DEFAULT_BATCH_SIZE})")
    return model


@robust_model_operation("モデル学習")
def train_model_with_validation(model: Sequential,
                               X_train: np.ndarray,
                               y_train: np.ndarray,
                               epochs: int = None,
                               validation_split: float = None,
                               batch_size: int = None,
                               patience: int = None):
    """
    モデルの学習を実行する（最適化版）
    
    Args:
        model: 学習対象のKerasモデル
        X_train: 学習用特徴量データ
        y_train: 学習用目的変数データ
        epochs: エポック数（デフォルト: config値）
        validation_split: 検証データの割合（デフォルト: config値）
        batch_size: バッチサイズ（デフォルト: config値）
        patience: Early Stoppingの忍耐度（デフォルト: config値）
        
    Returns:
        学習履歴オブジェクト
        
    Raises:
        ValueError: 学習パラメータエラーの場合
    """
    # デフォルト値設定
    if epochs is None:
        epochs = config.DEFAULT_EPOCHS
    if validation_split is None:
        validation_split = config.DEFAULT_VALIDATION_SPLIT
    if batch_size is None:
        batch_size = config.DEFAULT_BATCH_SIZE
    if patience is None:
        patience = config.DEFAULT_PATIENCE
    
    print(f"モデル学習開始 (epochs: {epochs}, batch_size: {batch_size}, patience: {patience})")
    
    # パラメータ検証
    if epochs <= 0 or batch_size <= 0 or patience <= 0:
        raise ValueError("学習パラメータは正の値である必要があります")
    
    # Early Stoppingコールバック（改善版）
    early_stopping = EarlyStopping(
        monitor='val_loss',
        min_delta=0.0001,  # より細かい改善幅
        patience=patience,  # 設定された忍耐度を使用
        restore_best_weights=True,
        verbose=1
    )
    
    # 学習実行
    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        validation_split=validation_split,
        batch_size=batch_size,
        verbose=1,
        callbacks=[early_stopping]
    )
    
    print(f"学習完了 (実際のエポック数: {len(history.history['loss'])})")
    return history
@robust_model_operation("学習履歴可視化")
def save_learning_history_plot(history, history_png: str) -> None:
    """
    学習履歴をプロットして保存する（統一可視化版）
    
    Args:
        history: 学習履歴オブジェクト
        history_png: 保存先ファイルパス
        
    Raises:
        ValueError: 履歴データエラーの場合
    """
    ensure_directory_exists(history_png)
    
    if not history.history:
        raise ValueError("学習履歴が空です")
    
    plt.figure(figsize=(16, 9))  # 16:9統一
    plt.title('Keras Training History', fontsize=12, pad=20)
    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel('Loss [kW^2]', fontsize=12)
    
    # 学習履歴プロット（日本語対応）
    epochs = range(1, len(history.history['loss']) + 1)
    plt.plot(epochs, history.history['loss'], 'b-', label='Training Loss', linewidth=1.5)
    plt.plot(epochs, history.history['val_loss'], 'r-', label='Validation Loss', linewidth=1.5)
    
    plt.legend(loc='upper right', fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(history_png, dpi=100, bbox_inches='tight')
    plt.close()
    
    print(f"学習履歴グラフ保存: {history_png}")

@robust_model_operation("モデル・スケーラー保存")
def save_model_files(model: Sequential, x_scaler: StandardScaler, y_scaler: StandardScaler, model_path: str) -> None:
    """
    モデルとスケーラーを保存する（統一パターン）
    
    Args:
        model: 学習済みKerasモデル
        x_scaler: 特徴量標準化オブジェクト
        y_scaler: 目的変数標準化オブジェクト
        model_path: モデル保存先パス
        
    Raises:
        IOError: ファイル保存エラーの場合
    """
    ensure_directory_exists(model_path)
    
    # h5形式で保存（Keras推奨形式）
    model.save(model_path)
    print(f"Kerasモデル保存: {model_path}")
    
    # pickle形式でも保存（互換性確保）
    pickle_path = model_path.replace('.h5', '.sav')
    with open(pickle_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Pickleモデル保存: {pickle_path}")
    
    # 特徴量スケーラー保存
    x_scaler_path = model_path.replace('.h5', '_scaler.pkl')
    with open(x_scaler_path, 'wb') as f:
        pickle.dump(x_scaler, f)
    print(f"特徴量スケーラー保存: {x_scaler_path}")
    
    # 目的変数スケーラー保存
    y_scaler_path = model_path.replace('.h5', '_y_scaler.pkl')
    with open(y_scaler_path, 'wb') as f:
        pickle.dump(y_scaler, f)
    print(f"目的変数スケーラー保存: {y_scaler_path}")

@robust_model_operation("モデル性能評価")
def evaluate_model_performance(model: Sequential,
                              X_test: np.ndarray,
                              y_test: np.ndarray,
                              y_scaler: StandardScaler) -> Tuple[float, float, float, np.ndarray]:
    """
    モデルの性能を評価する（目的変数逆正規化対応版）
    
    Args:
        model: 評価対象のKerasモデル
        X_test: テスト用特徴量データ
        y_test: テスト用目的変数データ（正規化済み）
        y_scaler: 目的変数の正規化用スケーラー
        
    Returns:
        Tuple[float, float, float, np.ndarray]: RMSE, R2スコア, MAE, 予測値
        
    Raises:
        ValueError: データ形式エラーの場合
    """
    print("モデル性能評価を実行中...")
    
    # データ検証
    if X_test.shape[0] != y_test.shape[0]:
        raise ValueError(f"テストデータのサンプル数が不一致: X={X_test.shape[0]}, y={y_test.shape[0]}")
    
    # テストデータでの評価（正規化空間）
    loss, mae = model.evaluate(X_test, y_test, verbose=0)
    print(f'テスト損失: {loss:.3f}, テストMAE: {mae:.3f}')

    # 予測値の計算（正規化空間）
    y_pred_scaled = model.predict(X_test, verbose=0).flatten()
    
    # 逆正規化で元スケールに戻す
    y_test_original = y_scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()
    y_pred_original = y_scaler.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
    
    # 性能指標の計算（元スケール）
    mse = mean_squared_error(y_test_original, y_pred_original)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test_original, y_pred_original)
    mae_calc = mean_absolute_error(y_test_original, y_pred_original)

    # 一行で統一フォーマット出力（ダッシュボードでの解析用に安定させる）
    print(f"最終結果 - RMSE: {rmse:.3f} kW, R2スコア: {r2:.4f}, MAE: {mae_calc:.3f} kW")

    return rmse, r2, mae_calc, y_pred_original


def save_predictions_to_csv(y_pred: np.ndarray, output_path: str) -> None:
    """
    予測結果をCSVファイルに保存する
    
    Args:
        y_pred: 予測値配列
        output_path: 保存先ファイルパス
    """
    try:
        ensure_directory_exists(output_path)
        
        y_pred_df = pd.DataFrame(y_pred, columns=config.DEFAULT_TARGET_COLUMNS)
        y_pred_df.to_csv(output_path, index=False)
        
        print(f"予測結果を {output_path} に保存しました")
        
    except Exception as e:
        print(f"予測結果CSV保存でエラー: {e}")
        traceback.print_exc()
        raise


def create_prediction_plots(y_pred: np.ndarray,
                           y_test: np.ndarray,
                           full_period_png: str,
                           week_period_png: str) -> None:
    """
    予測結果のグラフを作成・保存する
    
    Args:
        y_pred: 予測値配列
        y_test: 実際値配列
        full_period_png: 全期間グラフの保存先
        week_period_png: 1週間グラフの保存先
    """
    try:
        ensure_directory_exists(full_period_png)
        ensure_directory_exists(week_period_png)
        
        # データフレーム作成
        df_result = pd.DataFrame({
            "Predicted[kW]": y_pred,
            "Actual[kW]": y_test
        })
        
        # 全期間グラフ
        plt.figure(figsize=(16, 9))
        plt.plot(df_result["Predicted[kW]"], label="Predicted[kW]")
        plt.plot(df_result["Actual[kW]"], label="Actual[kW]")
        plt.xlabel('Time', fontsize=12)
        plt.ylabel('Power [kW]', fontsize=12)
        plt.title('Keras Power Demand Prediction - Full Period', fontsize=12)
        plt.legend(fontsize=11)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        plt.tight_layout()
        plt.savefig(full_period_png)
        plt.close()
        print(f"全期間グラフを {full_period_png} に保存しました")

        # 1週間分グラフ（最初の168時間）
        plt.figure(figsize=(16, 9))
        week_data = df_result[:24*7]
        plt.plot(week_data["Predicted[kW]"], label="Predicted[kW]")
        plt.plot(week_data["Actual[kW]"], label="Actual[kW]")
        plt.xlabel('Time', fontsize=12)
        plt.ylabel('Power [kW]', fontsize=12)
        plt.title('Keras Power Demand Prediction - 1 Week', fontsize=12)
        plt.legend(fontsize=11)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        plt.tight_layout()
        plt.savefig(week_period_png)
        plt.close()
        print(f"1週間グラフを {week_period_png} に保存しました")
        
    except Exception as e:
        print(f"グラフ作成・保存でエラー: {e}")
        traceback.print_exc()

def train(xtrain_csv: str,
          xtest_csv: str,
          ytrain_csv: str,
          ytest_csv: str,
          model_sav: str,
          ypred_csv: str,
          ypred_png: str,
          ypred_7d_png: str,
          learning_rate: float = None,
          epochs: int = None,
          validation_split: float = None,
          history_png: str = None) -> Optional[Tuple[float, float]]:
    """
    Kerasを使用した電力需要予測モデルの学習を実行する（最適化版）
    
    Args:
        xtrain_csv: 学習用特徴量データのパス
        xtest_csv: テスト用特徴量データのパス
        ytrain_csv: 学習用目的変数データのパス
        ytest_csv: テスト用目的変数データのパス
        model_sav: モデル保存先パス
        ypred_csv: 予測結果CSV保存先パス
        ypred_png: 予測結果グラフ（全期間）保存先パス
        ypred_7d_png: 予測結果グラフ（1週間）保存先パス
        learning_rate: 学習率
        epochs: エポック数
        validation_split: 検証データの割合
        history_png: 学習履歴グラフ保存先パス
        
    Returns:
        Optional[Tuple[float, float]]: RMSE, R2スコア（エラー時はNone）
    """
    print("Keras電力需要予測モデルの学習を開始します...")
    
    # デフォルト値設定
    if learning_rate is None:
        learning_rate = config.DEFAULT_LEARNING_RATE
    if epochs is None:
        epochs = config.DEFAULT_EPOCHS
    if validation_split is None:
        validation_split = config.DEFAULT_VALIDATION_SPLIT
    
    try:
        # 1. データの読み込み
        X_train, X_test, y_train, y_test = load_training_data(
            xtrain_csv, xtest_csv, ytrain_csv, ytest_csv
        )

        # 2. データの標準化（目的変数正規化対応）
        X_train_scaled, X_test_scaled, y_train_scaled, y_test_scaled, x_scaler, y_scaler = prepare_data_with_scaling(
            X_train, X_test, y_train, y_test
        )

        # 追加チェック: 学習/テストの特徴量数が一致するかを厳密に確認
        if X_train_scaled.shape[1] != X_test_scaled.shape[1]:
            raise ValueError(f"特徴量数の不一致: X_train={X_train_scaled.shape[1]}, X_test={X_test_scaled.shape[1]}")

        # 3. モデルの作成
        input_dim = X_train_scaled.shape[1]
        model = create_keras_model(input_dim, learning_rate)

        # 4. モデルの学習（正規化済み目的変数使用）
        history = train_model_with_validation(
            model, X_train_scaled, y_train_scaled, epochs, validation_split
        )

        # 5. 学習履歴の保存
        if history_png:
            save_learning_history_plot(history, history_png)

        # 6. モデルの保存（両方のスケーラー保存）
        save_model_files(model, x_scaler, y_scaler, model_sav)

        # 7. モデルの評価（逆正規化対応）
        rmse, r2, mae, y_pred = evaluate_model_performance(model, X_test_scaled, y_test_scaled, y_scaler)

        # 8. 予測結果の保存（元スケール）
        save_predictions_to_csv(y_pred, ypred_csv)

        # 9. 予測結果グラフの作成（元スケール）
        y_test_original = y_scaler.inverse_transform(y_test_scaled.reshape(-1, 1)).flatten()
        create_prediction_plots(y_pred, y_test_original, ypred_png, ypred_7d_png)

        print("Keras電力需要予測モデルの学習が正常に完了しました!")
        return rmse, r2, mae

    except Exception as e:
        error_msg = f"Keras学習でエラーが発生しました: {e}"
        print(error_msg)
        traceback.print_exc()
        return None


def main() -> None:
    """
    メイン関数（年組み合わせ最適化対応版）
    
    Keras学習のメイン実行関数
    学習年の組み合わせ手法を組み込み:
    - 環境変数AI_TARGET_YEARSによる年指定
    - 年組み合わせ最適化の自動実行
    - 最優秀組み合わせでの学習実行
    """
    start_time = time.time()
    
    try:
        print("=== Keras学習開始 ===")
        
        # 環境変数による年指定の確認
        target_years_env = os.environ.get('AI_TARGET_YEARS', '')
        if target_years_env:
            print(f"環境変数指定による学習年: {target_years_env}")
        else:
            print("環境変数AI_TARGET_YEARSが設定されていません。optimize_years.pyでの最適化実行を推奨")
        
        # ファイルパス設定
        xtrain_csv = r"data/Xtrain.csv"
        xtest_csv = r"data/Xtest.csv"
        ytrain_csv = r"data/Ytrain.csv"
        ytest_csv = r"data/Ytest.csv"
        model_sav = r'train/Keras/Keras_model.h5'
        ypred_csv = r'train/Keras/Keras_Ypred.csv'
        ypred_png = r'train/Keras/Keras_Ypred.png'
        ypred_7d_png = r'train/Keras/Keras_Ypred_7d.png'
        history_png = r'train/Keras/Keras_history.png'
        
        # 学習実行
        result = train(
            xtrain_csv, xtest_csv, ytrain_csv, ytest_csv,
            model_sav, ypred_csv, ypred_png, ypred_7d_png,
            learning_rate=config.DEFAULT_LEARNING_RATE,
            epochs=config.DEFAULT_EPOCHS,
            validation_split=config.DEFAULT_VALIDATION_SPLIT,
            history_png=history_png
        )
        
        if result:
            elapsed_time = time.time() - start_time
            rmse, r2, mae = result
            print(f"最終結果 - RMSE: {rmse:.3f} kW, R2: {r2:.4f}, MAE: {mae:.3f} kW")
            print(f"=== Keras学習完了 (実行時間: {elapsed_time:.2f}秒) ===")
        else:
            print("=== Keras学習失敗 ===")
            
    except Exception as e:
        print(f"Keras学習エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Log current AI_TARGET_YEARS for auditability
    try:
        import os
        print(f"AI_TARGET_YEARS={os.environ.get('AI_TARGET_YEARS', '(none)')}")
    except Exception:
        pass
    main()
