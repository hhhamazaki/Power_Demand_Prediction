# -*- coding: utf-8 -*-

"""
電力需要予測AIモデル - PyCaret学習年組み合わせ最適化

複数年の組み合わせでPyCaretモデル学習を実行し、最適な年選択を自動決定する。
学習年の組み合わせ手法を実装し、最適な組み合わせ年を検証する。

時系列交差検証（ローリング方式）により各組み合わせ性能を評価。
"""

import os
import sys
import subprocess
import json
import time
from typing import List, Tuple, Dict, Any
import pandas as pd
from dataclasses import dataclass
import numpy as np
from datetime import datetime
import glob
import re

# 設定
@dataclass
class OptimizationConfig:
    """学習年最適化設定"""
    TARGET_MODEL: str = "Pycaret"
    PYTHON_PATH: str = "py"
    PYTHON_VERSION: str = "-3.10"
    RESULTS_FILE: str = "year_optimization_results.json"

# グローバル設定
config = OptimizationConfig()

def get_available_years() -> List[str]:
    """利用可能な年を取得"""
    # スクリプトのディレクトリから相対パスでdataフォルダを探す
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "..", "data")
    data_dir = os.path.abspath(data_dir)
    
    power_pattern = os.path.join(data_dir, "juyo-*.csv")
    temp_pattern = os.path.join(data_dir, "temperature-*.csv")
    
    power_files = sorted(glob.glob(power_pattern))
    temp_files = sorted(glob.glob(temp_pattern))
    
    print(f"データフォルダ: {data_dir}")
    print(f"電力ファイル検索: {power_pattern}")
    print(f"電力ファイル数: {len(power_files)}")
    print(f"気温ファイル数: {len(temp_files)}")
    
    power_years = [os.path.basename(f)[5:9] for f in power_files if len(os.path.basename(f)) >= 9]
    temp_years = [os.path.basename(f)[12:16] for f in temp_files if len(os.path.basename(f)) >= 16]
    
    # 共通年のみ返す
    common_years = sorted(list(set(power_years) & set(temp_years)))
    
    # 現在年まで自動拡張
    current_year = datetime.now().year
    if common_years:
        max_available_year = max([int(y) for y in common_years if y.isdigit()])
        
        if max_available_year < current_year:
            print(f"警告: 最新データ年{max_available_year}、現在年{current_year}まで不足")
    
    return common_years

