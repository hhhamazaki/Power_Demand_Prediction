# 電力需要AI予測ダッシュボード - ローカル開発ガイド

このドキュメントは **Next.js アプリのローカル開発専用** ガイドです。

---

## 📋 ドキュメント階層

- プロジェクト全体の概要 → `../README.md` を参照
- AI 統合の詳細 → `INTEGRATION.md` を参照
- Vercel デプロイ → `DEPLOYMENT.md` を参照

---

## 概要

このプロジェクトは、LightGBM、Keras、PyCaret、RandomForest の 4 つの AI モデルを使用して、電力需要を高精度で予測するシステムです。Next.js 14 (App Router) と Python 3.10 を統合し、動的でインタラクティブなダッシュボードを提供します。

## 主な機能

- **4種類のAIモデル対応**: LightGBM、Keras、PyCaret、RandomForest
- **リアルタイム予測**: 最新データを取得して翌日の電力需要を予測
- **学習機能**: 選択した年のデータでモデルを学習
- **組み合わせ検証**: 最適な学習年の組み合わせを自動検証
- **可視化**: 予測結果と学習結果をグラフで表示
- **レスポンシブデザイン**: PC・タブレット・スマートフォン対応

## 技術スタック

### フロントエンド
- Next.js 14 (App Router)
- React 18
- TypeScript
- CSS Modules

### バックエンド
- Next.js API Routes
- **Python 3.10** (`py -3.10` コマンドで実行)
- LightGBM, TensorFlow/Keras, PyCaret, scikit-learn

### インフラ
- Vercel (デプロイ)
- Node.js 18+

## セットアップ

### 前提条件
- Node.js 18.0.0以上
- npm 9.0.0以上
- **Python 3.10** (`py -3.10 --version` で確認)
- pip

### インストール

1. **リポジトリのクローン**
```powershell
git clone https://github.com/J1921604/Power_Demand_Prediction.git
cd Power_Demand_Prediction
```

2. **Python 依存パッケージのインストール**
```powershell
# プロジェクトルートから AI フォルダの requirements をインストール
py -3.10 -m pip install --upgrade pip
py -3.10 -m pip install -r AI/requirements.txt
```

3. **Node.js 依存パッケージのインストール**
```powershell
cd nextjs-app
npm install
npm install --save-dev @types/node @types/react @types/react-dom
```

4. **データファイルの配置**
AI フォルダ内の data ディレクトリに、電力需要データ(`juyo-YYYY.csv`)と気温データ(`temperature-YYYY.csv`)を配置します。

**重要**: `AI/` フォルダと `nextjs-app/` フォルダは同じ親ディレクトリに配置する必要があります。詳細は `INTEGRATION.md` を参照。

### ローカル開発

```powershell
# nextjs-app ディレクトリから
npm run dev
```

ブラウザで `http://localhost:3000` を開きます。

## Vercelへのデプロイ

Vercel へのデプロイ手順およびよくあるトラブル対処は `DEPLOYMENT.md` に詳細を記載しています。まずはそちらを参照してください。

要点: GitHub に push し、Vercel 側で Root Directory を `nextjs-app` に設定すること、必要な環境変数（例: `PYTHON_VERSION=3.10` 等）を登録すること。

（手順の詳細とトラブルシューティングは `DEPLOYMENT.md` を確認してください）

## 使い方

### 1. モデルの選択
- Keras、LightGBM、PyCaret、RandomForestから選択

### 2. 学習
1. 学習年を選択（複数選択可能）
2. 「データ処理」ボタンをクリック（学習年を変更した場合のみ）
3. 「学習」ボタンをクリック
4. 学習完了後、RMSE/R2/MAEの指標が表示されます

### 3. 予測
1. 「最新データ取得」ボタンをクリック（初回のみ）
2. 「予測」ボタンをクリック
3. 予測完了後、RMSE/R2/MAEの指標と予測グラフが表示されます

### 4. 組み合わせ検証
- 「組み合わせ検証シミュレーション」ボタンをクリック
- 最適な学習年の組み合わせが自動的に検証されます

## ディレクトリ構成

```
nextjs-app/
├── src/
│   ├── app/
│   │   ├── api/           # API Routes
│   │   │   ├── run-data/
│   │   │   ├── run-train/
│   │   │   ├── run-tomorrow/
│   │   │   ├── run-tomorrow-data/
│   │   │   ├── run-optimize-years/
│   │   │   ├── available-years/
│   │   │   └── images/
│   │   ├── layout.tsx     # レイアウト
│   │   ├── page.tsx       # メインページ
│   │   └── globals.css    # グローバルCSS
│   └── components/
│       └── Dashboard.tsx  # ダッシュボードコンポーネント
├── public/                # 静的ファイル
├── package.json           # Node.js依存関係
├── requirements.txt       # Python依存関係
├── next.config.js         # Next.js設定
├── tsconfig.json          # TypeScript設定
├── vercel.json            # Vercel設定
└── README.md              # このファイル
```

## パフォーマンス最適化

- **サーバーサイドレンダリング**: 初回ロードを高速化
- **API Routes**: Pythonスクリプトを効率的に実行
- **画像最適化**: グラフ画像のキャッシュ制御
- **レスポンシブデザイン**: デバイスに応じた最適表示

## トラブルシューティング

### Pythonスクリプトが実行されない
- **Python 3.10 がインストールされているか確認**: `py -3.10 --version`
- **必要なパッケージがインストールされているか確認**: `py -3.10 -m pip install -r ../AI/requirements.txt`

### データファイルが見つからない
- `AI/data/` ディレクトリに CSV ファイルが配置されているか確認
- ファイル名が `juyo-YYYY.csv` と `temperature-YYYY.csv` の形式か確認
- 詳細は `INTEGRATION.md` を参照

### TypeScript 型エラー
```powershell
npm install --save-dev @types/node @types/react @types/react-dom
npm run build
```

### API が動作しない
- `AI/` フォルダと `nextjs-app/` が同じ親ディレクトリにあるか確認
- 詳細は `INTEGRATION.md` の「パス解決の仕組み」を参照

### Vercelデプロイ時のエラー
- **詳細は `DEPLOYMENT.md` のトラブルシューティングセクションを参照**
- ビルドログを確認
- 環境変数が正しく設定されているか確認（`PYTHON_VERSION=3.10`）
- `vercel.json` の設定を確認

## ライセンス

MIT License

## 開発者

Power Demand Prediction Team

## 問い合わせ

問題が発生した場合は、GitHubのIssuesセクションで報告してください。

---

© 2025 Power Demand Prediction Project
