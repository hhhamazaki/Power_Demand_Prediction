# -*- coding: utf-8 -*-
"""
電力需要予測AIモデル - RandomForest学習モジュール

ランダムフォレスト回帰を構築し電力需要で学習を行い、
電力消費予測のための予測モデルを作成するモジュール。
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import traceback
import os
import sys
import gc
import functools
from dataclasses import dataclass, field
from typing import Tuple, Optional, List, Callable
from pathlib import Path
import warnings

# sklearn関連
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# パフォーマンス最適化設定（統合版）
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
np.set_printoptions(suppress=True, precision=4)

# matplotlib最適化設定（16:9アスペクト比統一）
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
plt.rcParams['figure.max_open_warning'] = 10
print("RandomForest: パフォーマンス最適化設定を適用しました")


@dataclass
class RandomForestConfig:
    """
    RandomForest電力需要予測モデルの設定管理クラス
    
    統一設定:
    - データ型: float32でメモリ最適化
    - 可視化: 16:9アスペクト比統一
    - ランダムフォレスト: scikit-learn最適化パラメータ
    """
    # データ設定
    target_columns: List[str] = field(default_factory=lambda: ["KW"])
    data_dtype: str = 'float32'
    
    # RandomForest モデル設定
    n_estimators: int = 100
    max_depth: Optional[int] = None
    min_samples_split: int = 2
    min_samples_leaf: int = 1
    max_features: str = 'sqrt'
    n_jobs: int = -1  # すべてのCPUコアを使用（パフォーマンス最適化）
    random_state: int = 42
    
    # データ前処理設定
    enable_scaling: bool = True
    scaler_type: str = 'StandardScaler'
    
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
    
    def get_model_params(self) -> dict:
        """RandomForestモデルパラメータを取得"""
        return {
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
            'min_samples_split': self.min_samples_split,
            'min_samples_leaf': self.min_samples_leaf,
            'max_features': self.max_features,
            'n_jobs': self.n_jobs,
            'random_state': self.random_state
        }
    
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
            print(f"RandomForest {operation_name} を開始します...")
            try:
                result = func(*args, **kwargs)
                print(f"RandomForest {operation_name} が正常に完了しました")
                return result
            except Exception as e:
                error_msg = f"RandomForest {operation_name} でエラーが発生しました: {e}"
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
def load_training_data(config: RandomForestConfig,
                      xtrain_csv: str, 
                      xtest_csv: str, 
                      ytrain_csv: str, 
                      ytest_csv: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    学習・テストデータを読み込む（RandomForestConfig対応版）
    
    Args:
        config: RandomForest設定オブジェクト
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
    X_train = pd.read_csv(xtrain_csv).to_numpy().astype(dtype)
    X_test = pd.read_csv(xtest_csv).to_numpy().astype(dtype)
    y_train = pd.read_csv(ytrain_csv).values.astype(dtype).flatten()
    y_test = pd.read_csv(ytest_csv).values.astype(dtype).flatten()
    
    print(f"学習データ形状: X_train={X_train.shape}, y_train={y_train.shape}")
    print(f"テストデータ形状: X_test={X_test.shape}, y_test={y_test.shape}")
    print(f"データ型: {dtype} (メモリ最適化)")
    
    # メモリ最適化
    config.optimize_memory_if_enabled()
    
    return X_train, X_test, y_train, y_test


@robust_model_operation("データ標準化")
def prepare_data_with_scaling(config: RandomForestConfig,
                             X_train: np.ndarray, 
                             X_test: np.ndarray) -> Tuple[np.ndarray, np.ndarray, StandardScaler]:
    """
    データの標準化を実行する（設定統一版）
    
    Args:
        config: RandomForest設定オブジェクト
        X_train: 学習用特徴量データ
        X_test: テスト用特徴量データ
        
    Returns:
        Tuple[np.ndarray, np.ndarray, StandardScaler]: 
            標準化後のX_train, X_test, scaler
    """
    if not config.enable_scaling:
        print("データ標準化をスキップします")
        return X_train, X_test, None
    
    scaler = StandardScaler()
    scaler.fit(X_train)
    X_train_scaled = scaler.transform(X_train).astype(config.data_dtype)
    X_test_scaled = scaler.transform(X_test).astype(config.data_dtype)
    
    # メモリ最適化
    config.optimize_memory_if_enabled()
    
    return X_train_scaled, X_test_scaled, scaler


@robust_model_operation("RandomForestモデル作成")
def create_random_forest_model(config: RandomForestConfig) -> RandomForestRegressor:
    """
    Random Forestリグレッサーモデルを作成する（設定統一版）
    
    Args:
        config: RandomForest設定オブジェクト
        
    Returns:
        RandomForestRegressor: 構築されたRandom Forestモデル
    """
    model_params = config.get_model_params()
    print(f"Random Forestモデルパラメータ: {model_params}")
    
    model = RandomForestRegressor(**model_params)
    
    return model


@robust_model_operation("RandomForestモデル学習")
def train_random_forest_model(config: RandomForestConfig,
                             model: RandomForestRegressor,
                             X_train: np.ndarray,
                             y_train: np.ndarray) -> RandomForestRegressor:
    """
    Random Forestモデルの学習を実行する（設定統一版）
    
    Args:
        config: RandomForest設定オブジェクト
        model: 学習対象のRandom Forestモデル
        X_train: 学習用特徴量データ
        y_train: 学習用目的変数データ
        
    Returns:
        RandomForestRegressor: 学習済みモデル
    """
    model.fit(X_train, y_train)
    
    # メモリ最適化
    config.optimize_memory_if_enabled()
    
    return model

@robust_model_operation("モデル・スケーラー保存")
def save_model_and_scaler(config: RandomForestConfig,
                         model: RandomForestRegressor, 
                         scaler: Optional[StandardScaler], 
                         model_path: str) -> None:
    """
    モデルとスケーラーを保存する（設定統一版）
    
    Args:
        config: RandomForest設定オブジェクト
        model: 学習済みRandom Forestモデル
        scaler: 標準化オブジェクト（None可）
        model_path: モデル保存先パス
    """
    ensure_directory_exists(model_path)
    
    # モデルをpickle形式で保存
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Random Forestモデルを {model_path} に保存しました")
    
    # スケーラーを保存（存在する場合のみ）
    if scaler is not None:
        scaler_path = model_path.replace('.sav', '_scaler.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f)
        print(f"スケーラーを {scaler_path} に保存しました")
    else:
        print("スケーラーなし（標準化無効のため保存をスキップ）")


@robust_model_operation("モデル性能評価")
def evaluate_model_performance(config: RandomForestConfig,
                              model: RandomForestRegressor,
                              X_test: np.ndarray,
                              y_test: np.ndarray) -> Tuple[float, float, np.ndarray]:
    """
    モデルの性能を評価する（設定統一版）
    
    Args:
        config: RandomForest設定オブジェクト
        model: 評価対象のRandom Forestモデル
        X_test: テスト用特徴量データ
        y_test: テスト用目的変数データ
        
    Returns:
        Tuple[float, float, np.ndarray]: RMSE, R2スコア, 予測値
    """
    # テストスコア
    test_score = model.score(X_test, y_test)
    print(f'テストスコア: {test_score:.3f}')

    # 予測値の計算
    y_pred = model.predict(X_test).astype(config.data_dtype)
    
    # 性能指標の計算
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    print(f'テストRMSE: {rmse:.2f}')
    print(f'テストR2スコア: {r2:.3f}')
    
    # メモリ最適化
    config.optimize_memory_if_enabled()
    
    return rmse, r2, y_pred


@robust_model_operation("予測結果CSV保存")
def save_predictions_to_csv(config: RandomForestConfig,
                           y_pred: np.ndarray, 
                           output_path: str) -> None:
    """
    予測結果をCSVファイルに保存する（設定統一版）
    
    Args:
        config: RandomForest設定オブジェクト
        y_pred: 予測値配列
        output_path: 保存先ファイルパス
    """
    ensure_directory_exists(output_path)
    
    y_pred_df = pd.DataFrame(y_pred, columns=config.target_columns)
    y_pred_df.to_csv(output_path, index=False)
    
    print(f"予測結果を {output_path} に保存しました")


@robust_model_operation("予測結果グラフ作成")
def create_prediction_plots(config: RandomForestConfig,
                           y_pred: np.ndarray,
                           y_test: np.ndarray,
                           full_period_png: str,
                           week_period_png: str) -> None:
    """
    予測結果のグラフを作成・保存する（設定統一版・16:9アスペクト比）
    
    Args:
        config: RandomForest設定オブジェクト
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
    plt.title('Random Forest Power Prediction (Full)', fontsize=config.font_size_title)
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
    plt.title('Random Forest Power Prediction (1 Week)', fontsize=config.font_size_title)
    plt.legend(fontsize=config.font_size_legend)
    plt.xticks(fontsize=config.font_size_tick)
    plt.yticks(fontsize=config.font_size_tick)
    plt.tight_layout()
    plt.savefig(week_period_png)
    plt.close()
    print(f"1週間グラフを {week_period_png} に保存しました")
    
    # メモリ最適化
    config.optimize_memory_if_enabled()

