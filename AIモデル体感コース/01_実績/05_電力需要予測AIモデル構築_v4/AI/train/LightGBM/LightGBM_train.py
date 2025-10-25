# -*- coding: utf-8 -*-
"""
電力需要予測AIモデル - LightGBM学習モジュール

勾配ブースティング決定木を構築し電力需要で学習を行い、
電力消費予測のための予測モデルを作成するモジュール。
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import traceback
import os
import sys
import time
import gc
from dataclasses import dataclass
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import lightgbm as lgb
from typing import Tuple, Optional, Any, Callable
import warnings
from functools import wraps

# パフォーマンス最適化設定（統合版）
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)
np.set_printoptions(suppress=True, precision=4)

# matplotlib最適化設定（16:9統一、日本語対応）
plt.rcParams['figure.figsize'] = (16, 9)
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'
plt.rcParams['savefig.pad_inches'] = 0.1
# フォント優先リスト：Windows 環境では Meiryo / Yu Gothic を最優先にし、それ以外は DejaVu Sans にフォールバック
try:
    from matplotlib import font_manager
    preferred_fonts = ['Meiryo', 'Yu Gothic', 'Noto Sans CJK JP', 'IPAexGothic', 'TakaoPGothic', 'IPAPGothic', 'DejaVu Sans']
    available = {f.name for f in font_manager.fontManager.ttflist}
    chosen = None
    for fname in preferred_fonts:
        if fname in available:
            chosen = fname
            break
    if chosen:
        # font.family はリストで指定してフォールバックを明示
        plt.rcParams['font.family'] = [chosen, 'DejaVu Sans']
    else:
        plt.rcParams['font.family'] = 'DejaVu Sans'
    # マイナス記号が化ける場合の対策
    plt.rcParams['axes.unicode_minus'] = False
except Exception:
    # フォント周りで何かあれば最悪デフォルトに戻す
    plt.rcParams['font.family'] = 'DejaVu Sans'

plt.rcParams['font.size'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 11
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['lines.linewidth'] = 2.0
plt.rcParams['axes.linewidth'] = 1.0
print("=== LightGBM統一最適化設定適用完了 ===")


@dataclass
class LightGBMConfig:
    """LightGBM学習設定統一管理クラス"""
    
    # データ設定
    TARGET_COLUMNS: list = None
    RANDOM_STATE: int = 42
    
    # LightGBMハイパーパラメータ
    DEFAULT_N_ESTIMATORS: int = 100
    DEFAULT_LEARNING_RATE: float = 0.1
    DEFAULT_MAX_DEPTH: int = -1
    DEFAULT_NUM_LEAVES: int = 31
    DEFAULT_MIN_CHILD_SAMPLES: int = 20
    DEFAULT_SUBSAMPLE: float = 1.0
    DEFAULT_COLSAMPLE_BYTREE: float = 1.0
    
    # パフォーマンス設定
    MEMORY_OPTIMIZATION: bool = True
    DATA_TYPE: str = 'float32'
    VERBOSE_LEVEL: int = -1
    
    # 可視化設定
    FIGURE_SIZE: Tuple[int, int] = (16, 9)
    DPI: int = 300
    TITLE_FONTSIZE: int = 14
    LABEL_FONTSIZE: int = 12
    LEGEND_FONTSIZE: int = 11
    
    def __post_init__(self):
        if self.TARGET_COLUMNS is None:
            self.TARGET_COLUMNS = ["KW"]


# 統一設定インスタンス
config = LightGBMConfig()


def robust_model_operation(operation_name: str) -> Callable:
    """
    モデル操作の統一エラーハンドリングデコレータ
    
    Args:
        operation_name: 操作名（ログ用）
        
    Returns:
        Callable: デコレータ関数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                print(f"=== {operation_name} 開始 ===")
                result = func(*args, **kwargs)
                elapsed_time = time.time() - start_time
                print(f"=== {operation_name} 完了 (実行時間: {elapsed_time:.2f}秒) ===")
                return result
            except Exception as e:
                elapsed_time = time.time() - start_time
                print(f"=== {operation_name} エラー (実行時間: {elapsed_time:.2f}秒) ===")
                print(f"エラー詳細: {str(e)}")
                traceback.print_exc()
                raise
            finally:
                # メモリ最適化
                if config.MEMORY_OPTIMIZATION:
                    gc.collect()
        return wrapper
    return decorator

