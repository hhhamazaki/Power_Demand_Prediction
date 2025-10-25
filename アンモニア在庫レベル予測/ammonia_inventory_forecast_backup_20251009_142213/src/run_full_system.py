#!/usr/bin/env python3
"""
アンモニア在庫予測システム - 完全実行スクリプト
学習 → 予測 → ダッシュボード更新を一括実行
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """コマンドを実行して結果を返す"""
    print(f"\n=== {description} ===")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        print(f"[完了] {description} 完了")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[エラー] {description} 失敗")
        if e.stdout:
            print(f"標準出力: {e.stdout}")
        if e.stderr:
            print(f"エラー: {e.stderr}")
        return False
    except Exception as e:
        print(f"[エラー] {description} 失敗")
        print(f"エラー: {e}")
        return False

def main():
    """メイン実行関数"""
    print("=== アンモニア在庫予測システム - 完全実行 ===")
    print("学習 → 予測 → ダッシュボード更新を順次実行します")
    
    # スクリプト位置からプロジェクトルートを決定し cwd を設定（cwd に依存させない）
    script_path = Path(__file__).resolve()
    project_dir = script_path.parent.parent
    os.chdir(project_dir)

    # 実行に使うコマンド（py ランチャーを推奨）
    py_cmd = "py"

    # 1. モデル学習（動的消費量率対応）
    if not run_command(f"{py_cmd} src/train.py", "動的消費量率モデル学習"):
        print("学習に失敗したため、処理を中止します")
        return False
    
    # 2. 予測実行（動的消費量率対応）
    if not run_command(f"{py_cmd} src/predict.py", "動的消費量率予測実行"):
        print("予測に失敗したため、処理を中止します")
        return False
    
    # 3. ダッシュボード更新
    if not run_command(f"{py_cmd} src/update_dashboard.py", "ダッシュボード更新"):
        print("ダッシュボード更新に失敗しましたが、処理を続行します")
    
    print("\n=== 実行完了 ===")
    print("✅ 動的消費量率による学習 → 予測 → ダッシュボード更新が完了しました")
    print("📊 http://localhost:8001/dashboard/index.html でダッシュボードを確認")
    print("📈 data/predictions.csv に予測結果が保存されています（37特徴量・動的消費量率対応）")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)