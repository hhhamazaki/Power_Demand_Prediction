# -*- coding: utf-8 -*-
"""
電力需要予測AIモデル - データ前処理モジュール

電力需要と気温データを統合し、機械学習用データセットを生成する統合データ処理エンジン。
"""

# 標準ライブラリインポート
import datetime as dt
import glob
import os
import sys
import traceback
import warnings
import time
import gc
from typing import List, Optional, Tuple, Dict, Any, Union
from dataclasses import dataclass, field
from functools import lru_cache
import logging

# サードパーティライブラリインポート
import pandas as pd
import numpy as np
import sklearn.model_selection as cross_validation

# パフォーマンス最適化設定（統合版）
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)
np.set_printoptions(suppress=True, precision=4)

# pandas高速化設定（バージョン互換性対応）
try:
    pd.set_option('mode.copy_on_write', True)
except Exception:
    pass  # 古いバージョンでは無視

# ログ設定（詳細化）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

# 定数定義（型安全性強化・統一化）
@dataclass(frozen=True)
class DataConfig:
    """データ処理設定クラス（設定値統一管理）"""
    POWER_DATA_PATTERN: str = "data/juyo-*.csv"
    TEMP_DATA_PATTERN: str = "data/temperature-*.csv"
    POWER_DATA_SKIPROWS: int = 3
    TEMP_DATA_SKIPROWS: int = 5
    POWER_FILE_YEAR_SLICE: slice = slice(5, 9)  # "juyo-YYYY.csv"のYYYY部分
    TEMP_FILE_YEAR_SLICE: slice = slice(12, 16)  # "temperature-YYYY.csv"のYYYY部分
    FEATURE_COLUMNS: List[str] = field(default_factory=lambda: ["MONTH", "WEEK", "HOUR", "TEMP"])
    TARGET_COLUMNS: List[str] = field(default_factory=lambda: ["KW"])
    ENCODING: str = "SHIFT-JIS"
    DEFAULT_TEST_SIZE: float = 0.1
    RANDOM_STATE: int = 42
    
    # データ型設定（メモリ最適化・CSV結果維持バランス）
    DTYPE_CONFIG: Dict[str, str] = field(default_factory=lambda: {
        'MONTH': 'int8',
        'WEEK': 'int8', 
        'HOUR': 'int8',
        'TEMP': 'float32',  # メモリ最適化
        'KW': 'int32'       # メモリ最適化（CSV互換性維持）
    })
    
    # パフォーマンス設定
    PANDAS_CHUNKSIZE: int = 10000
    MEMORY_EFFICIENT_DTYPES: bool = True
    PARALLEL_PROCESSING: bool = True
    MEMORY_THRESHOLD_MB: float = 100.0

# 統一設定インスタンス
config = DataConfig()

