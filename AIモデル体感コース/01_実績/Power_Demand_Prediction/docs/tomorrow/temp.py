# -*- coding: utf-8 -*-
"""
電力需要予測AIモデル - tomorrow気温データ取得モジュール（最適化版）

Open-Meteo APIから過去・予測気温データを取得し機械学習用特徴量データセットを作成するモジュール。
"""

# 標準ライブラリインポート
import os
import sys
import time
import traceback
import warnings
import logging
import threading
import gc
from typing import List, Tuple, Optional, Dict, Any, Union
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

# サードパーティライブラリインポート
import pandas as pd
import numpy as np
import datetime as dt
import requests
from urllib3.exceptions import InsecureRequestWarning

# システム監視ライブラリインポート（オプション）
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    # logger定義後に警告を出力

# パフォーマンス最適化設定（統合版）
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.simplefilter('ignore', InsecureRequestWarning)
np.set_printoptions(suppress=True, precision=4)

# pandas高速化設定（バージョン互換性対応）
try:
    pd.set_option('mode.copy_on_write', True)
except Exception:
    pass  # 古いバージョンでは無視

# メモリ管理設定（最適化）
gc.set_threshold(700, 10, 10)

# ログ設定（詳細化）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

# psutil利用可否の警告（logger定義後）
if not PSUTIL_AVAILABLE:
    logger.warning("psutil未インストール - メモリ監視機能は無効です")

# 統一設定クラス（統合版）
@dataclass(frozen=True)
class TempConfig:
    """気温データ取得設定クラス（設定値統一管理）"""
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"
    DEFAULT_LATITUDE: str = "35.6785"  # 東京の緯度
    DEFAULT_LONGITUDE: str = "139.6823"  # 東京の経度
    DEFAULT_TIMEZONE: str = "Asia%2FTokyo"
    DEFAULT_PAST_DAYS: int = 7
    DEFAULT_FORECAST_DAYS: int = 7
    REQUIRED_COLUMNS: List[str] = field(default_factory=lambda: ["MONTH", "WEEK", "HOUR", "TEMP"])
    API_TIMEOUT: int = 30  # APIタイムアウト（秒）
    FLOAT_PRECISION: str = "float32"  # メモリ効率化
    MAX_WORKERS: int = 4  # 並列処理ワーカー数
    MEMORY_THRESHOLD_MB: int = 1000  # メモリ使用量監視閾値

# 統一設定インスタンス
config = TempConfig()

# セッション管理（パフォーマンス最適化）
session_lock = threading.Lock()
api_session: Optional[requests.Session] = None

def get_api_session() -> requests.Session:
    """
    APIセッション取得（パフォーマンス最適化）
    
    Returns:
        requests.Session: 最適化されたAPIセッション
    """
    global api_session
    
    with session_lock:
        if api_session is None:
            api_session = requests.Session()
            # HTTPアダプター設定（接続プール最適化）
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=10,
                pool_maxsize=20,
                max_retries=3
            )
            api_session.mount('https://', adapter)
            api_session.mount('http://', adapter)
            
            # デフォルトヘッダー設定
            api_session.headers.update({
                'User-Agent': 'PowerDemandForecast/1.0',
                'Accept': 'application/json',
                'Connection': 'keep-alive'
            })
            
        return api_session

def monitor_memory_usage(func_name: str) -> None:
    """
    メモリ使用量監視
    
    Args:
        func_name: 関数名（ログ用）
    """
    if not PSUTIL_AVAILABLE:
        logger.debug(f"{func_name}: メモリ監視スキップ（psutil未利用）")
        return
        
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    
    if memory_mb > config.MEMORY_THRESHOLD_MB:
        logger.warning(f"{func_name}: メモリ使用量が閾値を超えています: {memory_mb:.1f}MB")
        gc.collect()  # 強制ガベージコレクション
    else:
        logger.debug(f"{func_name}: メモリ使用量: {memory_mb:.1f}MB")

