# -*- coding: utf-8 -*-
"""
電力需要予測AIモデル - PyCaret学習モジュール

自動機械学習ライブラリを使用し電力需要で学習を行い、
電力消費予測のための予測モデルを作成するモジュール。
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import traceback
import os
import sys
import gc
import functools
from dataclasses import dataclass, field
from typing import Tuple, Optional, Any, Dict, List, Callable
from pathlib import Path
import warnings

# PyCaret regression モジュール
from pycaret.regression import *
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# パフォーマンス最適化設定（統合版）
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)
np.set_printoptions(suppress=True, precision=4)

# matplotlib最適化設定（16:9アスペクト比統一）
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

plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['lines.linewidth'] = 1.5
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['figure.max_open_warning'] = 10
print("PyCaret: パフォーマンス最適化設定を適用しました")


@dataclass
class PyCaretConfig:
    """
    PyCaret電力需要予測モデルの設定管理クラス
    
    統一設定:
    - データ型: float32でメモリ最適化
    - 可視化: 16:9アスペクト比統一
    - 自動ML: PyCaret最適化パラメータ
    """
    # データ設定
    feature_columns: List[str] = field(default_factory=lambda: ["MONTH", "WEEK", "HOUR", "TEMP"])
    target_columns: List[str] = field(default_factory=lambda: ["KW"])
    target_column_name: str = "KW"
    prediction_column_name: str = 'prediction_label'
    data_dtype: str = 'float32'
    
    # PyCaret モデル設定
    model_type: str = 'lightgbm'  # Light Gradient Boosting Machine（高性能）
    cv_folds: int = 10
    session_id: int = 123
    silent_mode: bool = True
    
    # 可視化設定（16:9アスペクト比統一）
    figure_size: Tuple[int, int] = (16, 9)
    figure_dpi: int = 100
    font_size_title: int = 12
    font_size_label: int = 12
    font_size_legend: int = 11
    font_size_tick: int = 10
    
    # 性能監視設定
    enable_memory_optimization: bool = True
    enable_garbage_collection: bool = True
    
    def get_pycaret_setup_params(self) -> Dict[str, Any]:
        """PyCaretセットアップパラメータを取得"""
        base_params = {
            'session_id': self.session_id,
        }
        
        # バージョン互換性のための段階的パラメータ
        try_params = [
            {'silent': self.silent_mode},
            {'verbose': not self.silent_mode},
            {}  # 基本パラメータのみ
        ]
        
        return base_params, try_params
    
    def optimize_memory_if_enabled(self) -> None:
        """メモリ最適化実行（有効時のみ）"""
        if self.enable_garbage_collection:
            gc.collect()
            print("メモリ最適化を実行しました")


def robust_model_operation(operation_name: str):
    """
    統一モデル操作デコレータ - エラーハンドリングと性能監視を提供
    
    Args:
        operation_name: 操作名（ログ出力用）
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(f"PyCaret {operation_name} を開始します...")
            try:
                result = func(*args, **kwargs)
                print(f"PyCaret {operation_name} が正常に完了しました")
                return result
            except Exception as e:
                error_msg = f"PyCaret {operation_name} でエラーが発生しました: {e}"
                print(error_msg)
                traceback.print_exc()
                raise Exception(error_msg) from e
        return wrapper
    return decorator

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