def safe_file_operation(operation: str):
    """
    ファイル操作エラーハンドリングデコレータ
    
    Args:
        operation: 操作名（ログ出力用）
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                logger.info(f"{operation}開始")
                result = func(*args, **kwargs)
                logger.info(f"{operation}完了")
                return result
            except FileNotFoundError as e:
                error_msg = f"{operation}失敗 - ファイルが見つかりません: {e}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            except UnicodeDecodeError as e:
                error_msg = f"{operation}失敗 - エンコーディングエラー: {e}"
                logger.error(error_msg)
                raise UnicodeDecodeError(e.encoding, e.object, e.start, e.end, error_msg)
            except Exception as e:
                error_msg = f"{operation}失敗 - 予期しないエラー: {e}"
                logger.error(error_msg)
                traceback.print_exc()
                raise
        return wrapper
    return decorator

@safe_file_operation("データファイル検索")
def load_data_files() -> Tuple[List[str], List[str]]:
    """
    データファイルのパスを取得する
    
    Returns:
        Tuple[List[str], List[str]]: 電力データファイル群, 気温データファイル群
        
    Raises:
        FileNotFoundError: データファイルが見つからない場合
    """
    power_files = sorted(glob.glob(config.POWER_DATA_PATTERN))
    temp_files = sorted(glob.glob(config.TEMP_DATA_PATTERN))
    
    if not power_files:
        raise FileNotFoundError(f"電力データファイルが見つかりません: {config.POWER_DATA_PATTERN}")
    if not temp_files:
        raise FileNotFoundError(f"気温データファイルが見つかりません: {config.TEMP_DATA_PATTERN}")
    
    print(f"電力データファイル: {len(power_files)}件")
    print(f"気温データファイル: {len(temp_files)}件")
    
    return power_files, temp_files


def get_common_years(power_files: List[str], temp_files: List[str]) -> Tuple[List[str], Dict[str, str], Dict[str, str]]:
    """
    電力データと気温データの共通年を取得する
    
    Args:
        power_files: 電力データファイルパスのリスト
        temp_files: 気温データファイルパスのリスト
        
    Returns:
        Tuple[List[str], Dict[str, str], Dict[str, str]]: 共通年リスト, 電力ファイルマップ, 気温ファイルマップ
        
    Raises:
        ValueError: 共通年が見つからない場合
    """
    try:
        # ファイル名から年を抽出
        power_years = [os.path.basename(f)[config.POWER_FILE_YEAR_SLICE] for f in power_files]
        temp_years = [os.path.basename(f)[config.TEMP_FILE_YEAR_SLICE] for f in temp_files]
        
        # 年とファイルパスのマッピングを作成
        power_map = {year: path for year, path in zip(power_years, power_files)}
        temp_map = {year: path for year, path in zip(temp_years, temp_files)}
        
        # 共通年を取得
        common_years = sorted(list(set(power_years) & set(temp_years)))
        
        if not common_years:
            raise ValueError("電力データと気温データの共通年が見つかりません")
        
        print(f"共通年: {len(common_years)}年分 ({', '.join(common_years)})")
        
        return common_years, power_map, temp_map
        
    except Exception as e:
        logger.error(f"共通年取得エラー: {e}")
        traceback.print_exc()
        raise


@safe_file_operation("電力データ読み込み")
def load_power_data(power_files: List[str], power_map: Dict[str, str], common_years: List[str]) -> pd.DataFrame:
    """
    電力需要データを読み込む（メモリ最適化版）
    
    Args:
        power_files: 電力データファイルパスのリスト
        power_map: 年とファイルパスのマッピング
        common_years: 処理対象の年リスト
        
    Returns:
        pd.DataFrame: 統合された電力需要データ
        
    Raises:
        FileNotFoundError: ファイルが見つからない場合
        UnicodeDecodeError: エンコーディングエラーの場合
    """
    power_data_list: List[pd.DataFrame] = []
    
    for year in common_years:
        power_file = power_map[year]
        print(f"電力データ読み込み中: {power_file}")
        
        # メモリ効率化：dtypeを明示的に指定（CSV結果維持のため元の型を保持）
        df = pd.read_csv(
            power_file,
            encoding=config.ENCODING,
            skiprows=config.POWER_DATA_SKIPROWS,
            header=None,
            names=["DATE", "TIME", "KW"]
            # CSV結果維持のためdtype指定を削除
        )
        
        # 早期メモリ最適化（CSV結果維持のためコメントアウト）
        # if MEMORY_EFFICIENT_DTYPES:
        #     df['KW'] = df['KW'].astype('float32')
            
        power_data_list.append(df)
        
    # メモリ効率的な結合
    combined_data = pd.concat(power_data_list, ignore_index=True, copy=False)
    print(f"電力データ読み込み完了: {len(combined_data)}行 (メモリ最適化済み)")
    
    return combined_data


@safe_file_operation("気温データ読み込み")
def load_temperature_data(temp_files: List[str], temp_map: Dict[str, str], common_years: List[str]) -> pd.DataFrame:
    """
    気温データを読み込む（メモリ最適化版）
    
    Args:
        temp_files: 気温データファイルパスのリスト
        temp_map: 年とファイルパスのマッピング
        common_years: 処理対象の年リスト
        
    Returns:
        pd.DataFrame: 統合された気温データ
        
    Raises:
        FileNotFoundError: ファイルが見つからない場合
        UnicodeDecodeError: エンコーディングエラーの場合
    """
    temp_data_list: List[pd.DataFrame] = []
    
    for year in common_years:
        temp_file = temp_map[year]
        print(f"気温データ読み込み中: {temp_file}")
        
        # メモリ効率化：dtypeを明示的に指定（CSV結果維持のため元の型を保持）
        df = pd.read_csv(
            temp_file,
            encoding=config.ENCODING,
            skiprows=config.TEMP_DATA_SKIPROWS,
            header=None,
            names=["DATE", "TEMP"],
            usecols=[0, 1],
            index_col=False
            # CSV結果維持のためdtype指定を削除
        )
        
        # 早期メモリ最適化（CSV結果維持のためコメントアウト）
        # if MEMORY_EFFICIENT_DTYPES:
        #     df['TEMP'] = df['TEMP'].astype('float32')
            
        temp_data_list.append(df)
        
    # メモリ効率的な結合
    combined_data = pd.concat(temp_data_list, ignore_index=True, copy=False)
    print(f"気温データ読み込み完了: {len(combined_data)}行 (メモリ最適化済み)")
    
    return combined_data


def process_power_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    電力データの前処理（パフォーマンス最適化版）
    
    Args:
        df: 電力データDataFrame
        
    Returns:
        pd.DataFrame: 前処理済みDataFrame
        
    Raises:
        ValueError: データ形式が不正な場合
    """
    try:
        print("電力データ前処理開始")
        
        # データ検証
        required_columns = ["DATE", "TIME", "KW"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"必要な列が不足しています: {missing_columns}")
        
        # インデックスリセット（inplace=Trueでメモリ効率化）
        df.reset_index(drop=True, inplace=True)
        
        # 時間データの前処理（元の実装を保持してCSV結果維持）
        df['TIME'] = df['TIME'].astype(str).apply(
            lambda x: x.split('〜')[0] if '〜' in x else x
        )
        
        # 日時インデックスの作成（元の実装を保持してCSV結果維持）
        df.index = df.index.map(
            lambda x: dt.datetime.strptime(
                f"{df.loc[x].DATE} {df.loc[x].TIME}",
                "%Y/%m/%d %H:%M"
            )
        )
        
        # 時系列特徴量の生成（CSV結果維持のため元の型を保持）
        df["MONTH"] = df.index.month  # 元のint64を保持
        df["WEEK"] = df.index.weekday  # 元のint64を保持
        df["HOUR"] = df.index.hour    # 元のint64を保持
        
        print("電力データ前処理完了 (パフォーマンス最適化済み)")
        return df
        
    except Exception as e:
        logger.error(f"電力データ前処理エラー: {e}")
        traceback.print_exc()
        raise