@robust_model_operation("ディレクトリ確認・作成")
def ensure_directory_exists(file_path: str) -> None:
    """
    ファイルパスのディレクトリが存在しない場合は作成する
    
    Args:
        file_path: ファイルパス
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        print(f"ディレクトリを作成しました: {directory}")


@robust_model_operation("学習データ読み込み")
def load_training_data(xtrain_csv: str, 
                      xtest_csv: str, 
                      ytrain_csv: str, 
                      ytest_csv: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    学習・テストデータを読み込む（メモリ最適化済み）
    
    Args:
        xtrain_csv: 学習用特徴量データのパス
        xtest_csv: テスト用特徴量データのパス
        ytrain_csv: 学習用目的変数データのパス
        ytest_csv: テスト用目的変数データのパス
        
    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]: 
            X_train, X_test, y_train, y_test（float32最適化済み）
            
    Raises:
        Exception: ファイル読み込みエラー時
    """
    print("学習データを読み込み中...")
    
    # pandas設定最適化
    pd.set_option('mode.copy_on_write', True)
    
    X_train = pd.read_csv(xtrain_csv).to_numpy().astype(config.DATA_TYPE)
    X_test = pd.read_csv(xtest_csv).to_numpy().astype(config.DATA_TYPE)
    y_train = pd.read_csv(ytrain_csv).values.astype(config.DATA_TYPE).flatten()
    y_test = pd.read_csv(ytest_csv).values.astype(config.DATA_TYPE).flatten()
    
    print(f"学習データ形状: X_train={X_train.shape}, y_train={y_train.shape}")
    print(f"テストデータ形状: X_test={X_test.shape}, y_test={y_test.shape}")
    print(f"メモリ最適化: {config.DATA_TYPE}データ型使用、メモリ使用量約50%削減")
    
    return X_train, X_test, y_train, y_test


@robust_model_operation("データ標準化処理")
def prepare_data_with_scaling(X_train: np.ndarray, 
                             X_test: np.ndarray) -> Tuple[np.ndarray, np.ndarray, StandardScaler]:
    """
    データの標準化を実行する（メモリ最適化済み）
    
    Args:
        X_train: 学習用特徴量データ
        X_test: テスト用特徴量データ
        
    Returns:
        Tuple[np.ndarray, np.ndarray, StandardScaler]: 
            標準化後のX_train, X_test, scaler（float32最適化済み）
    """
    print("データの標準化を実行中...")
    scaler = StandardScaler()
    
    X_train_scaled = scaler.fit_transform(X_train).astype(config.DATA_TYPE)
    X_test_scaled = scaler.transform(X_test).astype(config.DATA_TYPE)
    
    print(f"データの標準化が完了しました（{config.DATA_TYPE}最適化済み）")
    return X_train_scaled, X_test_scaled, scaler


