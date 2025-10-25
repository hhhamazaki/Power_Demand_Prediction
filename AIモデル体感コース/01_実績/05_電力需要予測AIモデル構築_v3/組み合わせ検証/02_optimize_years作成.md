
####   1. **各モデル用optimize_years.pyの作成**

以下の4つのファイルを作成しました：

- [LightGBM_optimize_years.py](vscode-file://vscode-app/c:/Users/h-ham/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)
- [Keras_optimize_years.py](vscode-file://vscode-app/c:/Users/h-ham/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)
- [Pycaret_optimize_years.py](vscode-file://vscode-app/c:/Users/h-ham/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)
- [RandomForest_optimize_years.py](vscode-file://vscode-app/c:/Users/h-ham/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)

**特徴：**

- 学習年の組み合わせ.mdに基づいた時系列交差検証（ローリング方式）を実装
- 2年～6年の学習データ組み合わせを自動生成してテスト
- 各組み合わせでRMSE、R²、MAEを計算
- 上位5組み合わせと統計情報を表示

#### 2. **結果のテキストファイル保存とメモ帳自動起動**

各スクリプトに以下の機能を実装：

- 実行結果を`YYYY-MM-DD_モデル名_optimize_years.txt`形式で保存
- スクリプト終了後、メモ帳で結果ファイルを自動的に開く

#### 3. **ダッシュボードに「組み合わせ検証」ボタン追加**

[index.html](vscode-file://vscode-app/c:/Users/h-ham/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)を更新：

- 学習年カードに「組み合わせ検証」ボタンを追加
- 学習ボタンと同じマゼンタ系スタイルを適用
- ツールチップで説明を追加
- 実行中のビジュアルフィードバック（スケール拡大、ネオン効果）を実装

#### 4. **サーバー側エンドポイント追加**

[server.py](vscode-file://vscode-app/c:/Users/h-ham/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)に`/run-optimize-years`エンドポイントを追加：

- 選択したモデルに応じて適切なoptimize_years.pyを実行
- LightGBM、Keras、PyCaret、RandomForestの4モデルに対応

### 🎯 実装の特徴

1. **効率的な検証手順**
    
    - 各モデルで独立したスクリプトを作成し、並行テスト可能
    - データ処理とモデル学習を自動化
2. **統一されたコードベース**
    
    - 全モデルで同じロジックとインターフェースを使用
    - メンテナンスしやすい設計
3. **ユーザーフレンドリー**
    
    - ダッシュボードから簡単に実行可能
    - 結果がメモ帳で自動的に開く
    - 視覚的なフィードバック（実行中の表示）

### 📊 使用方法

1. ダッシュボードでモデルを選択（Keras、LightGBM、PyCaret、RandomForest）
2. 「組み合わせ検証」ボタンをクリック
3. スクリプトが自動的に：
    - 2年～6年の複数の学習年組み合わせをテスト
    - 各組み合わせでデータ処理→モデル学習→性能評価を実行
    - 最適な組み合わせを特定
4. 結果がメモ帳で自動的に開き、以下の情報を確認：
    - 上位5組み合わせ（RMSE基準）
    - 統計情報（平均、標準偏差、最小、最大）
    - 最優秀組み合わせ