@robust_model_operation("RandomForest電力需要予測モデル学習")
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
    Random Forestを使用した電力需要予測モデルの学習を実行する（統一仕様版）
    
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
    config = RandomForestConfig()
    
    # 1. データの読み込み
    X_train, X_test, y_train, y_test = load_training_data(
        config, xtrain_csv, xtest_csv, ytrain_csv, ytest_csv
    )
    
    # 2. データの標準化
    X_train_scaled, X_test_scaled, scaler = prepare_data_with_scaling(
        config, X_train, X_test
    )
    
    # 3. モデルの作成
    model = create_random_forest_model(config)
    
    # 4. モデルの学習
    trained_model = train_random_forest_model(config, model, X_train_scaled, y_train)
    
    # 5. モデルとスケーラーの保存
    save_model_and_scaler(config, trained_model, scaler, model_sav)
    
    # 6. モデルの評価
    rmse, r2, y_pred = evaluate_model_performance(config, trained_model, X_test_scaled, y_test)
    
    # 7. 予測結果の保存
    save_predictions_to_csv(config, y_pred, ypred_csv)
    
    # 8. 予測結果グラフの作成
    create_prediction_plots(config, y_pred, y_test, ypred_png, ypred_7d_png)
    
    return rmse, r2


def main() -> None:
    """
    メイン実行関数（統一仕様版）
    
    RandomForestConfigを使用した設定管理で、
    電力需要予測モデルの学習プロセスを実行
    """
    print("="*60)
    print("RandomForest電力需要予測AIモデル学習システム")
    print("統一リファクタリング仕様 - RandomForestConfig対応版")
    print("="*60)
    
    # ファイルパス設定
    xtrain_csv = r"data/Xtrain.csv"
    xtest_csv = r"data/Xtest.csv"
    ytrain_csv = r"data/Ytrain.csv"
    ytest_csv = r"data/Ytest.csv"
    model_sav = r'train/RandomForest/RandomForest_model.sav'
    ypred_csv = r'train/RandomForest/RandomForest_Ypred.csv'
    ypred_png = r'train/RandomForest/RandomForest_Ypred.png'
    ypred_7d_png = r'train/RandomForest/RandomForest_Ypred_7d.png'
    
    # ハイパーパラメータ設定（Random Forestでは使用されないが互換性のため）
    learning_rate = ''
    epochs = ''
    validation_split = ''
    history_png = r'train/RandomForest/RandomForest_history.png'

    try:
        # 学習実行
        result = train(
            xtrain_csv, xtest_csv, ytrain_csv, ytest_csv, model_sav,
            ypred_csv, ypred_png, ypred_7d_png,
            learning_rate, epochs, validation_split, history_png
        )
        
        if result:
            rmse, r2 = result
            print("="*60)
            print(f"🎯 RandomForest学習完了 - RMSE: {rmse:.2f}, R2スコア: {r2:.3f}")
            print("="*60)
        else:
            print("❌ 学習処理が失敗しました")
            
    except Exception as e:
        print(f"❌ メイン処理でエラーが発生しました: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