@robust_model_operation("LightGBMモデル構築")
def create_lightgbm_model(n_estimators: int = None,
                         learning_rate: float = None,
                         max_depth: int = None,
                         num_leaves: int = None,
                         min_child_samples: int = None,
                         subsample: float = None,
                         colsample_bytree: float = None) -> lgb.LGBMRegressor:
    """
    LightGBMリグレッサーモデルを作成する（統一設定対応）
    
    Args:
        n_estimators: 決定木の数
        learning_rate: 学習率
        max_depth: 最大深度
        num_leaves: 葉ノード数
        min_child_samples: 子ノードの最小サンプル数
        subsample: サブサンプリング比率
        colsample_bytree: 特徴量サンプリング比率
        
    Returns:
        lgb.LGBMRegressor: 構築されたLightGBMモデル
    """
    print("LightGBMモデルを構築中...")
    
    # 設定値の適用（引数優先、次にconfig値）
    params = {
        'n_estimators': n_estimators or config.DEFAULT_N_ESTIMATORS,
        'learning_rate': learning_rate or config.DEFAULT_LEARNING_RATE,
        'max_depth': max_depth or config.DEFAULT_MAX_DEPTH,
        'num_leaves': num_leaves or config.DEFAULT_NUM_LEAVES,
        'min_child_samples': min_child_samples or config.DEFAULT_MIN_CHILD_SAMPLES,
        'subsample': subsample or config.DEFAULT_SUBSAMPLE,
        'colsample_bytree': colsample_bytree or config.DEFAULT_COLSAMPLE_BYTREE,
        'random_state': config.RANDOM_STATE,
        'verbose': config.VERBOSE_LEVEL
    }
    
    model = lgb.LGBMRegressor(**params)
    
    print(f"LightGBMモデル構築完了 - パラメータ: {params}")
    return model


@robust_model_operation("LightGBMモデル学習")
def train_lightgbm_model(model: lgb.LGBMRegressor,
                        X_train: np.ndarray,
                        y_train: np.ndarray) -> lgb.LGBMRegressor:
    """
    LightGBMモデルの学習を実行する
    
    Args:
        model: 学習対象のLightGBMモデル
        X_train: 学習用特徴量データ
        y_train: 学習用目的変数データ
        
    Returns:
        lgb.LGBMRegressor: 学習済みモデル
    """
    print("LightGBMモデルの学習を開始します...")
    
    model.fit(X_train, y_train)
    
    print("LightGBMモデルの学習が完了しました")
    return model


@robust_model_operation("モデル・スケーラー保存")
def save_model_and_scaler(model: lgb.LGBMRegressor, scaler: StandardScaler, model_path: str) -> None:
    """
    モデルとスケーラーを保存する
    
    Args:
        model: 学習済みLightGBMモデル
        scaler: 標準化オブジェクト
        model_path: モデル保存先パス
    """
    ensure_directory_exists(model_path)
    
    # モデルをpickle形式で保存
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"LightGBMモデルを {model_path} に保存しました")
    
    # スケーラーを保存
    scaler_path = model_path.replace('.sav', '_scaler.pkl')
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"スケーラーを {scaler_path} に保存しました")


@robust_model_operation("モデル性能評価")
def evaluate_model_performance(model: lgb.LGBMRegressor,
                              X_test: np.ndarray,
                              y_test: np.ndarray) -> Tuple[float, float, float, np.ndarray]:
    """
    モデルの性能を評価する（統一指標対応）
    
    Args:
        model: 評価対象のLightGBMモデル
        X_test: テスト用特徴量データ
        y_test: テスト用目的変数データ
        
    Returns:
        Tuple[float, float, float, np.ndarray]: RMSE, R2スコア, MAE, 予測値
    """
    print("=== モデル性能評価開始 ===")
    print("モデル性能評価を実行中...")
    
    # テストスコア
    test_score = model.score(X_test, y_test)
    print(f'テストスコア: {test_score:.4f}')

    # 予測値の計算
    y_pred = model.predict(X_test).astype(config.DATA_TYPE)
    
    # 性能指標の計算
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    print(f'テスト損失: {mse:.3f}, テストMAE: {mae:.3f}')
    print(f'RMSE: {rmse:.3f} kW')
    print(f'R2スコア: {r2:.4f}')
    print(f'MAE: {mae:.3f} kW')
    print("=== モデル性能評価完了 ===")
    
    return rmse, r2, mae, y_pred


@robust_model_operation("予測結果CSV保存")
def save_predictions_to_csv(y_pred: np.ndarray, output_path: str) -> None:
    """
    予測結果をCSVファイルに保存する
    
    Args:
        y_pred: 予測値配列
        output_path: 保存先ファイルパス
    """
    ensure_directory_exists(output_path)
    
    y_pred_df = pd.DataFrame(y_pred, columns=config.TARGET_COLUMNS)
    y_pred_df.to_csv(output_path, index=False)
    
    print(f"予測結果を {output_path} に保存しました（{len(y_pred)}行）")