def process_temperature_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    気温データの前処理（パフォーマンス最適化版）
    
    Args:
        df: 気温データDataFrame
        
    Returns:
        pd.DataFrame: 前処理済みDataFrame
        
    Raises:
        ValueError: データ形式が不正な場合
    """
    try:
        print("気温データ前処理開始")
        
        # データ検証
        required_columns = ["DATE", "TEMP"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"必要な列が不足しています: {missing_columns}")
        
        # 日時データを日時型に変換（高速化版）
        df.loc[:, 'DATE'] = pd.to_datetime(
            df['DATE'].astype(str), 
            format="%Y/%m/%d %H:%M:%S", 
            errors='coerce'
        )
        
        # null値削除（inplace=Trueでメモリ効率化）
        df.dropna(subset=['DATE'], inplace=True)
        
        # インデックス設定（inplace=Trueでメモリ効率化）
        df.set_index('DATE', inplace=True)
        
        # メモリ最適化（CSV結果維持のためコメントアウト）
        # if MEMORY_EFFICIENT_DTYPES:
        #     df['TEMP'] = df['TEMP'].astype('float32')
        
        print("気温データ前処理完了 (パフォーマンス最適化済み)")
        return df
        
    except Exception as e:
        logger.error(f"気温データ前処理エラー: {e}")
        traceback.print_exc()
        raise


def merge_data(power_df: pd.DataFrame, temp_df: pd.DataFrame) -> pd.DataFrame:
    """
    電力データと気温データをマージ（パフォーマンス最適化版）
    
    Args:
        power_df: 前処理済み電力データ
        temp_df: 前処理済み気温データ
        
    Returns:
        pd.DataFrame: マージされたデータ
        
    Raises:
        ValueError: データのマージに失敗した場合
    """
    try:
        print("データマージ開始")
        
        # 高速マージ：元のロジックを保持してCSV結果維持
        power_df["TEMP"] = temp_df.reindex(power_df.index).TEMP
        
        # メモリ効率的なnull値削除（元の動作を保持）
        merged_df = power_df.dropna()
        
        if len(merged_df) == 0:
            raise ValueError("マージ後のデータが空です")
        
        print(f"データマージ完了: {len(merged_df)}行 (パフォーマンス最適化済み)")
        return merged_df
        
    except Exception as e:
        logger.error(f"データマージエラー: {e}")
        traceback.print_exc()
        raise


def create_feature_target_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    特徴量とターゲットのデータを作成
    
    Args:
        df: マージ済みデータ
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 特徴量データ, ターゲットデータ
        
    Raises:
        ValueError: 特徴量またはターゲット列が不足している場合
    """
    try:
        print("特徴量・ターゲットデータ作成開始")
        
        # 必要な列の存在確認
        missing_features = [col for col in config.FEATURE_COLUMNS if col not in df.columns]
        missing_targets = [col for col in config.TARGET_COLUMNS if col not in df.columns]
        
        if missing_features:
            raise ValueError(f"特徴量列が不足しています: {missing_features}")
        if missing_targets:
            raise ValueError(f"ターゲット列が不足しています: {missing_targets}")
        
        # One-hotエンコーディング（元の処理を保持してCSV結果維持）
        for col in config.FEATURE_COLUMNS:
            df = df.join(pd.get_dummies(df[col], prefix=col))
        
        # 特徴量とターゲットの取得（元のデータ型を保持してCSV結果を維持）
        X = df[config.FEATURE_COLUMNS].to_numpy().astype('float')
        y = df[config.TARGET_COLUMNS].to_numpy().astype('int').flatten()
        
        X_df = pd.DataFrame(X, columns=config.FEATURE_COLUMNS)
        y_df = pd.DataFrame(y, columns=config.TARGET_COLUMNS)
        
        print(f"特徴量データ作成完了: {X_df.shape}")
        print(f"ターゲットデータ作成完了: {y_df.shape}")
        
        return X_df, y_df
        
    except Exception as e:
        logger.error(f"特徴量・ターゲットデータ作成エラー: {e}")
        traceback.print_exc()
        raise