@lru_cache(maxsize=128)
def cached_url_generation(
    latitude: str, 
    longitude: str, 
    timezone: str, 
    past_days: int, 
    forecast_days: int
) -> str:
    """
    APIURLキャッシュ生成（パフォーマンス最適化）
    
    Args:
        latitude: 緯度
        longitude: 経度  
        timezone: タイムゾーン
        past_days: 過去日数
        forecast_days: 予測日数
        
    Returns:
        str: キャッシュされたAPIURL
    """
    return (f"{config.OPEN_METEO_BASE_URL}"
            f"?latitude={latitude}"
            f"&longitude={longitude}"
            f"&hourly=temperature_2m"
            f"&timezone={timezone}"
            f"&past_days={past_days}"
            f"&forecast_days={forecast_days}")

def safe_api_operation(operation: str):
    """
    API操作エラーハンドリングデコレータ
    
    Args:
        operation: 操作名（ログ出力用）
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            monitor_memory_usage(f"{operation}_開始")
            
            try:
                logger.info(f"{operation}開始")
                result = func(*args, **kwargs)
                
                elapsed_time = time.time() - start_time
                monitor_memory_usage(f"{operation}_完了")
                logger.info(f"{operation}完了 (実行時間: {elapsed_time:.3f}秒)")
                return result
            except requests.exceptions.Timeout as e:
                error_msg = f"{operation}失敗 - APIタイムアウト: {e}"
                logger.error(error_msg)
                raise requests.exceptions.Timeout(error_msg)
            except requests.exceptions.ConnectionError as e:
                error_msg = f"{operation}失敗 - 接続エラー: {e}"
                logger.error(error_msg)
                raise requests.exceptions.ConnectionError(error_msg)
            except requests.exceptions.RequestException as e:
                error_msg = f"{operation}失敗 - APIリクエストエラー: {e}"
                logger.error(error_msg)
                raise requests.exceptions.RequestException(error_msg)
            except Exception as e:
                error_msg = f"{operation}失敗 - 予期しないエラー: {e}"
                logger.error(error_msg)
                traceback.print_exc()
                raise
        return wrapper
    return decorator

def generate_api_url(
    latitude: str, 
    longitude: str, 
    timezone: str, 
    past_days: Union[str, int], 
    forecast_days: Union[str, int]
) -> str:
    """
    Open-Meteo APIのURL生成（キャッシュ対応）
    
    Args:
        latitude: 緯度
        longitude: 経度
        timezone: タイムゾーン
        past_days: 過去日数
        forecast_days: 予測日数
        
    Returns:
        str: 生成されたAPIURL
    """
    # キャッシュ関数を使用してパフォーマンス向上
    return cached_url_generation(
        latitude, longitude, timezone, 
        int(past_days), int(forecast_days)
    )

@safe_api_operation("気温データAPI取得")
def fetch_temperature_data(
    latitude: str, 
    longitude: str, 
    timezone: str, 
    past_days: Union[str, int], 
    forecast_days: Union[str, int]
) -> Dict[str, Any]:
    """
    Open-Meteo APIから気温データを取得（セッション最適化版）
    
    Args:
        latitude: 緯度
        longitude: 経度
        timezone: タイムゾーン
        past_days: 過去日数
        forecast_days: 予測日数
        
    Returns:
        Dict[str, Any]: APIレスポンスデータ
        
    Raises:
        requests.exceptions.RequestException: APIリクエストエラー
        ValueError: APIレスポンス検証エラー
    """
    # APIエンドポイントURL生成（キャッシュ利用）
    api_url = generate_api_url(latitude, longitude, timezone, past_days, forecast_days)
    logger.info(f"API Request URL: {api_url}")
    
    # セッション使用による最適化APIリクエスト実行
    session = get_api_session()
    response = session.get(api_url, timeout=config.API_TIMEOUT)
    response.raise_for_status()  # HTTPステータスエラーチェック
    
    # レスポンスデータ取得・検証
    data = response.json()
    
    if 'hourly' not in data:
        raise ValueError("APIレスポンスに'hourly'キーが存在しません")
    
    if 'time' not in data['hourly'] or 'temperature_2m' not in data['hourly']:
        raise ValueError("APIレスポンスに必要なデータ('time', 'temperature_2m')が不足しています")
    
    return data

def create_temperature_dataframe(api_data: Dict[str, Any]) -> pd.DataFrame:
    """
    APIデータから機械学習用気温データフレーム作成（メモリ最適化版）
    
    Args:
        api_data: Open-Meteo APIレスポンスデータ
        
    Returns:
        pd.DataFrame: 時系列特徴量付き気温データ
        
    Raises:
        ValueError: データ変換エラー
    """
    try:
        monitor_memory_usage("DataFrame作成前")
        
        # 基本データフレーム作成（メモリ効率化）
        time_data = api_data['hourly']['time']
        temp_data = api_data['hourly']['temperature_2m']
        
        # 一度に作成して無駄なコピーを避ける
        df = pd.DataFrame({
            'time': pd.to_datetime(time_data),
            'TEMP': pd.array(temp_data, dtype='float64')  # 効率的な配列作成
        })
        
        # NaN値チェック・処理（最適化）
        nan_count = df['TEMP'].isna().sum()
        if nan_count > 0:
            logger.warning(f"気温データにNaN値が{nan_count}個含まれています。補間処理を実行します。")
            df['TEMP'] = df['TEMP'].interpolate(method='linear')
        
        # 時系列特徴量生成（ベクトル化で高速化）
        df['MONTH'] = df['time'].dt.month.astype('int64')
        df['WEEK'] = df['time'].dt.weekday.astype('int64')  
        df['HOUR'] = df['time'].dt.hour.astype('int64')
        df['TEMP'] = df['TEMP'].astype(config.FLOAT_PRECISION)  # メモリ効率化
        
        # 必要なカラムのみ選択（メモリ削減）
        result_df = df[config.REQUIRED_COLUMNS].copy()
        
        # 不要なオブジェクトを即座に削除
        del df
        gc.collect()
        
        monitor_memory_usage("DataFrame作成後")
        logger.info(f"気温データフレーム作成完了: {len(result_df)}行, カラム: {list(result_df.columns)}")
        return result_df
        
    except Exception as e:
        error_msg = f"データフレーム作成エラー: {e}"
        logger.error(error_msg)
        traceback.print_exc()
        raise ValueError(error_msg)

@safe_api_operation("CSV保存")
def save_temperature_csv(df: pd.DataFrame, output_path: str) -> None:
    """
    気温データをCSVファイルに保存（I/O最適化版）
    
    Args:
        df: 保存対象データフレーム
        output_path: 出力ファイルパス
        
    Raises:
        IOError: ファイル保存エラー
    """
    try:
        monitor_memory_usage("CSV保存前")
        
        # ディレクトリ確認・作成
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"ディレクトリ作成: {output_dir}")
        
        # CSVファイル保存（効率的設定）
        df.to_csv(
            output_path, 
            index=False, 
            encoding='utf-8',
            float_format='%.6f',  # 精度指定でファイルサイズ最適化
            chunksize=10000       # 大きなデータでもメモリ効率良く
        )
        
        # 保存確認
        if os.path.exists(output_path):
            file_size_mb = os.path.getsize(output_path) / 1024 / 1024
            logger.info(f"気温データCSV保存完了: {output_path} ({file_size_mb:.2f}MB)")
        else:
            raise IOError(f"CSVファイル保存に失敗しました: {output_path}")
            
        monitor_memory_usage("CSV保存後")
        
    except Exception as e:
        error_msg = f"CSV保存エラー: {e}"
        logger.error(error_msg)
        traceback.print_exc()
        raise IOError(error_msg)

def temp(
    latitude: str, 
    longitude: str, 
    timezone: str, 
    Xtomorrow_csv: str, 
    past_days: Union[str, int], 
    forecast_days: Union[str, int]
) -> Optional[str]:
    """
    気温データ取得・処理メイン関数（パフォーマンス最適化版）
    
    Args:
        latitude: 緯度
        longitude: 経度
        timezone: タイムゾーン
        Xtomorrow_csv: 出力CSVファイルパス
        past_days: 過去データ取得日数
        forecast_days: 予測日数
        
    Returns:
        Optional[str]: エラーが発生した場合はエラーメッセージ、正常終了時はNone
        
    Raises:
        Exception: 気温データ処理に関する各種エラー
    """
    try:
        start_time = time.time()
        monitor_memory_usage("temp関数開始")
        logger.info("気温データ取得処理開始")
        
        # APIから気温データ取得
        api_data = fetch_temperature_data(latitude, longitude, timezone, past_days, forecast_days)
        
        # データフレーム作成
        temperature_df = create_temperature_dataframe(api_data)
        
        # CSV保存
        save_temperature_csv(temperature_df, Xtomorrow_csv)
        
        elapsed_time = time.time() - start_time
        monitor_memory_usage("temp関数完了")
        logger.info(f"気温データ取得処理完了 (実行時間: {elapsed_time:.3f}秒)")
        return None
        
    except Exception as e:
        error_msg = f"気温データ取得処理エラー: {e}"
        logger.error(error_msg)
        traceback.print_exc()
        return error_msg

def main() -> None:
    """
    メイン処理実行（パフォーマンス最適化版）
    """
    # api_sessionはグローバル変数として扱う（代入がある場合はglobals()を使用）
    
    try:
        start_time = time.time()
        
        # メモリ監視（psutil利用可能時のみ）
        if PSUTIL_AVAILABLE:
            process = psutil.Process()
            start_memory = process.memory_info().rss / 1024 / 1024
            logger.info(f"開始時メモリ使用量: {start_memory:.1f}MB")
        
        print("=== tomorrow気温データ取得・処理開始（パフォーマンス最適化版） ===")
        
        # 設定値
        latitude = config.DEFAULT_LATITUDE
        longitude = config.DEFAULT_LONGITUDE
        timezone = config.DEFAULT_TIMEZONE
        output_csv = "tomorrow/tomorrow.csv"
        past_days = config.DEFAULT_PAST_DAYS
        forecast_days = config.DEFAULT_FORECAST_DAYS
        
        # 気温データ取得関数呼び出し
        result = temp(latitude, longitude, timezone, output_csv, past_days, forecast_days)
        
        if result:
            print(f"エラーが発生しました: {result}")
            return
        
        # パフォーマンス統計表示
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print("=== 処理完了 ===")
        print(f"実行時間: {elapsed_time:.3f}秒")
        
        # メモリ統計（psutil利用可能時のみ）
        if PSUTIL_AVAILABLE:
            end_memory = process.memory_info().rss / 1024 / 1024
            memory_delta = end_memory - start_memory
            print(f"メモリ使用量変化: {memory_delta:+.1f}MB (開始: {start_memory:.1f}MB → 終了: {end_memory:.1f}MB)")
        
        print(f"出力ファイル: {output_csv}")
        
        # セッションクリーンアップ
        try:
            # グローバル変数を安全に参照
            if 'api_session' in globals() and globals()['api_session']:
                globals()['api_session'].close()
                globals()['api_session'] = None
        except:
            pass  # セッションが存在しない場合は無視
        
        # 最終ガベージコレクション
        gc.collect()
        
    except Exception as e:
        print(f"メイン処理エラー: {e}")
        traceback.print_exc()
        
        # エラー時もセッションクリーンアップ
        try:
            # グローバル変数を参照するためglobalsを使用
            if 'api_session' in globals() and globals()['api_session']:
                globals()['api_session'].close()
        except:
            pass  # クリーンアップ失敗は無視

# メイン実行部（モジュールとして実行された場合）
if __name__ == "__main__":
    main()