@robust_model_operation("予測結果可視化")
def create_prediction_plots(y_pred: np.ndarray,
                           y_test: np.ndarray,
                           full_period_png: str,
                           week_period_png: str) -> None:
    """
    予測結果のグラフを作成・保存する（統一16:9フォーマット）
    
    Args:
        y_pred: 予測値配列
        y_test: 実際値配列
        full_period_png: 全期間グラフの保存先
        week_period_png: 1週間グラフの保存先
    """
    ensure_directory_exists(full_period_png)
    ensure_directory_exists(week_period_png)
    
    # データフレーム作成
    df_result = pd.DataFrame({
        "Predicted[kW]": y_pred,
        "Actual[kW]": y_test
    })
    
    # 全期間グラフ（16:9統一フォーマット）
    plt.figure(figsize=config.FIGURE_SIZE)
    plt.plot(df_result["Predicted[kW]"], label="Predicted[kW]", linewidth=2, alpha=0.8)
    plt.plot(df_result["Actual[kW]"], label="Actual[kW]", linewidth=2, alpha=0.8)
    plt.xlabel('Time', fontsize=config.LABEL_FONTSIZE)
    plt.ylabel('Power [kW]', fontsize=config.LABEL_FONTSIZE)
    plt.title('LightGBM Power Demand Prediction - Full Period', fontsize=config.TITLE_FONTSIZE)
    plt.legend(fontsize=config.LEGEND_FONTSIZE)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(full_period_png, dpi=config.DPI, bbox_inches='tight')
    plt.close()
    print(f"全期間グラフを {full_period_png} に保存しました（16:9統一フォーマット）")

    # 1週間分グラフ（最初の168時間）
    plt.figure(figsize=config.FIGURE_SIZE)
    week_data = df_result[:24*7]
    plt.plot(week_data["Predicted[kW]"], label="Predicted[kW]", linewidth=2, alpha=0.8)
    plt.plot(week_data["Actual[kW]"], label="Actual[kW]", linewidth=2, alpha=0.8)
    plt.xlabel('Time', fontsize=config.LABEL_FONTSIZE)
    plt.ylabel('Power [kW]', fontsize=config.LABEL_FONTSIZE)
    plt.title('LightGBM Power Demand Prediction - 1 Week', fontsize=config.TITLE_FONTSIZE)
    plt.legend(fontsize=config.LEGEND_FONTSIZE)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(week_period_png, dpi=config.DPI, bbox_inches='tight')
    plt.close()
    print(f"1週間グラフを {week_period_png} に保存しました（16:9統一フォーマット）")