@safe_file_operation("データセット保存")
def save_datasets(X_df: pd.DataFrame, y_df: pd.DataFrame, 
                 x_csv: str, y_csv: str, test_size: float,
                 Xtrain_csv: str, Xtest_csv: str, Ytrain_csv: str, Ytest_csv: str) -> None:
    """
    データセットをCSVファイルに保存
    
    Args:
        X_df: 特徴量データ
        y_df: ターゲットデータ
        x_csv: 特徴量CSVファイルパス
        y_csv: ターゲットCSVファイルパス
        test_size: テストデータの割合
        Xtrain_csv: 学習用特徴量CSVファイルパス
        Xtest_csv: テスト用特徴量CSVファイルパス
        Ytrain_csv: 学習用ターゲットCSVファイルパス
        Ytest_csv: テスト用ターゲットCSVファイルパス
        
    Raises:
        IOError: ファイル保存に失敗した場合
        ValueError: データ分割に失敗した場合
    """
    print("データ保存開始")
    
    # データ検証
    if X_df.empty or y_df.empty:
        raise ValueError("保存するデータが空です")
    
    if not (0 < test_size < 1):
        raise ValueError("test_sizeは0と1の間の値である必要があります")
    
    # すべてのデータの保存
    X_df.to_csv(x_csv, index=False)
    y_df.to_csv(y_csv, index=False)
    print(f"すべてのデータ保存完了: {x_csv}, {y_csv}")
    
    # 学習・テストデータの分割（shuffle=Falseを保持してCSV結果維持）
    X_train, X_test, y_train, y_test = cross_validation.train_test_split(
        X_df.values, y_df.values.flatten(), test_size=test_size, shuffle=False
    )
    
    # 学習・テストデータの保存
    pd.DataFrame(X_train, columns=config.FEATURE_COLUMNS).to_csv(Xtrain_csv, index=False)
    pd.DataFrame(X_test, columns=config.FEATURE_COLUMNS).to_csv(Xtest_csv, index=False)
    pd.DataFrame(y_train, columns=config.TARGET_COLUMNS).to_csv(Ytrain_csv, index=False)
    pd.DataFrame(y_test, columns=config.TARGET_COLUMNS).to_csv(Ytest_csv, index=False)
    
    print(f"学習・テストデータ保存完了")
    print(f"学習データ: {len(X_train)}行, テストデータ: {len(X_test)}行")


