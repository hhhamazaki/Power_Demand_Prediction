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
    COLUMN_DTYPES: Dict[str, str] = field(default_factory=lambda: {
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

def _detect_holidays(date_index: pd.DatetimeIndex) -> pd.Series:
    """
    日本の祝日を検出する（簡易版）
    
    Args:
        date_index: 日時インデックス
        
    Returns:
        pd.Series: 祝日フラグ（1: 祝日, 0: 平日）
    """
    # 主要な固定祝日と移動祝日（簡易実装）
    holiday_dates = set()
    
    for year in range(2016, 2026):
        # 固定祝日
        holiday_dates.update([
            f"{year}-01-01",  # 元日
            f"{year}-02-11",  # 建国記念の日
            f"{year}-04-29",  # 昭和の日
            f"{year}-05-03",  # 憲法記念日
            f"{year}-05-04",  # みどりの日
            f"{year}-05-05",  # こどもの日
            f"{year}-08-11",  # 山の日
            f"{year}-11-03",  # 文化の日
            f"{year}-11-23",  # 勤労感謝の日
            f"{year}-12-23",  # 天皇誕生日（2019年以降）
        ])
        
        # 移動祝日（簡易計算）
        # 成人の日（1月第2月曜日）
        jan_mondays = pd.date_range(f"{year}-01-01", f"{year}-01-31", freq='W-MON')
        if len(jan_mondays) >= 2:
            holiday_dates.add(jan_mondays[1].strftime("%Y-%m-%d"))
            
        # 海の日（7月第3月曜日）
        jul_mondays = pd.date_range(f"{year}-07-01", f"{year}-07-31", freq='W-MON')
        if len(jul_mondays) >= 3:
            holiday_dates.add(jul_mondays[2].strftime("%Y-%m-%d"))
            
        # 敬老の日（9月第3月曜日）
        sep_mondays = pd.date_range(f"{year}-09-01", f"{year}-09-30", freq='W-MON')
        if len(sep_mondays) >= 3:
            holiday_dates.add(sep_mondays[2].strftime("%Y-%m-%d"))
            
        # 体育の日/スポーツの日（10月第2月曜日）
        oct_mondays = pd.date_range(f"{year}-10-01", f"{year}-10-31", freq='W-MON')
        if len(oct_mondays) >= 2:
            holiday_dates.add(oct_mondays[1].strftime("%Y-%m-%d"))
    
    # 日付文字列をdatetimeに変換
    holiday_set = {pd.to_datetime(date).date() for date in holiday_dates}
    
    # インデックスの日付と照合
    return pd.Series([1 if date.date() in holiday_set else 0 for date in date_index], index=date_index)

def _detect_long_weekends(date_index: pd.DatetimeIndex, is_holiday: pd.Series) -> pd.Series:
    """
    連休を検出する
    
    Args:
        date_index: 日時インデックス
        is_holiday: 祝日フラグ
        
    Returns:
        pd.Series: 連休フラグ（1: 3日以上の連休期間, 0: 通常）
    """
    # 週末と祝日を統合
    weekday = pd.Series([date.weekday() for date in date_index], index=date_index)
    is_weekend = (weekday >= 5).astype(int)
    is_off = (is_weekend | is_holiday).astype(bool)
    
    # 連続する休日期間を検出
    long_weekend_flags = []
    consecutive_count = 0
    
    for i, is_off_day in enumerate(is_off):
        if is_off_day:
            consecutive_count += 1
        else:
            # 連続期間終了：3日以上なら連休
            if consecutive_count >= 3:
                # 過去の連続期間をすべて連休フラグに設定
                start_idx = max(0, i - consecutive_count)
                for j in range(start_idx, i):
                    if j < len(long_weekend_flags):
                        long_weekend_flags[j] = 1
            consecutive_count = 0
            
        long_weekend_flags.append(0)  # デフォルトは0
    
    # 最後の連続期間をチェック
    if consecutive_count >= 3:
        start_idx = len(long_weekend_flags) - consecutive_count
        for j in range(start_idx, len(long_weekend_flags)):
            long_weekend_flags[j] = 1
    
    return pd.Series(long_weekend_flags, index=date_index)

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

    # 環境変数 'AI_TARGET_YEARS' によるフィルタ（オプション）
    try:
        env_years = os.environ.get('AI_TARGET_YEARS', '')
        if env_years:
            allowed = set([y.strip() for y in env_years.split(',') if y.strip()])
            if allowed:
                power_files = [f for f in power_files if os.path.basename(f)[config.POWER_FILE_YEAR_SLICE] in allowed]
                temp_files = [f for f in temp_files if os.path.basename(f)[config.TEMP_FILE_YEAR_SLICE] in allowed]
                print(f"AI_TARGET_YEARS によりファイルを絞り込み: {sorted(list(allowed))}")
    except Exception:
        # 環境変数の解析に失敗した場合は無視して通常動作を継続
        pass
    
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
        
        # 日時インデックスの作成（効率化版）
        datetime_series = pd.to_datetime(df['DATE'] + ' ' + df['TIME'], format="%Y/%m/%d %H:%M")
        df.index = datetime_series
        
        # 時系列特徴量の生成（CSV結果維持のため元の型を保持）
        df["MONTH"] = df.index.month  # 月情報（1-12）
        df["WEEK"] = df.index.weekday  # 曜日情報（0-6）
        df["HOUR"] = df.index.hour    # 時間情報（0-23）
        
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
        
        # --- 変更点: 基本4次元特徴量のみ使用 ---
        # 元の数値列（MONTH, WEEK, HOUR, TEMP）のみを特徴量として利用
        # 祝日・週末・連休要素は除外し、シンプルな特徴量で予測精度改善
        feature_cols: List[str] = [c for c in config.FEATURE_COLUMNS if c in df.columns]

        # 数値変換（安全に数値化し、欠損があれば行単位で除去する）
        X_df = df[feature_cols].copy()
        # 文字列や混在型があれば数値化（失敗はNaNに）
        X_df = X_df.apply(lambda s: pd.to_numeric(s, errors='coerce'))

        # ターゲットも取得し、特徴量と同じ有効行のみを残す
        y_df = df[config.TARGET_COLUMNS].copy()

        # 行単位で欠損がある場合は削除（特徴量とターゲットの整合性を維持）
        valid_idx = X_df.dropna().index.intersection(y_df.dropna().index)
        X_df = X_df.loc[valid_idx].reset_index(drop=True)
        y_df = y_df.loc[valid_idx].reset_index(drop=True)

        # 最終的な型調整
        X_df = X_df.astype(float)
        # ターゲットは元の型を尊重（整数のままでもKeras側でスケーリングする）
        try:
            y_df = y_df.astype(int)
        except Exception:
            y_df = y_df.apply(lambda s: pd.to_numeric(s, errors='coerce'))
            y_df = y_df.dropna().astype(int)
        
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
    # 注意: X_df の列はダミー列展開により増えている可能性があるため、保存時は元の X_df.columns を使用する
    pd.DataFrame(X_train, columns=X_df.columns).to_csv(Xtrain_csv, index=False)
    pd.DataFrame(X_test, columns=X_df.columns).to_csv(Xtest_csv, index=False)
    pd.DataFrame(y_train, columns=y_df.columns).to_csv(Ytrain_csv, index=False)
    pd.DataFrame(y_test, columns=y_df.columns).to_csv(Ytest_csv, index=False)
    
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

        # ----- 年指定サポート -----
        # 環境変数 'AI_TARGET_YEARS' またはコマンドライン引数で処理対象の年を指定できます。
        # 例: AI_TARGET_YEARS=2019,2020 のようなカンマ区切り文字列
        target_years = None
        # 優先: コマンドライン引数（スクリプト呼び出し時に '2019,2020' を指定）
        if len(sys.argv) > 1 and sys.argv[1].strip():
            target_years = [y.strip() for y in sys.argv[1].split(',') if y.strip()]
            os.environ['AI_TARGET_YEARS'] = ','.join(target_years)
        else:
            env_years = os.environ.get('AI_TARGET_YEARS', '')
            if env_years:
                target_years = [y.strip() for y in env_years.split(',') if y.strip()]

        if target_years:
            print(f"対象年に制限を適用します: {target_years}")
        else:
            print("対象年の制限はありません（検出された全共通年を処理します）")

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
