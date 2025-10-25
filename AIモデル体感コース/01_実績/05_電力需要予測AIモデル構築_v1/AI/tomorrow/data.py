# -*- coding: utf-8 -*-
"""
電力需要予測AIモデル - tomorrow予測データ取得モジュール

TEPCOから最新の電力需要を取得し、予測用データセットを作成するモジュール。
"""

# 標準ライブラリインポート
import os
import sys
import traceback
import warnings
import logging
import gc
from typing import Optional, List, Dict, Any, Tuple, Union
from functools import lru_cache
from dataclasses import dataclass, field
import time

# サードパーティライブラリインポート
import pandas as pd
import numpy as np
import datetime as dt
import urllib.request
import zipfile
import io
import requests
from urllib3.exceptions import InsecureRequestWarning
try:
    import psutil
except Exception:
    psutil = None

# パフォーマンス最適化設定（統合版）
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)
warnings.simplefilter('ignore', InsecureRequestWarning)
np.set_printoptions(suppress=True, precision=4)

# pandas高速化設定（バージョン互換性対応）
try:
    pd.set_option('mode.copy_on_write', True)
except Exception:
    pass  # 古いバージョンでは無視
    
try:
    pd.set_option('future.no_silent_downcasting', True)
except Exception:
    pass  # 対応していないバージョンでは無視

# ログ設定（詳細化）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

# 統一定数の削除（configクラスに統合）
# ENCODING: str = "SHIFT-JIS"
# EXPECTED_HEADER: List[str] = ["DATE", "TIME", "KW"]
# JAPANESE_HEADER: str = "DATE,TIME,実績(万kW)"
# ZIP_SKIPROWS: int = 14
# ZIP_NROWS: int = 24
# ZIP_USECOLS: List[int] = [0, 1, 2]
# CSV_SKIPROWS: int = 3
# DEFAULT_PAST_DAYS: int = 7
# DEFAULT_FORECAST_DAYS: int = 7
# CHUNK_SIZE: int = 10000
# MAX_RETRIES: int = 3
# REQUEST_TIMEOUT: int = 30
# MEMORY_THRESHOLD_MB: float = 100.0
# TEPCO_URL_TEMPLATE: str = "https://www.tepco.co.jp/forecast/html/images/{year:04d}{month:02d}_power_usage.zip"
# OPTIMIZED_DTYPES: Dict[str, str] = {...}

@lru_cache(maxsize=128)
def get_current_datetime_info() -> Tuple[int, int, str]:
    """
    現在の日時情報を取得（キャッシュ最適化）
    
    Returns:
        Tuple[int, int, str]: 年, 月, フォーマット済み日時文字列
    """
    current_time = dt.datetime.now()
    formatted_datetime = f"{current_time.year}/{current_time.month}/{current_time.day} {current_time.hour}:{current_time.minute:02d} UPDATE"
    return current_time.year, current_time.month, formatted_datetime

@lru_cache(maxsize=128)
def generate_file_url(year: int, month: int) -> str:
    """
    TEPCOデータファイルURL生成（キャッシュ最適化）
    
    Args:
        year: 対象年
        month: 対象月
        
    Returns:
        str: 生成されたURL
    """
    return config.TEPCO_URL_TEMPLATE.format(year=year, month=month)

@lru_cache(maxsize=128)
def generate_target_path(year: int) -> str:
    """
    対象ファイルパス生成（キャッシュ最適化）
    
    Args:
        year: 対象年
        
    Returns:
        str: 生成されたファイルパス
    """
    return f"data/juyo-{year}.csv"

def monitor_memory_usage(func):
    """
    メモリ使用量監視デコレータ（最適化版）
    """
    def wrapper(*args, **kwargs):
        # psutilが利用可能ならメモリ差分をログ出力、それ以外は通常実行
        if psutil is None:
            return func(*args, **kwargs)
        try:
            process = psutil.Process()
            mem_before = process.memory_info().rss / 1024 / 1024  # MB

            result = func(*args, **kwargs)

            mem_after = process.memory_info().rss / 1024 / 1024  # MB
            mem_diff = mem_after - mem_before

            if abs(mem_diff) > config.MEMORY_THRESHOLD_MB:
                logger.info(f"{func.__name__} メモリ使用量変化: {mem_diff:.2f}MB")

            return result
        except Exception:
            # psutil呼び出しで不具合が出た場合はフォールバック実行
            return func(*args, **kwargs)
    return wrapper

