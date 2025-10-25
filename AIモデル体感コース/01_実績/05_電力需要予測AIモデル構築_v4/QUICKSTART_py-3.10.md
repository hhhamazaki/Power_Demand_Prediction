# Next.js 変換クイックスタートガイド（py -3.10 前提）

**作成日**: 2025-10-25  
**対象**: 電力需要AI予測システム Next.js 移行版

---

## このドキュメントの目的

このファイルは、既存 Python ベース AI システムを Next.js に変換した作業の要約と、**最速で動作確認するためのクイックスタート**を提供します。詳細な手順は各専門ドキュメントを参照してください。

**重要**: すべての Python 実行は `py -3.10` を使用します。

---

## 📋 ドキュメント構成と推奨読み順

プロジェクトには以下のドキュメントがあります。**この順で読むことを強く推奨**します:

| 順序 | ファイル名 | 役割 | いつ読むか |
|------|-----------|------|-----------|
| 1 | `README.md` | プロジェクト全体の概要・技術スタック・ディレクトリ構成 | **最初に必読** |
| 2 | `nextjs-app/README.md` | Next.js アプリのローカル開発専用ガイド | ローカル起動前 |
| 3 | `nextjs-app/INTEGRATION.md` | AI フォルダとの統合仕様・パス解決の詳細 | 統合動作確認時 |
| 4 | `nextjs-app/DEPLOYMENT.md` | Vercel デプロイの完全手順・環境変数・トラブルシューティング | デプロイ前 |
| 5 | このファイル | クイックスタート・全体要約 | 今ここ |

---

ただしクイックスタートは「最速で起動したい場合」に先に使っても問題ありません（目的に応じて順序を柔軟に使ってください）。

## ⚡ クイックスタート（5分で起動）

### 前提条件
- Node.js 18+ がインストール済み
- Python 3.10 がインストール済み（`py -3.10 --version` で確認）
- Git でリポジトリをクローン済み

### 手順（PowerShell）

```powershell
# 1. プロジェクトルートへ移動
cd <your-project-root>\05_電力需要予測AIモデル構築_v4

# 2. Python 依存をインストール
py -3.10 -m pip install --upgrade pip
py -3.10 -m pip install -r AI/requirements.txt

# 3. Next.js アプリへ移動
cd nextjs-app

# 4. Node 依存と型定義をインストール
npm install
npm install --save-dev @types/node @types/react @types/react-dom

# 5. 開発サーバ起動
npm run dev
```

ブラウザで `http://localhost:3000` を開く → ダッシュボード UI が表示されれば成功！

---

## 🚀 次のステップ

### ローカル開発を続ける場合
→ `nextjs-app/README.md` を読んで、モデル学習・予測の使い方を確認してください。

### AI との統合を理解したい場合
→ `nextjs-app/INTEGRATION.md` で API ルートと Python スクリプトの連携を確認してください。

### Vercel にデプロイする場合
→ `nextjs-app/DEPLOYMENT.md` で詳細なデプロイ手順と環境変数設定を確認してください。

---

## ⚠️ よくあるトラブル（速攻解決）

| 問題 | 解決策 |
|------|-------|
| TypeScript 型エラーが出る | `npm install --save-dev @types/node @types/react @types/react-dom` を実行 |
| Python モジュールが見つからない | `py -3.10 -m pip install -r AI/requirements.txt` を再実行 |
| `spawn python ENOENT` エラー | Python 3.10 のパスが通っているか確認（`py -3.10 --version`） |
| API が 404 エラー | `AI/` フォルダと `nextjs-app/` が同じ親ディレクトリにあるか確認 |

詳細なトラブルシューティングは `nextjs-app/DEPLOYMENT.md` の「トラブルシューティング」セクションを参照。

---

## 📦 変換で追加されたファイル

- `nextjs-app/` 全体（Next.js プロジェクト）
  - `src/app/api/*` - API Routes（Python 実行）
  - `src/components/Dashboard.tsx` - UI コンポーネント
  - `package.json`, `next.config.js`, `tsconfig.json`, `vercel.json` - 設定ファイル

詳細なディレクトリ構成は `README.md` を参照。

---

## 🔗 関連リンク

- プロジェクト README: `../README.md`
- Next.js 開発ガイド: `nextjs-app/README.md`
- 統合仕様: `nextjs-app/INTEGRATION.md`
- デプロイ手順: `nextjs-app/DEPLOYMENT.md`

---

**© 2025 Power Demand Prediction Project**
