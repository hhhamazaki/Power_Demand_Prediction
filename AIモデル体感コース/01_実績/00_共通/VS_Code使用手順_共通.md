# VS Code使用手順 共通版

## 1. 適用範囲と前提

### 1.1 VS Code
- **推奨バージョン**: 最新安定版（定期更新推奨）
- **対象OS**: Windows 10/11（PowerShell使用）
- **インストール元**: [VS Code公式サイト](https://code.visualstudio.com/)

### 1.2 Python
- **推奨バージョン**: 3.10.11（全プロジェクト統一）
- **インストール元**: [python.org 公式サイト](https://www.python.org/downloads/release/python-31011/)
Filesの「**Windows installer (64-bit)**」をクリックしてインストーラー（python-3.10.11-amd64.exeファイル）をダウンロードします。

## 2. 環境セットアップ

### 2.1 VS Codeでフォルダを開く

1. VS Codeを起動
2. `Ctrl + K, Ctrl + O` または「ファイル」→「フォルダーを開く」を選択
3. 以下のパスを指定して開く。
C:\Users\<UserName>\<project_root>\03_経費登録ワークフロー
C:\Users\<UserName>\<project_root>\04_経費管理アプリ
C:\Users\<UserName>\<project_root>\05_電力需要予測AIモデル構築

### 2.2 PowerShellターミナルを開く

1. VS Codeで `Ctrl + Shift + P` を押す
2. 「Terminal: Create New Terminal」を選択
3. ターミナルが表示されることを確認

### 2.3 Python環境設定

# Python バージョン確認（3.10.11必須）
py -3.10 --version
# 結果例: Python 3.10.11

# 仮想環境作成（推奨・Python 3.10.11指定）
py -3.10 -m venv .venv

# 仮想環境を有効化
.\.venv\Scripts\Activate.ps1
**重要**：コマンドライン先頭に `(.venv)` が表示されることを確認！

# 仮想環境Python バージョン確認（3.10.11必須）
.\.venv\Scripts\python.exe --version
# 結果例: Python 3.10.11

### 2.4 VS Code Pythonインタープリターの選択

1. - `Ctrl+Shift+P`でコマンドパレットを開く
2. - 「Python: Select Interpreter」と入力して選択
3. - 作成した仮想環境の`.\venv\Scripts\python.exe` を選択

### 2.5 必要ライブラリのインストール

# 1. 既存パッケージの完全削除（推奨）
python -m pip freeze > temp_packages.txt
python -m pip uninstall -r temp_packages.txt -y
Remove-Item temp_packages.txt

# 2. pip自体の最新化
python -m pip install --upgrade pip

# 3. 全モデル対応の完全版インストール
pip install -r requirements.txt

環境をリセットしたい場合は、`.venv`フォルダを削除し、再度手順3.2から実行してください。

## 3. 実行

### 3.1. 経費登録ワークフロー
python -m py/経費登録_claude_sonnet_4.py
python -m py/経費登録_gpt-4.1.py
python -m py/経費登録_claude_sonnet_3.5.py
python -m py/経費登録_gpt-5.py

### 3.2. 経費管理アプリ
`html` フォルダを選択
`index.html` を右クリック → `Open with Live Server`
ブラウザで http://localhost:5500 または http://127.0.0.1:5500 にアクセス

### 3.3. 電力需要予測AIモデル構築

# データ前処理実行
python -m AI/data/data.py

# Keras学習実行
python -m AI/train/Keras/Keras_train.py

# LightGBM学習実行
python -m AI/train/LightGBM/LightGBM_train.py

# PyCaret学習実行
python -m AI/train/Pycaret/Pycaret_train.py

# RandomForest学習実行
python -m AI/train/RandomForest/RandomForest_train.py

# 統一最新電力需要データ取得
python -m AI/tomorrow/data.py

# 統一気象データ取得（Open-Meteo API）
python -m AI/tomorrow/temp.py

# Keras翌日予測実行
python -m AI/tomorrow/Keras/Keras_tomorrow.py

# LightGBM翌日予測実行
python -m AI/tomorrow/LightGBM/LightGBM_tomorrow.py

# PyCaret翌日予測実行
python -m AI/tomorrow/Pycaret/Pycaret_tomorrow.py

# RandomForest翌日予測実行
python -m AI/tomorrow/RandomForest/RandomForest_tomorrow.py
