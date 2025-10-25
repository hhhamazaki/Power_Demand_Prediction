"""
時系列特徴量生成モジュール
季節性、曜日、休日効果などの特徴量を追加
"""

import pandas as pd
import numpy as np
import holidays

def add_time_features(df, date_col='date'):
    """
    時系列特徴量を追加
    
    Parameters:
    -----------
    df : pd.DataFrame
        元データフレーム
    date_col : str
        日付列の名前
        
    Returns:
    --------
    pd.DataFrame
        特徴量が追加されたデータフレーム
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    
    # 基本的な時系列特徴量
    df['year'] = df[date_col].dt.year
    df['month'] = df[date_col].dt.month
    df['day'] = df[date_col].dt.day
    df['day_of_week'] = df[date_col].dt.dayofweek
    df['day_of_year'] = df[date_col].dt.dayofyear
    df['week_of_year'] = df[date_col].dt.isocalendar().week
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    
    # 日本の祝日判定
    jp_holidays = holidays.Japan(years=df['year'].unique())
    df['is_holiday'] = df[date_col].apply(lambda x: 1 if x in jp_holidays else 0)
    
    # 周期特徴量（sin/cos変換）
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    df['day_of_year_sin'] = np.sin(2 * np.pi * df['day_of_year'] / 365)
    df['day_of_year_cos'] = np.cos(2 * np.pi * df['day_of_year'] / 365)
    df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    
    # 季節フラグ
    df['season'] = df['month'].apply(lambda x: 
        1 if x in [12, 1, 2] else  # 冬
        2 if x in [3, 4, 5] else    # 春
        3 if x in [6, 7, 8] else    # 夏
        4)                           # 秋
    
    return df

def add_lag_features(df, target_cols, lags=[1, 2, 3, 7], date_col='date'):
    """
    ラグ特徴量を追加
    
    Parameters:
    -----------
    df : pd.DataFrame
        元データフレーム
    target_cols : list
        ラグを作成する列名のリスト
    lags : list
        ラグ日数のリスト
    date_col : str
        日付列の名前
        
    Returns:
    --------
    pd.DataFrame
        ラグ特徴量が追加されたデータフレーム
    """
    df = df.copy()
    df = df.sort_values(date_col)
    
    for col in target_cols:
        for lag in lags:
            df[f'{col}_lag{lag}'] = df[col].shift(lag)
    
    return df

def add_rolling_features(df, target_cols, windows=[7, 14, 30], date_col='date'):
    """
    移動平均・移動分散特徴量を追加
    
    Parameters:
    -----------
    df : pd.DataFrame
        元データフレーム
    target_cols : list
        移動統計量を作成する列名のリスト
    windows : list
        ウィンドウサイズのリスト
    date_col : str
        日付列の名前
        
    Returns:
    --------
    pd.DataFrame
        移動統計量が追加されたデータフレーム
    """
    df = df.copy()
    df = df.sort_values(date_col)
    
    for col in target_cols:
        for window in windows:
            # 移動平均
            df[f'{col}_ma{window}'] = df[col].rolling(window=window, min_periods=1).mean()
            # 移動標準偏差
            df[f'{col}_std{window}'] = df[col].rolling(window=window, min_periods=1).std()
            # 移動最大値
            df[f'{col}_max{window}'] = df[col].rolling(window=window, min_periods=1).max()
            # 移動最小値
            df[f'{col}_min{window}'] = df[col].rolling(window=window, min_periods=1).min()
    
    return df

def add_diff_features(df, target_cols, periods=[1, 7], date_col='date'):
    """
    差分特徴量を追加
    
    Parameters:
    -----------
    df : pd.DataFrame
        元データフレーム
    target_cols : list
        差分を作成する列名のリスト
    periods : list
        差分期間のリスト
    date_col : str
        日付列の名前
        
    Returns:
    --------
    pd.DataFrame
        差分特徴量が追加されたデータフレーム
    """
    df = df.copy()
    df = df.sort_values(date_col)
    
    for col in target_cols:
        for period in periods:
            df[f'{col}_diff{period}'] = df[col].diff(period)
    
    return df

def create_all_features(df, date_col='date', target_cols=['actual_power', 'actual_ammonia']):
    """
    すべての特徴量を一括生成
    
    Parameters:
    -----------
    df : pd.DataFrame
        元データフレーム
    date_col : str
        日付列の名前
    target_cols : list
        特徴量を作成する対象列のリスト
        
    Returns:
    --------
    pd.DataFrame
        全特徴量が追加されたデータフレーム
    """
    df = add_time_features(df, date_col)
    df = add_lag_features(df, target_cols, lags=[1, 2, 3, 7], date_col=date_col)
    df = add_rolling_features(df, target_cols, windows=[7, 14], date_col=date_col)
    df = add_diff_features(df, target_cols, periods=[1, 7], date_col=date_col)
    
    return df