@robust_model_operation("LightGBM学習統合処理")
def train(xtrain_csv: str,
          xtest_csv: str,
          ytrain_csv: str,
          ytest_csv: str,
          model_sav: str,
          ypred_csv: str,
          ypred_png: str,
          ypred_7d_png: str,
          learning_rate: Optional[str] = None,
          epochs: Optional[str] = None,
          validation_split: Optional[str] = None,
          history_png: Optional[str] = None) -> Optional[Tuple[float, float, float]]:
    """
    LightGBMを使用した電力需要予測モデルの学習を実行する（統一パターン対応）
    
    Args:
        xtrain_csv: 学習用特徴量データのパス
        xtest_csv: テスト用特徴量データのパス
        ytrain_csv: 学習用目的変数データのパス
        ytest_csv: テスト用目的変数データのパス
        model_sav: モデル保存先パス
        ypred_csv: 予測結果CSV保存先パス
        ypred_png: 予測結果グラフ（全期間）保存先パス
        ypred_7d_png: 予測結果グラフ（1週間）保存先パス
        learning_rate: 学習率（LightGBM用、文字列）
        epochs: エポック数（使用されない、互換性のため）
        validation_split: 検証データ割合（使用されない、互換性のため）
        history_png: 学習履歴グラフ（使用されない、互換性のため）
        
    Returns:
        Optional[Tuple[float, float, float]]: RMSE, R2スコア, MAE（エラー時はNone）
    """
    print("=== LightGBM電力需要予測モデル学習開始 ===")
    
    # 1. データの読み込み
    X_train, X_test, y_train, y_test = load_training_data(
        xtrain_csv, xtest_csv, ytrain_csv, ytest_csv
    )
    
    # 2. データの標準化
    X_train_scaled, X_test_scaled, scaler = prepare_data_with_scaling(X_train, X_test)
    
    # 3. モデルの作成（学習率の設定）
    lr = config.DEFAULT_LEARNING_RATE
    if learning_rate is not None:
        try:
            # 文字列または数値の場合の処理
            if isinstance(learning_rate, str) and learning_rate.strip():
                lr = float(learning_rate)
            elif isinstance(learning_rate, (int, float)):
                lr = float(learning_rate)
            print(f"学習率を {lr} に設定しました")
        except (ValueError, TypeError):
            print(f"無効な学習率: {learning_rate}、デフォルト値 {config.DEFAULT_LEARNING_RATE} を使用します")
    
    model = create_lightgbm_model(learning_rate=lr)
    
    # 4. モデルの学習
    trained_model = train_lightgbm_model(model, X_train_scaled, y_train)
    
    # 5. モデルとスケーラーの保存
    save_model_and_scaler(trained_model, scaler, model_sav)
    
    # 6. モデルの評価
    rmse, r2, mae, y_pred = evaluate_model_performance(trained_model, X_test_scaled, y_test)
    
    # 7. 予測結果の保存
    save_predictions_to_csv(y_pred, ypred_csv)
    
    # 8. 予測結果グラフの作成
    create_prediction_plots(y_pred, y_test, ypred_png, ypred_7d_png)
    
    print("=== LightGBM電力需要予測モデル学習完了 ===")
    return rmse, r2, mae


def main() -> None:
    """
    LightGBMモデル学習のメイン実行関数
    
    機能:
    - ファイルパス設定
    - ハイパーパラメータ設定
    - 学習実行
    - 結果出力
    - エラーハンドリング
    - パフォーマンス最適化
    - 可視化統一
    """
    start_time = time.time()
    
    try:
        print("=== LightGBM学習開始 ===")
        
        # ファイルパス設定
        xtrain_csv = r"data/Xtrain.csv"
        xtest_csv = r"data/Xtest.csv"
        ytrain_csv = r"data/Ytrain.csv"
        ytest_csv = r"data/Ytest.csv"
        model_sav = r'train/LightGBM/LightGBM_model.sav'
        ypred_csv = r'train/LightGBM/LightGBM_Ypred.csv'
        ypred_png = r'train/LightGBM/LightGBM_Ypred.png'
        ypred_7d_png = r'train/LightGBM/LightGBM_Ypred_7d.png'
        
        # ハイパーパラメータ設定（LightGBMでは使用されないが互換性のため）
        learning_rate_param = config.DEFAULT_LEARNING_RATE
        epochs = ''
        validation_split = ''
        history_png = r'train/LightGBM/LightGBM_history.png'

        # 学習実行
        result = train(
            xtrain_csv, xtest_csv, ytrain_csv, ytest_csv,
            model_sav, ypred_csv, ypred_png, ypred_7d_png,
            learning_rate=learning_rate_param,
            epochs=epochs,
            validation_split=validation_split,
            history_png=history_png
        )
        
        if result:
            rmse, r2, mae = result
            elapsed_time = time.time() - start_time
            print(f"=== LightGBM学習完了 (実行時間: {elapsed_time:.2f}秒) ===")
            print(f"最終結果 - RMSE: {rmse:.3f} kW, R2スコア: {r2:.4f}, MAE: {mae:.3f} kW")
        else:
            print("=== LightGBM学習失敗 ===")
            
    except Exception as e:
        print(f"LightGBM学習エラー: {e}")
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
