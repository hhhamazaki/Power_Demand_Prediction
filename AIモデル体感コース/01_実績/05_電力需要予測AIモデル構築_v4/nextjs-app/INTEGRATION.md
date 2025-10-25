# Next.jsアプリとAIフォルダの統合ガイド

このドキュメントは **Next.js と既存 AI フォルダの統合仕様** を解説します。

---

## 📋 ドキュメント階層

- プロジェクト全体の概要 → `../README.md` を参照
- ローカル開発手順 → `README.md` を参照
- Vercel デプロイ → `DEPLOYMENT.md` を参照

---

## 概要

Next.js アプリケーションは、既存の AI フォルダ内の Python スクリプト（**Python 3.10 で実行**）を呼び出して動作します。この統合を正しく機能させるための設定ガイドです。

## ディレクトリ構造の要件

プロジェクトのディレクトリ構造は以下のようになっている必要があります:

```
05_電力需要予測AIモデル構築_v4/
├── AI/                    # 既存のPythonスクリプト群
│   ├── data/
│   ├── train/
│   ├── tomorrow/
│   └── requirements.txt
│
└── nextjs-app/            # Next.jsアプリケーション
    ├── src/
    ├── package.json
    └── requirements.txt
```

## ローカル開発環境のセットアップ

### Windows (PowerShell)

1. **プロジェクトルートに移動**

```powershell
cd C:\Users\<UserName>\<project_root>\05_電力需要予測AIモデル構築_v4
```

2. **Python 依存のインストール**

```powershell
# Python 3.10 で依存をインストール
py -3.10 -m pip install --upgrade pip
py -3.10 -m pip install -r AI/requirements.txt
```

3. **Next.js アプリのセットアップ**

```powershell
cd nextjs-app
npm install
npm install --save-dev @types/node @types/react @types/react-dom
```

4. **開発サーバー起動**

```powershell
npm run dev
```

### macOS / Linux

1. **プロジェクトルートに移動**

```bash
cd /path/to/05_電力需要予測AIモデル構築_v4
```

2. **Python 依存のインストール**

```bash
# Python 3.10 で依存をインストール
python3.10 -m pip install --upgrade pip
python3.10 -m pip install -r AI/requirements.txt
```

3. **Next.js アプリのセットアップ**

```bash
cd nextjs-app
npm install
npm install --save-dev @types/node @types/react @types/react-dom
```

4. **開発サーバー起動**

```bash
npm run dev
```

## APIルートとPythonスクリプトの統合

### パス解決の仕組み

Next.js APIルートは、以下のようにPythonスクリプトのパスを解決します:

```typescript
// 例: src/app/api/run-data/route.ts
const scriptPath = path.join(process.cwd(), '..', 'AI', 'data', 'data.py');
// 結果: /path/to/05_電力需要予測AIモデル構築_v4/AI/data/data.py
```

### 重要なポイント

1. **相対パス**: `..` を使用して nextjs-app から親ディレクトリ（プロジェクトルート）に移動
2. **作業ディレクトリ**: Python スクリプトは常に AI フォルダを cwd として実行
3. **環境変数**: `AI_TARGET_YEARS` などの環境変数を適切に設定
4. **Python バージョン**: すべての Python 実行は **Python 3.10** (`py -3.10` または `python3.10`) を使用

## Vercelデプロイ時の注意点

### ファイル配置

Vercelにデプロイする際は、**両方のフォルダ（AIとnextjs-app）**をリポジトリに含める必要があります:

```
your-repo/
├── AI/           # Pythonスクリプト群
└── nextjs-app/   # Next.jsアプリ
```

### vercel.json設定

Root Directoryを `nextjs-app` に設定しつつ、親ディレクトリのAIフォルダにもアクセスできるようにします:

```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "framework": "nextjs"
}
```

### GitHubリポジトリ構造

```
J1921604/Power_Demand_Prediction/
├── .gitignore
├── README.md
├── AI/
│   ├── data/
│   │   ├── data.py
│   │   ├── juyo-*.csv
│   │   └── temperature-*.csv
│   ├── train/
│   │   ├── LightGBM/
│   │   ├── Keras/
│   │   ├── Pycaret/
│   │   └── RandomForest/
│   ├── tomorrow/
│   │   ├── LightGBM/
│   │   ├── Keras/
│   │   ├── Pycaret/
│   │   └── RandomForest/
│   └── requirements.txt
│
└── nextjs-app/
    ├── src/
    ├── package.json
    ├── next.config.js
    ├── tsconfig.json
    ├── vercel.json
    └── requirements.txt
```

## トラブルシューティング

### エラー: "Pythonスクリプトが見つかりません"

**原因**: ディレクトリ構造が正しくない

**解決策**:

1. プロジェクト構造を確認
2. AIフォルダとnextjs-appフォルダが同じ親ディレクトリにあることを確認

### エラー: "ModuleNotFoundError"

**原因**: Python依存パッケージがインストールされていない

**解決策**:

```powershell
# Python 3.10 で依存をインストール
py -3.10 -m pip install --upgrade pip
py -3.10 -m pip install -r AI/requirements.txt
```

### エラー: "spawn python ENOENT"

**原因**: Python が環境変数 PATH に登録されていない、または Python 3.10 が見つからない

**解決策**:

- Windows: Python 3.10 インストール時に「Add Python to PATH」をチェック、または `py -3.10 --version` で確認
- macOS/Linux: `which python3.10` で確認、必要なら `python3.10` へのシンボリックリンクを作成

## データファイルの管理

### 開発環境

データファイル（CSV）はAI/dataフォルダに配置:

```
AI/data/
├── juyo-2016.csv
├── juyo-2017.csv
...
├── temperature-2016.csv
├── temperature-2017.csv
...
```

### 本番環境（Vercel）

Vercelでは、データファイルもリポジトリに含める必要があります。ただし、大きなファイルは `.gitignore` で除外し、環境変数や外部ストレージを使用することを推奨します。

## パフォーマンス最適化

### キャッシュ戦略

生成された画像やCSVファイルは、APIレスポンスヘッダーでキャッシュ制御:

```typescript
// src/app/api/images/[...path]/route.ts
return new NextResponse(fileBuffer, {
  headers: {
    'Content-Type': contentType,
    'Cache-Control': 'no-cache, no-store, must-revalidate',
  },
});
```

### サーバーレス関数の最適化

```json
// vercel.json
{
  "functions": {
    "src/app/api/**/*.ts": {
      "maxDuration": 300,
      "memory": 3008
    }
  }
}
```

## まとめ

- Next.jsアプリとAIフォルダは **同じ親ディレクトリ** に配置
- APIルートは **相対パス** でPythonスクリプトを実行
- Vercelデプロイ時は **両方のフォルダ** をリポジトリに含める
- データファイルは **AIフォルダ内** に配置

---

© 2025 Power Demand Prediction Project