# 統一設定クラス（統合版）
@dataclass(frozen=True)
class TomorrowDataConfig:
    """tomorrow予測データ取得設定クラス（設定値統一管理）"""
    ENCODING: str = "SHIFT-JIS"
    EXPECTED_HEADER: List[str] = field(default_factory=lambda: ["DATE", "TIME", "KW"])
    JAPANESE_HEADER: str = "DATE,TIME,実績(万kW)"
    ZIP_SKIPROWS: int = 14
    ZIP_NROWS: int = 24
    ZIP_USECOLS: List[int] = field(default_factory=lambda: [0, 1, 2])
    CSV_SKIPROWS: int = 3
    DEFAULT_PAST_DAYS: int = 7
    DEFAULT_FORECAST_DAYS: int = 7
    
    # パフォーマンス最適化定数
    CHUNK_SIZE: int = 10000
    MAX_RETRIES: int = 3
    REQUEST_TIMEOUT: int = 30
    MEMORY_THRESHOLD_MB: float = 100.0
    
    # URL設定
    TEPCO_URL_TEMPLATE: str = "https://www.tepco.co.jp/forecast/html/images/{year:04d}{month:02d}_power_usage.zip"
    
    # データ型最適化マッピング
    OPTIMIZED_DTYPES: Dict[str, str] = field(default_factory=lambda: {
        'DATE': 'object',
        'TIME': 'object', 
        'KW': 'int32',  # メモリ効率化
        'MONTH': 'int8',
        'WEEK': 'int8',
        'HOUR': 'int8'
    })

# 統一設定インスタンス
config = TomorrowDataConfig()

