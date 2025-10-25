#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ダッシュボード更新スクリプト（動的消費量率対応）
predictions.csvの結果をスタンドアロンダッシュボードに反映
予測値ベース次回補充推奨機能付き
"""

import pandas as pd
import json
import os
import sys
from pathlib import Path

# エンコーディング設定（Windows の標準出力に対する安全なラッパー）
import locale
import codecs
try:
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
except Exception:
    # 一部環境では detach() が使用できないためフォールバック
    pass

def update_dashboard():
    """スタンドアロンダッシュボードに最新の予測データを反映"""
    
    print("=== ダッシュボード更新開始（動的消費量率対応） ===")
    
    # スクリプトファイルの場所からプロジェクトルートを決定（cwd に依存させない）
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent

    predictions_path = project_root / 'data' / 'predictions.csv'
    try:
        predictions_df = pd.read_csv(predictions_path)
        print(f"予測データ読み込み: {len(predictions_df)}件（動的消費量率による予測）")
    except FileNotFoundError:
        print(f"エラー: {predictions_path} が見つかりません")
        return False
    
    # データをCSV形式に変換
    csv_lines = ['date,actual_power,actual_ammonia,is_refill,predicted_ammonia,prediction_error,prediction_error_pct']
    
    for _, row in predictions_df.iterrows():
        date_str = row['date']
        actual_power = row.get('actual_power', 0)
        actual_ammonia = row.get('actual_ammonia', '')
        predicted_ammonia = row.get('predicted_ammonia', 0)
        is_refill = row.get('is_refill', 0)
        prediction_error = row.get('prediction_error', '')
        prediction_error_pct = row.get('prediction_error_pct', '')
        
        # actual_ammoniaがNaNの場合は空文字にする
        actual_ammonia_val = actual_ammonia if pd.notna(actual_ammonia) else ''
        prediction_error_val = prediction_error if pd.notna(prediction_error) else ''
        prediction_error_pct_val = prediction_error_pct if pd.notna(prediction_error_pct) else ''
        
        csv_lines.append(f"{date_str},{actual_power},{actual_ammonia_val},{int(is_refill)},{predicted_ammonia},{prediction_error_val},{prediction_error_pct_val}")
    
    csv_data = '\n'.join(csv_lines)
    
    # スタンドアロンダッシュボードを更新（スクリプト位置からの相対パス）
    dashboard_path = project_root / 'dashboard' / 'index_standalone.html'

    if not dashboard_path.exists():
        print(f"エラー: {dashboard_path} が見つかりません")
        return False
    
    try:
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # データ部分を更新
        
        # <script type="text/csv" id="csvData"> ... </script> の部分を置換
        start_marker = '<script type="text/csv" id="csvData">'
        end_marker = '</script>'
        
        start_pos = html_content.find(start_marker)
        if start_pos == -1:
            print("エラー: csvData の開始位置が見つかりません")
            return False
        
        end_pos = html_content.find(end_marker, start_pos)
        if end_pos == -1:
            print("エラー: csvData の終了位置が見つかりません")
            return False
        
        # データ部分を置換
        new_html = (
            html_content[:start_pos] + 
            f"{start_marker}\n{csv_data}\n{end_marker}" +
            html_content[end_pos + len(end_marker):]
        )
        
        # ファイルに書き込み
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(new_html)

        print("ダッシュボード更新完了: " + str(dashboard_path))
        print("   データ件数: " + str(len(predictions_df)) + "件")
        print("   動的消費量率による高精度予測システム対応")
        return True
        
    except Exception as e:
        print(f"エラー: ダッシュボード更新に失敗 - {e}")
        return False

if __name__ == "__main__":
    success = update_dashboard()
    if not success:
        exit(1)
    print("\n動的消費量率対応ダッシュボード更新完了!")