@robust_model_operation("データ読み込み")
def load_training_data(config: PyCaretConfig,
                      xtrain_csv: str, 
                      xtest_csv: str, 
                      ytrain_csv: str, 
                      ytest_csv: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    学習・テストデータを読み込む（PyCaretConfig対応版）
    
    Args:
        config: PyCaret設定オブジェクト
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
    # float32型でメモリ効率を向上
    dtype = config.data_dtype
    
    print("学習データを読み込み中...")
    # CSVのヘッダを保持して読み込み、実際の特徴量列名を config に反映する
    X_train_df = pd.read_csv(xtrain_csv)
    X_test_df = pd.read_csv(xtest_csv)

    # 読み込んだ実際の列名を config.feature_columns に設定（後続処理で使用されるため）
    try:
        cols = list(X_train_df.columns)
        if cols:
            config.feature_columns = cols
            print(f"設定: 読み込んだ特徴量列を config.feature_columns に反映しました ({len(cols)} 列)")
    except Exception as e:
        print(f"特徴量列の反映に失敗しました: {e}")

    X_train = X_train_df.to_numpy().astype(dtype)
    X_test = X_test_df.to_numpy().astype(dtype)
    y_train = pd.read_csv(ytrain_csv).values.astype(dtype).flatten()
    y_test = pd.read_csv(ytest_csv).values.astype(dtype).flatten()
    
    print(f"学習データ形状: X_train={X_train.shape}, y_train={y_train.shape}")
    print(f"テストデータ形状: X_test={X_test.shape}, y_test={y_test.shape}")
    print(f"データ型: {dtype} (メモリ最適化)")
    
    # メモリ最適化
    config.optimize_memory_if_enabled()
    
    return X_train, X_test, y_train, y_test


@robust_model_operation("PyCaret実験環境セットアップ")
def setup_pycaret_experiment(config: PyCaretConfig, 
                            X_train: np.ndarray, 
                            y_train: np.ndarray) -> Any:
    """
    PyCaretの実験環境をセットアップする（設定管理統一版）
    
    Args:
        config: PyCaret設定オブジェクト
        X_train: 学習用特徴量データ
        y_train: 学習用目的変数データ
        
    Returns:
        Any: PyCaretの実験オブジェクト
    """
    # データフレームの作成
    train_data = pd.concat([
        pd.DataFrame(X_train, columns=config.feature_columns),
        pd.DataFrame(y_train, columns=config.target_columns)
    ], axis=1)
    
    # PyCaretセットアップ（バージョン互換性対応）
    base_params, try_params = config.get_pycaret_setup_params()
    
    for additional_params in try_params:
        try:
            setup_params = {
                'data': train_data,
                'target': config.target_column_name,
                **base_params,
                **additional_params
            }
            exp = setup(**setup_params)
            print(f"PyCaretセットアップ成功: {setup_params}")
            break
        except TypeError as e:
            print(f"PyCaretパラメータ {additional_params} でエラー: {e}")
            continue
    else:
        # 最小限のパラメータでセットアップ
        exp = setup(
            data=train_data,
            target=config.target_column_name,
            session_id=config.session_id
        )
        print("PyCaretセットアップ: 基本パラメータで実行")
    
    return exp


@robust_model_operation("PyCaretモデル作成・学習")
def create_pycaret_model(config: PyCaretConfig) -> Any:
    """
    PyCaretモデルを作成・学習する（設定統一版）
    
    Args:
        config: PyCaret設定オブジェクト
        
    Returns:
        Any: 学習済みPyCaretモデル
    """
    print(f"PyCaretモデル（{config.model_type}）を作成・学習中...")
    
    model = create_model(config.model_type, fold=config.cv_folds)
    
    # メモリ最適化
    config.optimize_memory_if_enabled()
    
    return model


@robust_model_operation("PyCaretモデル保存")
def save_pycaret_model(config: PyCaretConfig, model: Any, model_path: str) -> None:
    """
    PyCaretモデルを保存する（設定統一版）
    
    Args:
        config: PyCaret設定オブジェクト
        model: 学習済みPyCaretモデル
        model_path: モデル保存先パス
    """
    ensure_directory_exists(model_path + '.pkl')  # PyCaretは拡張子を自動付加
    
    save_model(model, model_name=model_path)
    print(f"PyCaretモデルを {model_path}.pkl に保存しました")


@robust_model_operation("PyCaretモデル予測")
def predict_with_pycaret_model(config: PyCaretConfig, 
                              model: Any, 
                              X_test: np.ndarray) -> np.ndarray:
    """
    PyCaretモデルで予測を実行する（設定統一版）
    
    Args:
        config: PyCaret設定オブジェクト
        model: 学習済みPyCaretモデル
        X_test: テスト用特徴量データ
        
    Returns:
        np.ndarray: 予測値配列
    """
    # テストデータをDataFrameに変換
    test_df = pd.DataFrame(X_test, columns=config.feature_columns)
    
    # 予測実行
    predictions = predict_model(model, data=test_df)
    
    # 予測列のみを抽出し一次元配列に変換
    y_pred = predictions[config.prediction_column_name].values
    
    print(f"予測が完了しました。予測値の形状: {y_pred.shape}")
    
    # メモリ最適化
    config.optimize_memory_if_enabled()
    
    return y_pred

@robust_model_operation("モデル性能評価")
def evaluate_model_performance(config: PyCaretConfig,
                              model: Any,
                              X_test: np.ndarray,
                              y_test: np.ndarray,
                              y_pred: np.ndarray) -> Tuple[float, float, float]:
    """
    モデルの性能を評価する（設定統一版）
    
    Args:
        config: PyCaret設定オブジェクト
        model: 評価対象のPyCaretモデル
        X_test: テスト用特徴量データ
        y_test: テスト用目的変数データ
        y_pred: 予測値
        
    Returns:
        Tuple[float, float]: RMSE, R2スコア
    """
    # PyCaretモデルのスコア（参考値）
    try:
        test_score = model.score(X_test, y_test)
        print(f'PyCaretテストスコア: {test_score:.3f}')
    except Exception as e:
        print(f"PyCaretスコア計算でエラー: {e}")
    
    # 性能指標の計算
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    # 一行で統一フォーマット出力
    print(f"最終結果 - RMSE: {rmse:.3f} kW, R2: {r2:.4f}, MAE: {mae:.3f} kW")

    return rmse, r2, mae


@robust_model_operation("予測結果CSV保存")
def save_predictions_to_csv(config: PyCaretConfig, 
                           y_pred: np.ndarray, 
                           output_path: str) -> None:
    """
    予測結果をCSVファイルに保存する（設定統一版）
    
    Args:
        config: PyCaret設定オブジェクト
        y_pred: 予測値配列
        output_path: 保存先ファイルパス
    """
    ensure_directory_exists(output_path)
    
    y_pred_df = pd.DataFrame(y_pred, columns=config.target_columns)
    y_pred_df.to_csv(output_path, index=False)
    
    print(f"予測結果を {output_path} に保存しました")


@robust_model_operation("予測結果グラフ作成")
def create_prediction_plots(config: PyCaretConfig,
                           y_pred: np.ndarray,
                           y_test: np.ndarray,
                           full_period_png: str,
                           week_period_png: str) -> None:
    """
    予測結果のグラフを作成・保存する（設定統一版・16:9アスペクト比）
    
    Args:
        config: PyCaret設定オブジェクト
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
    
    # 全期間グラフ（16:9アスペクト比統一）
    plt.figure(figsize=config.figure_size, dpi=config.figure_dpi)
    plt.plot(df_result["Predicted[kW]"], label="Predicted[kW]")
    plt.plot(df_result["Actual[kW]"], label="Actual[kW]")
    plt.xlabel('Time', fontsize=config.font_size_label)
    plt.ylabel('Power [kW]', fontsize=config.font_size_label)
    plt.title('PyCaret Power Demand Prediction - Full Period', fontsize=config.font_size_title)
    plt.legend(fontsize=config.font_size_legend)
    plt.xticks(fontsize=config.font_size_tick)
    plt.yticks(fontsize=config.font_size_tick)
    plt.tight_layout()
    plt.savefig(full_period_png)
    plt.close()
    print(f"全期間グラフを {full_period_png} に保存しました")

    # 1週間分グラフ（最初の168時間・16:9アスペクト比統一）
    plt.figure(figsize=config.figure_size, dpi=config.figure_dpi)
    week_data = df_result[:24*7]
    plt.plot(week_data["Predicted[kW]"], label="Predicted[kW]")
    plt.plot(week_data["Actual[kW]"], label="Actual[kW]")
    plt.xlabel('Time', fontsize=config.font_size_label)
    plt.ylabel('Power [kW]', fontsize=config.font_size_label)
    plt.title('PyCaret Power Demand Prediction - 1 Week', fontsize=config.font_size_title)
    plt.legend(fontsize=config.font_size_legend)
    plt.xticks(fontsize=config.font_size_tick)
    plt.yticks(fontsize=config.font_size_tick)
    plt.tight_layout()
    plt.savefig(week_period_png)
    plt.close()
    print(f"1週間グラフを {week_period_png} に保存しました")
    
    # メモリ最適化
    config.optimize_memory_if_enabled()

@robust_model_operation("PyCaret電力需要予測モデル学習")
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
          history_png: Optional[str] = None) -> Optional[Tuple[float, float]]:
    """
    PyCaretを使用した電力需要予測モデルの学習を実行する（統一仕様版）
    
    Args:
        xtrain_csv: 学習用特徴量データのパス
        xtest_csv: テスト用特徴量データのパス
        ytrain_csv: 学習用目的変数データのパス
        ytest_csv: テスト用目的変数データのパス
        model_sav: モデル保存先パス
        ypred_csv: 予測結果CSV保存先パス
        ypred_png: 予測結果グラフ（全期間）保存先パス
        ypred_7d_png: 予測結果グラフ（1週間）保存先パス
        learning_rate: 学習率（使用されない、互換性のため）
        epochs: エポック数（使用されない、互換性のため）
        validation_split: 検証データ割合（使用されない、互換性のため）
        history_png: 学習履歴グラフ（使用されない、互換性のため）
        
    Returns:
        Optional[Tuple[float, float]]: RMSE, R2スコア（エラー時はNone）
    """
    # 設定オブジェクト初期化
    config = PyCaretConfig()
    
    # 1. データの読み込み
    X_train, X_test, y_train, y_test = load_training_data(
        config, xtrain_csv, xtest_csv, ytrain_csv, ytest_csv
    )
    
    # 2. PyCaret実験環境のセットアップ
    exp = setup_pycaret_experiment(config, X_train, y_train)
    
    # 3. モデルの作成・学習
    model = create_pycaret_model(config)
    
    # 4. モデルの保存
    save_pycaret_model(config, model, model_sav)
    
    # 5. 予測の実行
    y_pred = predict_with_pycaret_model(config, model, X_test)
    
    # 6. モデルの評価
    rmse, r2, mae = evaluate_model_performance(config, model, X_test, y_test, y_pred)
    
    # 7. 予測結果の保存
    save_predictions_to_csv(config, y_pred, ypred_csv)
    
    # 8. 予測結果グラフの作成
    create_prediction_plots(config, y_pred, y_test, ypred_png, ypred_7d_png)
    
    return rmse, r2, mae


def main() -> None:
    """
    メイン実行関数（統一仕様版）
    
    PyCaretConfigを使用した設定管理で、
    電力需要予測モデルの学習プロセスを実行
    """
    print("="*60)
    print("PyCaret電力需要予測AIモデル学習システム")
    print("統一リファクタリング仕様 - PyCaretConfig対応版")
    print("="*60)
    
    # ファイルパス設定
    xtrain_csv = r"data/Xtrain.csv"
    xtest_csv = r"data/Xtest.csv"
    ytrain_csv = r"data/Ytrain.csv"
    ytest_csv = r"data/Ytest.csv"
    model_sav = r'train/Pycaret/Pycaret_model'
    ypred_csv = r'train/Pycaret/Pycaret_Ypred.csv'
    ypred_png = r'train/Pycaret/Pycaret_Ypred.png'
    ypred_7d_png = r'train/Pycaret/Pycaret_Ypred_7d.png'
    
    # ハイパーパラメータ設定（PyCaretでは使用されないが互換性のため）
    learning_rate = ''
    epochs = ''
    validation_split = ''
    history_png = r'train/Pycaret/Pycaret_history.png'

    try:
        # 学習実行
        result = train(
            xtrain_csv, xtest_csv, ytrain_csv, ytest_csv, model_sav,
            ypred_csv, ypred_png, ypred_7d_png,
            learning_rate, epochs, validation_split, history_png
        )
        
        if result:
            rmse, r2, mae = result
            print("="*60)
            print(f"[SUCCESS] PyCaret学習完了 - RMSE: {rmse:.3f} kW, R2: {r2:.4f}, MAE: {mae:.3f} kW")
            print("="*60)
        else:
            print("[ERROR] 学習処理が失敗しました")
            
    except Exception as e:
        print(f"[ERROR] メイン処理でエラーが発生しました: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    # Log current AI_TARGET_YEARS for auditability
    try:
        import os
        print(f"AI_TARGET_YEARS={os.environ.get('AI_TARGET_YEARS', '(none)')}")
    except Exception:
        pass
    main()
