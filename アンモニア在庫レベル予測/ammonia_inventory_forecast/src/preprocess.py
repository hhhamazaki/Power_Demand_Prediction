"""
前処理モジュール
データ読み込み、欠損処理、補充検出を行う
"""

import pandas as pd
import numpy as np

def load_data(file_path):
    """
    CSVファイルを読み込む
    
    Parameters:
    -----------
    file_path : str
        CSVファイルのパス
        
    Returns:
    --------
    pd.DataFrame
        読み込まれたデータフレーム
    """
    df = pd.read_csv(file_path)
    # 日本時間（JST, UTC+9）を明示的に指定してタイムゾーン対応
    df['date'] = pd.to_datetime(df['date'], utc=True).dt.tz_convert('Asia/Tokyo')
    # 日付のみを保持する場合はタイムゾーンを除去
    if 'date' in df.columns and df['date'].dt.tz is not None:
        df['date'] = df['date'].dt.tz_localize(None)
    df = df.sort_values('date').reset_index(drop=True)
    return df

def handle_missing_values(df, method='interpolate'):
    """
    欠損値を処理
    
    Parameters:
    -----------
    df : pd.DataFrame
        元データフレーム
    method : str
        処理方法 ('interpolate', 'ffill', 'drop')
        
    Returns:
    --------
    pd.DataFrame
        欠損値が処理されたデータフレーム
    """
    df = df.copy()
    
    if method == 'interpolate':
        # 線形補間
        df['actual_power'] = df['actual_power'].interpolate(method='linear')
        df['actual_ammonia'] = df['actual_ammonia'].interpolate(method='linear')
    elif method == 'ffill':
        # 前方埋め
        df['actual_power'] = df['actual_power'].fillna(method='ffill')
        df['actual_ammonia'] = df['actual_ammonia'].fillna(method='ffill')
    elif method == 'drop':
        # 削除
        df = df.dropna(subset=['actual_power', 'actual_ammonia'])
    
    return df

def detect_refill_events(df, ammonia_col='actual_ammonia', threshold=50, 
                         exclude_days_after=3, date_col='date'):
    """
    補充イベントを検出し、フラグを立てる
    
    Parameters:
    -----------
    df : pd.DataFrame
        元データフレーム
    ammonia_col : str
        アンモニア在庫列の名前
    threshold : float
        補充判定の閾値（m³）。この値以上の増加を補充とみなす
    exclude_days_after : int
        補充後、学習から除外する日数
    date_col : str
        日付列の名前
        
    Returns:
    --------
    pd.DataFrame
        補充フラグが追加されたデータフレーム
    """
    df = df.copy()
    df = df.sort_values(date_col).reset_index(drop=True)
    
    # 差分を計算
    df['ammonia_diff'] = df[ammonia_col].diff()
    
    # 補充イベントフラグ（閾値以上の増加）
    df['is_refill'] = (df['ammonia_diff'] >= threshold).astype(int)
    
    # 補充後の除外フラグ
    df['exclude_from_training'] = 0
    
    refill_indices = df[df['is_refill'] == 1].index
    for idx in refill_indices:
        # 補充当日から指定日数後まで除外フラグを立てる
        end_idx = min(idx + exclude_days_after + 1, len(df))
        df.loc[idx:end_idx-1, 'exclude_from_training'] = 1
    
    return df

def remove_outliers(df, cols=['actual_power', 'actual_ammonia'], method='iqr', factor=3):
    """
    外れ値を除去
    
    Parameters:
    -----------
    df : pd.DataFrame
        元データフレーム
    cols : list
        外れ値検出対象の列名リスト
    method : str
        外れ値検出方法 ('iqr', 'zscore')
    factor : float
        外れ値判定の係数
        
    Returns:
    --------
    pd.DataFrame
        外れ値が除去されたデータフレーム
    """
    df = df.copy()
    
    for col in cols:
        if method == 'iqr':
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - factor * IQR
            upper = Q3 + factor * IQR
            df = df[(df[col] >= lower) & (df[col] <= upper)]
        elif method == 'zscore':
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            df = df[z_scores < factor]
    
    return df

def validate_data(df, required_cols=['date', 'actual_power', 'actual_ammonia']):
    """
    データの妥当性を検証
    
    Parameters:
    -----------
    df : pd.DataFrame
        検証対象のデータフレーム
    required_cols : list
        必須列のリスト
        
    Returns:
    --------
    bool
        データが妥当ならTrue、そうでなければFalse
    """
    # 必須列の存在チェック
    for col in required_cols:
        if col not in df.columns:
            print(f"Error: Required column '{col}' is missing.")
            return False
    
    # 負の値チェック
    if (df['actual_power'] < 0).any():
        print("Warning: Negative values found in 'actual_power'.")
    
    if (df['actual_ammonia'] < 0).any():
        print("Warning: Negative values found in 'actual_ammonia'.")
    
    # 日付の連続性チェック
    df_sorted = df.sort_values('date')
    date_diff = df_sorted['date'].diff().dt.days
    if (date_diff[1:] > 1).any():
        print("Warning: Date gaps detected in the data.")
    
    return True

def preprocess_pipeline(file_path, refill_threshold=50, exclude_days_after=3):
    """
    前処理パイプライン全体を実行
    
    Parameters:
    -----------
    file_path : str
        入力CSVファイルのパス
    refill_threshold : float
        補充判定の閾値
    exclude_days_after : int
        補充後の除外日数
        
    Returns:
    --------
    pd.DataFrame
        前処理済みデータフレーム
    """
    # データ読み込み
    df = load_data(file_path)
    print(f"Loaded {len(df)} records from {file_path}")
    
    # データ検証
    if not validate_data(df):
        raise ValueError("Data validation failed.")
    
    # 欠損値処理
    df = handle_missing_values(df, method='interpolate')
    print(f"Missing values handled. Remaining records: {len(df)}")
    
    # 補充イベント検出
    df = detect_refill_events(df, threshold=refill_threshold, 
                              exclude_days_after=exclude_days_after)
    refill_count = df['is_refill'].sum()
    print(f"Detected {refill_count} refill events")
    
    # 外れ値除去（オプション）
    # df = remove_outliers(df)
    
    return df