class YearCombinationOptimizer:
    """年組み合わせ最適化クラス"""
    
    def __init__(self, available_years: List[int] = None):
        """
        初期化
        
        Args:
            available_years: 利用可能な年リスト（デフォルト: 自動検出）
        """
        if available_years is None:
            available_years_str = get_available_years()
            self.available_years = [int(year) for year in available_years_str if year.isdigit()]
            
            # 現在年まで自動拡張
            current_year = datetime.now().year
            max_year = max(self.available_years) if self.available_years else 2024
            if max_year < current_year:
                print(f"データ年範囲を{max_year}から{current_year}に自動拡張")
                self.available_years.extend(range(max_year + 1, current_year + 1))
        else:
            self.available_years = available_years
            
        # 結果ファイルをスクリプトと同じディレクトリに保存
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.results_file = os.path.join(script_dir, f"{datetime.now().strftime('%Y-%m-%d')}_{config.TARGET_MODEL}_optimize_years.txt")

    def generate_rolling_combinations(self) -> List[Tuple[List[int], int]]:
        """
        学習年の組み合わせローリング時系列交差検証の組み合わせ生成
        ユーザー要求: 全モデル高精度3年（2年学習→1年テスト）組み合わせ限定
        
        Returns:
            List[Tuple[List[int], int]]: (学習年リスト, テスト年)の組み合わせ
        """
        combinations_list = []
        
        # 2年学習 → 1年テスト（連続年、合計3年）のみ
        for i in range(len(self.available_years) - 2):
            train_years = self.available_years[i:i+2]
            test_year = self.available_years[i+2]
            combinations_list.append((train_years, test_year))
        
        return combinations_list

    def evaluate_year_combination(self, train_years: List[str], test_year: str) -> Dict[str, Any]:
        """
        指定された年組み合わせでモデル性能を評価
        
        Args:
            train_years: 学習年リスト
            test_year: テスト年
            
        Returns:
            評価結果辞書
        """
        start_time = time.time()
        
        try:
            # 環境変数設定
            env = os.environ.copy()
            env['AI_TARGET_YEARS'] = ','.join(train_years + [test_year])
            
            # スクリプトのディレクトリから絶対パスを取得
            script_dir = os.path.dirname(os.path.abspath(__file__))
            ai_dir = os.path.join(script_dir, "..", "..")
            ai_dir = os.path.abspath(ai_dir)
            data_script = os.path.join(ai_dir, "data", "data.py")
            
            # データ処理実行
            data_cmd = [config.PYTHON_PATH, config.PYTHON_VERSION, data_script, ','.join(train_years + [test_year])]
            data_result = subprocess.run(data_cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', env=env, cwd=ai_dir, timeout=300)
            
            if data_result.returncode != 0:
                return {
                    'train_years': train_years,
                    'test_year': test_year,
                    'success': False,
                    'error': f"Data processing failed: {data_result.stderr}",
                    'execution_time': time.time() - start_time
                }
            
            # モデル学習実行（Pycaretの場合はタイムアウトを延長）
            model_script = os.path.join(script_dir, f"{config.TARGET_MODEL}_train.py")
            model_cmd = [config.PYTHON_PATH, config.PYTHON_VERSION, model_script]
            train_timeout = 1200 if config.TARGET_MODEL == "Pycaret" else 600
            model_result = subprocess.run(model_cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', env=env, cwd=ai_dir, timeout=train_timeout)
            
            if model_result.returncode != 0:
                return {
                    'train_years': train_years,
                    'test_year': test_year,
                    'success': False,
                    'error': f"Model training failed: {model_result.stderr}",
                    'execution_time': time.time() - start_time
                }
            
            # 結果解析（stdout から性能指標を抽出）
            output = model_result.stdout
            rmse = self._extract_metric(output, "RMSE")
            r2 = self._extract_metric(output, "R2")
            mae = self._extract_metric(output, "MAE")
            
            return {
                'train_years': train_years,
                'test_year': test_year,
                'success': True,
                'rmse': rmse,
                'r2': r2,
                'mae': mae,
                'execution_time': time.time() - start_time
            }
            
        except Exception as e:
            return {
                'train_years': train_years,
                'test_year': test_year,
                'success': False,
                'error': str(e),
                'execution_time': time.time() - start_time
            }

    def _extract_metric(self, output: str, metric_name: str) -> float:
        """出力から指標値を抽出"""
        patterns = {
            "RMSE": r"RMSE:\s*([0-9\.]+)\s*kW",
            "R2": r"R2(?:スコア)?:\s*([0-9\.]+)",
            "MAE": r"MAE:\s*([0-9\.]+)\s*kW"
        }
        
        pattern = patterns.get(metric_name, "")
        if pattern:
            match = re.search(pattern, output)
            if match:
                return float(match.group(1))
        return 0.0

    def optimize_years(self, target_metric: str = "rmse") -> Dict[str, Any]:
        """
        組み合わせ年を最適化
        
        Args:
            target_metric: 最適化対象指標 ("rmse", "r2", "mae")
            
        Returns:
            最適化結果辞書
        """
        print("=" * 80)
        print(f"{config.TARGET_MODEL}モデル - 学習年組み合わせ最適化")
        print("=" * 80)
        print(f"利用可能年: {', '.join(map(str, self.available_years))}")
        
        # ローリング時系列交差検証の組み合わせ生成
        combinations = self.generate_rolling_combinations()
        
        print(f"検証組み合わせ数: {len(combinations)}")
        
        all_results = []
        
        print("\n学習年組み合わせ検証を実行中...")
        
        # 各組み合わせを評価
        for i, (train_years, test_year) in enumerate(combinations):
            train_years_str = [str(y) for y in train_years]
            test_year_str = str(test_year)
            
            progress = f"[{i+1:2d}/{len(combinations):2d}]"
            combination_desc = f"{','.join(train_years_str)}→{test_year_str}"
            print(f"{progress} {combination_desc}: ", end="", flush=True)
            
            result = self.evaluate_year_combination(train_years_str, test_year_str)
            all_results.append(result)
            
            if result['success']:
                print(f"成功 (RMSE: {result['rmse']:.1f})")
            else:
                print(f"失敗 - {result['error']}")
        
        # 結果保存
        self._save_results(all_results)
        
        # 最適結果選択
        successful_results = [r for r in all_results if r['success']]
        if not successful_results:
            raise Exception("全ての組み合わせで評価に失敗しました")
        
        # 最適化指標に基づいて選択
        if target_metric == "rmse":
            best_result = min(successful_results, key=lambda x: x['rmse'])
        elif target_metric == "r2":
            best_result = max(successful_results, key=lambda x: x['r2'])
        elif target_metric == "mae":
            best_result = min(successful_results, key=lambda x: x['mae'])
        else:
            best_result = min(successful_results, key=lambda x: x['rmse'])
        
        # 統計情報計算
        rmse_values = [r['rmse'] for r in successful_results]
        r2_values = [r['r2'] for r in successful_results]
        
        # 結果出力
        print("\n" + "=" * 80)
        print(f"{config.TARGET_MODEL}モデル - 学習年組み合わせ最適化結果")
        print("=" * 80)
        print()
        print(f"総実行回数: {len(combinations)}")
        print(f"成功回数: {len(successful_results)}")
        print()
        
        # 上位5組み合わせを表示
        sorted_results = sorted(successful_results, key=lambda x: x['rmse'])
        print("【上位5組み合わせ（RMSE基準）】")
        print()
        
        for rank, result in enumerate(sorted_results[:5], 1):
            train_str = ','.join(result['train_years'])
            print(f"{rank}位: 学習年 {train_str} → テスト年 {result['test_year']}")
            print(f"   RMSE: {result['rmse']:.3f} kW")
            print(f"   R²: {result['r2']:.4f}")
            print(f"   MAE: {result['mae']:.3f} kW")
            print(f"   実行時間: {result['execution_time']:.1f}秒")
            print()
        
        # 統計情報
        print("【統計情報】")
        rmse_mean = np.mean(rmse_values)
        rmse_std = np.std(rmse_values)
        r2_mean = np.mean(r2_values)
        r2_std = np.std(r2_values)
        
        print(f"RMSE - 平均: {rmse_mean:.3f}, 標準偏差: {rmse_std:.3f}")
        print(f"RMSE - 最小: {min(rmse_values):.3f}, 最大: {max(rmse_values):.3f}")
        print(f"R² - 平均: {r2_mean:.4f}, 標準偏差: {r2_std:.4f}")
        print()
        
        # 最優秀組み合わせ
        print(f"【最優秀組み合わせ】")
        best_train_str = ','.join(best_result['train_years'])
        print(f"学習年: {best_train_str}")
        print(f"テスト年: {best_result['test_year']}")
        print(f"RMSE: {best_result['rmse']:.3f} kW, R²: {best_result['r2']:.4f}, MAE: {best_result['mae']:.3f} kW")
        print()
        
        print(f"結果を {self.results_file} に保存しました")
        print("=" * 80)
        print(f"{config.TARGET_MODEL}モデル学習年組み合わせ最適化が完了しました")
        print("=" * 80)
        
        return {
            'model': config.TARGET_MODEL,
            'best_combination': best_result,
            'all_results': all_results,
            'statistics': {
                'rmse_mean': rmse_mean,
                'rmse_std': rmse_std,
                'r2_mean': r2_mean,
                'r2_std': r2_std
            }
        }

    def _save_results(self, results: List[Dict]) -> None:
        """結果をテキストファイルに保存"""
        output_lines = []
        output_lines.append("=" * 80)
        output_lines.append(f"{config.TARGET_MODEL}モデル - 学習年組み合わせ最適化結果")
        output_lines.append("=" * 80)
        output_lines.append(f"実行日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        output_lines.append("")
        
        successful_results = [r for r in results if r['success']]
        output_lines.append(f"総実行回数: {len(results)}")
        output_lines.append(f"成功回数: {len(successful_results)}")
        output_lines.append("")
        
        if successful_results:
            # 上位5組み合わせを表示
            sorted_results = sorted(successful_results, key=lambda x: x['rmse'])
            output_lines.append("【上位5組み合わせ（RMSE基準）】")
            output_lines.append("")
            
            for rank, result in enumerate(sorted_results[:5], 1):
                train_str = ','.join(result['train_years'])
                output_lines.append(f"{rank}位: 学習年 {train_str} → テスト年 {result['test_year']}")
                output_lines.append(f"   RMSE: {result['rmse']:.3f} kW")
                output_lines.append(f"   R²: {result['r2']:.4f}")
                output_lines.append(f"   MAE: {result['mae']:.3f} kW")
                output_lines.append(f"   実行時間: {result['execution_time']:.1f}秒")
                output_lines.append("")
            
            # 統計情報
            rmse_values = [r['rmse'] for r in successful_results]
            r2_values = [r['r2'] for r in successful_results]
            
            output_lines.append("【統計情報】")
            rmse_mean = np.mean(rmse_values)
            rmse_std = np.std(rmse_values)
            r2_mean = np.mean(r2_values)
            r2_std = np.std(r2_values)
            
            output_lines.append(f"RMSE - 平均: {rmse_mean:.3f}, 標準偏差: {rmse_std:.3f}")
            output_lines.append(f"RMSE - 最小: {min(rmse_values):.3f}, 最大: {max(rmse_values):.3f}")
            output_lines.append(f"R² - 平均: {r2_mean:.4f}, 標準偏差: {r2_std:.4f}")
            output_lines.append("")
            
            # 最優秀組み合わせ
            best_result = sorted_results[0]
            output_lines.append(f"【最優秀組み合わせ】")
            best_train_str = ','.join(best_result['train_years'])
            output_lines.append(f"学習年: {best_train_str}")
            output_lines.append(f"テスト年: {best_result['test_year']}")
            output_lines.append(f"RMSE: {best_result['rmse']:.3f} kW, R²: {best_result['r2']:.4f}, MAE: {best_result['mae']:.3f} kW")
            output_lines.append("")
        
        output_lines.append("=" * 80)
        
        # ファイル保存
        with open(self.results_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        
        print(f"結果を {self.results_file} に保存しました")

def main() -> None:
    """メイン処理"""
    current_year = datetime.now().year
    
    print(f"電力需要予測AIモデル - {config.TARGET_MODEL}学習年組み合わせ最適化")
    print("=" * 80)
    
    # 利用可能年取得
    available_years_str = get_available_years()
    available_years = [int(year) for year in available_years_str if year.isdigit()]
    
    print(f"利用可能年: {', '.join(map(str, available_years))}")
    print(f"現在年: {current_year}")
    
    # 最適化実行
    optimizer = YearCombinationOptimizer(available_years)
    
    try:
        result = optimizer.optimize_years(target_metric="rmse")
        
        # メモ帳で結果ファイルを開く
        result_file_path = os.path.abspath(optimizer.results_file)
        if os.path.exists(result_file_path):
            subprocess.Popen(['notepad.exe', result_file_path])
        
    except Exception as e:
        print(f"[ERROR] 最適化エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