def safe_file_operation(operation: str):
    """
    ファイル操作エラーハンドリングデコレータ（強化版）
    
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
            except pd.errors.EmptyDataError as e:
                error_msg = f"{operation}失敗 - 空データエラー: {e}"
                logger.error(error_msg)
                raise pd.errors.EmptyDataError(error_msg)
            except Exception as e:
                error_msg = f"{operation}失敗 - 予期しないエラー: {e}"
                logger.error(error_msg)
                traceback.print_exc()
                raise
        return wrapper
    return decorator

def get_current_datetime_info() -> Tuple[int, int, str]:
    """
    現在の日時情報を取得（重複関数統合）
    
    Returns:
        Tuple[int, int, str]: 年, 月, フォーマット済み日時文字列
    """
    current_time = dt.datetime.now()
    formatted_datetime = f"{current_time.year}/{current_time.month}/{current_time.day} {current_time.hour}:{current_time.minute:02d} UPDATE"
    return current_time.year, current_time.month, formatted_datetime

def generate_file_url(year: int, month: int) -> str:
    """
    TEPCOデータファイルURLを生成（重複関数統合）
    
    Args:
        year: 対象年
        month: 対象月
        
    Returns:
        str: 生成されたURL
    """
    return config.TEPCO_URL_TEMPLATE.format(year=year, month=month)

def generate_target_path(year: int) -> str:
    """
    対象ファイルパスを生成（重複関数統合）
    
    Args:
        year: 対象年
        
    Returns:
        str: 生成されたファイルパス
    """
    return f"data/juyo-{year}.csv"

@safe_file_operation("既存データ読み込み")
@monitor_memory_usage
def load_existing_data(file_path: str) -> Tuple[pd.DataFrame, List[str], str]:
    """
    既存データファイルを読み込む（最適化版）
    
    Args:
        file_path: ファイルパス
        
    Returns:
        Tuple[pd.DataFrame, List[str], str]: データフレーム, メタデータ行, 日本語ヘッダー
        
    Raises:
        FileNotFoundError: ファイルが見つからない場合
        UnicodeDecodeError: エンコーディングエラーの場合
    """
    metadata_lines: List[str] = []
    japanese_header: str = ""
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"ファイルが存在しません: {file_path}")
    
    # メタデータとヘッダーの効率的読み込み
    with open(file_path, 'r', encoding=config.ENCODING, buffering=8192) as f:
        metadata_lines.append(f.readline().rstrip('\r\n'))  # Line 1
        metadata_lines.append(f.readline().rstrip('\r\n'))  # Line 2
        japanese_header = f.readline().rstrip('\r\n')       # Line 3
    
    # 最適化されたデータ読み込み
    df = pd.read_csv(
        file_path, 
        encoding=config.ENCODING, 
        skiprows=config.CSV_SKIPROWS, 
        header=None, 
        names=config.EXPECTED_HEADER,
        dtype={'DATE': 'object', 'TIME': 'object', 'KW': 'int32'},
        engine='c',  # C エンジン使用（高速化）
        low_memory=False
    )
    
    logger.info(f"既存データ読み込み完了: {file_path} ({len(df):,}行)")
    return df, metadata_lines, japanese_header

@monitor_memory_usage
def create_new_file_with_headers(file_path: str) -> Tuple[pd.DataFrame, List[str], str]:
    """
    新規ファイルをヘッダー付きで作成（最適化版）
    
    Args:
        file_path: ファイルパス
        
    Returns:
        Tuple[pd.DataFrame, List[str], str]: 空のデータフレーム, メタデータ行, 日本語ヘッダー
        
    Raises:
        IOError: ファイル作成に失敗した場合
    """
    try:
        # ディレクトリ作成
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # メタデータ作成
        _, _, formatted_datetime = get_current_datetime_info()
        metadata_lines = [formatted_datetime, ""]  # Empty second line
        japanese_header = config.JAPANESE_HEADER
        
        # ファイル作成（バッファリング最適化）
        with open(file_path, 'w', encoding=config.ENCODING, buffering=8192) as f:
            for line in metadata_lines:
                f.write(line + '\n')
            f.write(japanese_header + '\n')
        
        # 最適化されたデータ型でDataFrame作成
        empty_df = pd.DataFrame(columns=config.EXPECTED_HEADER)
        for col in config.EXPECTED_HEADER:
            if col in config.OPTIMIZED_DTYPES:
                empty_df[col] = empty_df[col].astype(config.OPTIMIZED_DTYPES[col])
        
        logger.info(f"新規ファイル作成完了: {file_path}")
        
        return empty_df, metadata_lines, japanese_header
        
    except Exception as e:
        error_msg = f"新規ファイル作成エラー: {file_path}, {e}"
        logger.error(error_msg)
        raise IOError(error_msg)

@monitor_memory_usage
def data(Ytest_csv: str, past_days: Union[str, int], forecast_days: Union[str, int]) -> Optional[str]:
    """
    tomorrow予測用データセットを作成するメイン関数（パフォーマンス最適化版）
    
    Args:
        Ytest_csv: 出力CSVファイルパス
        past_days: 過去データ取得日数
        forecast_days: 予測日数
        
    Returns:
        Optional[str]: エラーが発生した場合はエラーメッセージ、正常終了時はNone
        
    Raises:
        Exception: データ処理に関する各種エラー
    """
    try:
        logger.info("tomorrow予測データ取得開始")
        
        # 型変換・バリデーション
        past_days_int = int(past_days) if isinstance(past_days, str) else past_days
        forecast_days_int = int(forecast_days) if isinstance(forecast_days, str) else forecast_days
        
        if past_days_int <= 0 or forecast_days_int <= 0:
            raise ValueError("past_days と forecast_days は正の整数である必要があります")
        
        # 現在日時情報取得
        current_year, current_month, _ = get_current_datetime_info()

        # 試行する (year, month) の候補リストを作成
        # 優先: 当月 -> 前月（前月が前年に跨る場合は前年の12月）
        candidates = [(current_year, current_month)]
        if current_month == 1:
            candidates.append((current_year - 1, 12))
        else:
            candidates.append((current_year, current_month - 1))

        # 成功した月の結果を全て収集 -> 最終的に結合してデータセット作成を行う
        latest_dfs_list: List[pd.DataFrame] = []

        for year_try, month_try in candidates:
            zip_file_url = generate_file_url(year_try, month_try)
            juyo_target_path = generate_target_path(year_try)

            logger.info(f"試行対象URL: {zip_file_url}")
            logger.info(f"試行対象ファイル: {juyo_target_path}")

            # 既存データ読み込み or 新規作成
            try:
                existing_df, original_metadata_lines, original_japanese_header_line = load_existing_data(juyo_target_path)
            except FileNotFoundError:
                logger.info(f"ファイル {juyo_target_path} が存在しません。新規作成します。")
                existing_df = pd.DataFrame(columns=config.EXPECTED_HEADER)
                original_metadata_lines = []
                original_japanese_header_line = config.JAPANESE_HEADER

            # 最新データ取得とマージ処理（成功ならリストに追加）
            month_df = download_and_extract_latest_data(
                zip_file_url, existing_df, original_metadata_lines, 
                original_japanese_header_line, juyo_target_path
            )

            if month_df is not None:
                latest_dfs_list.append(month_df)
        
        if not latest_dfs_list:
            error_msg = "最新データ取得に失敗しました（当月・前月ともに取得不可）"
            logger.error(error_msg)
            return error_msg

        # 取得成功した月を全て結合（年を跨ぐ可能性あり）
        latest_df = pd.concat(latest_dfs_list, ignore_index=True)
        
        # tomorrow予測データセット作成
        result_message = create_tomorrow_prediction_dataset(
            latest_df, Ytest_csv, str(past_days_int), str(forecast_days_int)
        )
        
        if result_message:
            logger.error(f"tomorrow予測データセット作成エラー: {result_message}")
            return result_message
        
        # メモリクリーンアップ
        del latest_df, existing_df
        gc.collect()
        
        logger.info("tomorrow予測データ取得完了")
        return None
        
    except Exception as e:
        error_msg = f"tomorrow予測データ取得エラー: {e}"
        logger.error(error_msg)
        traceback.print_exc()
        return error_msg

@safe_file_operation("最新データダウンロード・展開")
@monitor_memory_usage
def download_and_extract_latest_data(
    zip_file_url: str, 
    existing_df: pd.DataFrame, 
    original_metadata_lines: List[str], 
    original_japanese_header_line: str, 
    juyo_target_path: str
) -> Optional[pd.DataFrame]:
    """
    最新データをダウンロード・展開し、既存データとマージ
    
    Args:
        zip_file_url: ZIPファイルURL
        existing_df: 既存データフレーム
        original_metadata_lines: 元のメタデータ行
        original_japanese_header_line: 元の日本語ヘッダー行
        juyo_target_path: 出力ファイルパス
        
    Returns:
        Optional[pd.DataFrame]: マージ済みデータフレーム、失敗時はNone
        
    Raises:
        Exception: ダウンロード・展開・マージ処理エラー
    """
    # 最新データダウンロード・展開
    new_data_dfs: List[pd.DataFrame] = []
    
    try:
        # 効率的HTTPリクエスト（セッション使用）
        session = requests.Session()
        session.verify = False
        
        response = session.get(zip_file_url, timeout=config.REQUEST_TIMEOUT, stream=True)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            csv_files_in_zip = sorted([name for name in z.namelist() if name.endswith('.csv')])

            for filename in csv_files_in_zip:
                with z.open(filename) as csv_file:
                    # 最適化されたCSV読み込み
                    df_to_append = pd.read_csv(
                        csv_file, 
                        encoding=config.ENCODING, 
                        header=None, 
                        skiprows=config.ZIP_SKIPROWS, 
                        nrows=config.ZIP_NROWS, 
                        usecols=config.ZIP_USECOLS,
                        dtype={'0': 'object', '1': 'object', '2': 'int32'},
                        engine='c'  # C エンジン使用（高速化）
                    )
                    df_to_append.columns = config.EXPECTED_HEADER  # 英語ヘッダー割り当て
                    
                    # 効率的文字列処理
                    str_cols = df_to_append.select_dtypes(include=['object']).columns
                    for col in str_cols:
                        df_to_append[col] = df_to_append[col].astype('string').str.replace('\r', '', regex=False)
                    
                    new_data_dfs.append(df_to_append)
        
        session.close()
        logger.info(f"ZIPファイルダウンロード・処理完了: {zip_file_url}")

    except requests.exceptions.RequestException as e:
        logger.error(f"ZIPファイルダウンロードエラー: {zip_file_url}, {e}")
        return None
        print(f"ZIPファイル形式エラー: {e}")
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"ZIP処理中の予期しないエラー: {e}")
        traceback.print_exc()
        return None

    # 既存データと新規データをマージ
    if new_data_dfs:
        combined_df = pd.concat([existing_df] + new_data_dfs, ignore_index=True)
    else:
        combined_df = existing_df

    # TIMEカラム処理（開始時刻のみ取得）
    if 'TIME' in combined_df.columns:
        combined_df['TIME'] = combined_df['TIME'].astype(str).apply(lambda x: x.split('〜')[0] if '〜' in x else x)
    else:
        print("警告: 'TIME'カラムが見つかりません。時刻処理をスキップします。")

    # DATE・TIMEによる重複除去
    if 'DATE' in combined_df.columns and 'TIME' in combined_df.columns:
        combined_df.drop_duplicates(subset=['DATE', 'TIME'], inplace=True)
    else:
        print("警告: 'DATE'または'TIME'カラムが見つかりません。重複除去をスキップします。")

    # 全カラムの改行文字除去
    for col in combined_df.columns:
        combined_df[col] = combined_df[col].astype(str).str.replace('\r', '')

    # クリーンアップしたデータをCSVに保存
    try:
        # データフレームを文字列バッファに書き込み
        data_buffer = io.StringIO()
        combined_df.to_csv(data_buffer, header=False, index=False, encoding=config.ENCODING, lineterminator='\n')
        data_content = data_buffer.getvalue()
        # 改行文字の正規化
        data_content = data_content.replace('\r\n', '\n')

        with open(juyo_target_path, 'wb') as f:  # バイナリ書き込みモード
            for line in original_metadata_lines:
                f.write(line.encode(config.ENCODING) + b'\n')
            f.write(original_japanese_header_line.encode(config.ENCODING) + b'\n')
            f.write(data_content.encode(config.ENCODING))  # データコンテンツ書き込み

        print(f"データ更新・重複除去完了: {juyo_target_path}")
        return combined_df
        
    except Exception as e:
        print(f"データ書き込みエラー: {juyo_target_path}, {e}")
        traceback.print_exc()
        return None

@safe_file_operation("tomorrow予測データセット作成")
def create_tomorrow_prediction_dataset(
    combined_df: pd.DataFrame, 
    Ytest_csv: str, 
    past_days: str, 
    forecast_days: str
) -> Optional[str]:
    """
    tomorrow予測用データセットを作成
    
    Args:
        combined_df: マージ済みデータフレーム
        Ytest_csv: 出力CSVファイルパス
        past_days: 過去データ取得日数
        forecast_days: 予測日数
        
    Returns:
        Optional[str]: エラーメッセージ、正常終了時はNone
        
    Raises:
        Exception: データセット作成エラー
    """
    try:
        # メインデータ処理
        data_files = [generate_target_path(dt.datetime.now().year)]
        data_dfs: List[pd.DataFrame] = []
        
        for data_file in data_files:
            # 4行目以降からデータ読み込み、英語ヘッダー割り当て
            data_df = pd.read_csv(
                data_file, 
                encoding=config.ENCODING, 
                skiprows=config.CSV_SKIPROWS, 
                header=None, 
                names=config.EXPECTED_HEADER
            )
            data_dfs.append(data_df)

        df = pd.concat(data_dfs)
        
        # TIMEカラム処理（開始時刻のみ取得）
        df['TIME'] = df['TIME'].astype(str).apply(lambda x: x.split('〜')[0] if '〜' in x else x)

        # DATE・TIME結合
        df['DATETIME_COMBINED'] = df['DATE'].astype(str) + " " + df['TIME'].astype(str)

        # 日時変換（エラー強制変換）
        df['DATETIME_COMBINED'] = pd.to_datetime(
            df['DATETIME_COMBINED'], 
            format="%Y/%m/%d %H:%M", 
            errors='coerce'
        )

        # 日時変換失敗行の除去
        df.dropna(subset=['DATETIME_COMBINED'], inplace=True)

        # 日時カラムをインデックスに設定
        df.set_index('DATETIME_COMBINED', inplace=True)

        # 時系列特徴量追加
        df["MONTH"] = df.index.month
        df["WEEK"] = df.index.weekday
        df["HOUR"] = df.index.hour

        df_kw = df

        # 温度データの読み込み・処理
        return process_temperature_and_create_dataset(df_kw, Ytest_csv, past_days, forecast_days)
        
    except Exception as e:
        error_msg = f"tomorrow予測データセット作成エラー: {e}"
        logger.error(error_msg)
        traceback.print_exc()
        return error_msg

@safe_file_operation("温度データ処理・データセット作成")
def process_temperature_and_create_dataset(
    df_kw: pd.DataFrame, 
    Ytest_csv: str, 
    past_days: str, 
    forecast_days: str
) -> Optional[str]:
    """
    温度データを処理し、最終的なデータセットを作成
    
    Args:
        df_kw: 電力データフレーム
        Ytest_csv: 出力CSVファイルパス
        past_days: 過去データ取得日数
        forecast_days: 予測日数
        
    Returns:
        Optional[str]: エラーメッセージ、正常終了時はNone
        
    Raises:
        Exception: 温度データ処理・データセット作成エラー
    """
    try:

        # 最新日付取得（今日の日付）
        latest_date = dt.datetime.now().date()
        latest_date = pd.Timestamp(latest_date)
        print(f"最新日付: {latest_date}")

        # 過去指定日数のデータ抽出
        start_date = dt.datetime.combine(latest_date, dt.time(0, 0)) - pd.Timedelta(days=int(past_days))
        df_kw = df_kw[(df_kw.index >= start_date) & (df_kw.index <= latest_date)]
        print(f"開始日付: {start_date}")

        # 欠損値除去
        df_kw = df_kw.dropna()
        
        # 目的変数カラム
        y_cols = ["KW"]
        y = df_kw[y_cols].to_numpy().astype('int').flatten()

        # 予測日数を整数に変換
        forecast_days_int = int(forecast_days)
        print(f"予測日数: {forecast_days_int}")

        # DataFrameに変換してCSV保存
        y_csv = pd.DataFrame(y, columns=y_cols)
        y_csv.to_csv(Ytest_csv, index=False)
        
        print(f"tomorrow予測データセット作成完了: {Ytest_csv} ({len(y_csv)}行)")
        return None
        
    except Exception as e:
        error_msg = f"温度データ処理・データセット作成エラー: {e}"
        logger.error(error_msg)
        error = traceback.format_exc()
        return error

def main() -> None:
    """
    メイン関数（統一パターン）
    
    tomorrow予測用データ取得・処理のメイン実行関数
    リファクタリング最適化済み版
    - 型安全性強化
    - エラーハンドリング改善
    - パフォーマンス最適化
    - ログ出力追加
    """
    start_time = time.time()
    
    try:
        print("=== tomorrow予測データ取得開始 ===")
        logger.info("tomorrow予測データ取得開始")
        
        # ファイルパス設定
        Ytest_csv = r"tomorrow/Ytest.csv"
        past_days = '7'
        forecast_days = '7'

        # データ関数呼び出し
        result = data(Ytest_csv, past_days, forecast_days)
        
        if result:
            print(f"エラーが発生しました: {result}")
            logger.error(f"tomorrow予測データ取得エラー: {result}")
            raise RuntimeError(f"データ取得エラー: {result}")
        
        # メモリクリーンアップ
        gc.collect()
        
        # 実行時間表示
        elapsed_time = time.time() - start_time
        print(f"=== tomorrow予測データ取得完了 (実行時間: {elapsed_time:.2f}秒) ===")
        logger.info(f"tomorrow予測データ取得正常完了 (実行時間: {elapsed_time:.2f}秒)")
        
    except Exception as e:
        error_msg = f"メイン関数エラー: {e}"
        print(error_msg)
        logger.error(error_msg)
        traceback.print_exc()
        raise


# メイン実行部（モジュールとして実行された場合）
if __name__ == "__main__":
    main()