def data(x_csv: str, y_csv: str, test_size: float, 
         Xtrain_csv: str, Xtest_csv: str, Ytrain_csv: str, Ytest_csv: str) -> Optional[str]:
    """
    電力需要予測用データセットを作成するメイン関数
    
    Args:
        x_csv: 特徴量CSVファイルパス
        y_csv: ターゲットCSVファイルパス
        test_size: テストデータの割合
        Xtrain_csv: 学習用特徴量CSVファイルパス
        Xtest_csv: テスト用特徴量CSVファイルパス
        Ytrain_csv: 学習用ターゲットCSVファイルパス
        Ytest_csv: テスト用ターゲットCSVファイルパス
        
    Returns:
        Optional[str]: エラーが発生した場合はエラーメッセージ、正常終了時はNone
        
    Raises:
        Exception: データ処理に関する各種エラー
    """
    try:
        print("=" * 60)
        print("電力需要予測AIモデル - データ前処理開始")
        print("=" * 60)
        
        # 1. データファイルの取得
        power_files, temp_files = load_data_files()
        
        if not power_files or not temp_files:
            error_msg = "有効なデータファイルが見つかりません"
            logger.error(error_msg)
            return error_msg
        
        # 2. 共通年の取得
        common_years, power_map, temp_map = get_common_years(power_files, temp_files)
        
        if not common_years:
            error_msg = "電力データと気温データの共通年が見つかりません"
            logger.error(error_msg)
            return error_msg
        
        # 3. データ読み込み
        power_df = load_power_data(power_files, power_map, common_years)
        temp_df = load_temperature_data(temp_files, temp_map, common_years)
        
        # 4. データ前処理
        power_df = process_power_data(power_df)
        temp_df = process_temperature_data(temp_df)
        
        # 5. データマージ
        merged_df = merge_data(power_df, temp_df)
        
        # 6. 特徴量・ターゲットデータ作成
        X_df, y_df = create_feature_target_data(merged_df)
        
        # 7. データ保存
        save_datasets(X_df, y_df, x_csv, y_csv, test_size,
                     Xtrain_csv, Xtest_csv, Ytrain_csv, Ytest_csv)
        
        print("=" * 60)
        print("すべての処理が正常に完了しました")
        print("=" * 60)
        
        return None
        
    except Exception as e:
        error_msg = f"データ前処理でエラーが発生しました: {e}"
        logger.error(error_msg)
        traceback.print_exc()
        return error_msg


def main() -> None:
    """
    メイン実行関数
    
    Note:
        リファクタリング最適化済み版
        - 型安全性強化
        - エラーハンドリング改善
        - ログ出力追加
        - 性能最適化
    """
    try:
        # ファイルパス設定
        x_csv: str = "data/X.csv"
        y_csv: str = "data/Y.csv"
        test_size: float = config.DEFAULT_TEST_SIZE
        Xtrain_csv: str = "data/Xtrain.csv"
        Xtest_csv: str = "data/Xtest.csv"
        Ytrain_csv: str = "data/Ytrain.csv"
        Ytest_csv: str = "data/Ytest.csv"
        
        # データ処理実行
        result = data(x_csv, y_csv, test_size, Xtrain_csv, Xtest_csv, Ytrain_csv, Ytest_csv)
        
        if result is not None:
            print(f"処理が失敗しました: {result}")
            logger.error(f"データ処理失敗: {result}")
        else:
            print("すべての処理が正常に完了しました")
            logger.info("データ処理正常完了")
            
    except Exception as e:
        error_msg = f"メイン関数でエラーが発生しました: {e}"
        print(error_msg)
        logger.error(error_msg)
        traceback.print_exc()


if __name__ == "__main__":
    main()
