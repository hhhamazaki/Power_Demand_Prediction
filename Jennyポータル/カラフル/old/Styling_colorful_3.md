# Webサイト スタイリングガイド

このドキュメントは、JennyPortalのWebサイト構築に使用されるスタイリングのガイドラインを定義します。共通スタイルとテーマ固有のスタイル（Colorfulテーマ）に分けて記述します。

---

## 1. 共通スタイル

全てのテーマで共通して適用される基本的なレイアウト、コンポーネント、タイポグラフィのスタイルです。

### 1.1. 基本レイアウト

- **全体**: スムーズスクロールを有効化。
- **ボックスモデル**: 全要素で `box-sizing: border-box` を適用。
- **ボディ (`body`)**:
  - フレックスボックスレイアウト（縦方向）。
  - 最小高さはビューポートの100%。
  - 基本フォントサイズ: `1.05em`、行の高さ: `1.6`。
- **メインコンテンツ (`main`)**:
  - 最大幅 `1600px` で中央揃え。
  - 半透明の背景 (`rgba(26, 32, 44, 0.9)`) とブラー効果 (`backdrop-filter: blur(16px)`)。
  - 角丸 (`border-radius: 24px`)。
- **セクション (`section`)**:
  - 角丸 (`border-radius: 10px`)。
  - 下マージン (`margin-bottom: 35px`)。
  - ホバー時のに浮き上がるアニメーション効果 (`transform: translateY(-5px)`)。
- **フッター (`footer`)**:
  - 中央揃え。

### 1.2. タイポグラフィ

- **基本フォント**: 'Noto Sans JP', sans-serif
- **見出しフォント**: 'Orbitron', sans-serif
- **セクションタイトル (`section h2`)**:
  - フォントサイズ: `1.8em`
  - `font-weight: 700`
- **カードタイトル (`.sub-card h3`)**:
  - フォントサイズ: `1.3em`
  - `font-weight: 700`

### 1.3. コンポーネント

- **サブカードコンテナ (`.sub-card-container`)**:
  - レスポンシブなグリッドレイアウト (`grid-template-columns: repeat(auto-fit, minmax(300px, 1fr))`)。
  - カード間のスペース: `20px`。
- **サブカード (`.sub-card`)**:
  - 角丸 (`border-radius: 8px`)。
  - ホバー時に浮き上がるアニメーション効果 (`transform: translateY(-3px)`)。
  - カード全体がクリック可能なリンクとして機能。
- **ミニリンクカード (`.mini-link-card`)**:
  - フレックスレイアウトで横並びに配置。
  - 小さな角丸 (`border-radius: 6px`)。
  - ホバー時に浮き上がるアニメーション効果 (`transform: translateY(-2px)`)。
- **ダウンロードボタン (`.download-button`)**:
  - 角丸 (`border-radius: 5px`)。
  - 見出しフォント (`Orbitron`) を使用。

### 1.4. レスポンシブデザイン

- **1200px以下**: サブカードの最小幅を `280px` に調整。
- **768px以下**:
  - `main` と `section` のパディングを縮小。
  - サブカードを2カラムレイアウトに調整。
- **480px以下**:
  - サブカードを1カラムレイアウトに調整。
  - 各見出しのフォントサイズを縮小。

---

## 2. Colorfulテーマ 固有スタイル

カラフルで視覚的に魅力的なテーマのスタイルです。

### 2.1. 配色

- **基本背景**: ダークなグラデーション (`linear-gradient(135deg, #1a202c 0%, #2d3748 100%)`)
- **テキスト色**: 明るいグレー (`#e0e0e0`)
- **カード背景**:
  - `section`: `#2a2a4a`
  - `.sub-card`: `rgba(42, 42, 74, 0.7)`
- **セクションタイトル (`section h2`)**:
  - 色: 明るい紫 (`#667eea`)
  - 下線: 同色 (`#667eea`)
- **セクション説明テキスト (`section > p`)**:
  - 色: 薄いグレー (`#a0aec0`)

#### 2.1.1 ボーダー色 (.border- クラス)
        /* カードボーダー色 (新しい統一された色順) */
        .border-yellow { border-color: #f59e0b; --card-border-color-var: #f59e0b; }
        .border-orange { border-color: #f97316; --card-border-color-var: #f97316; }
        .border-red { border-color: #ef4444; --card-border-color-var: #ef4444; }
        .border-blue { border-color: #3b82f6; --card-border-color-var: #3b82f6; }
        .border-teal { border-color: #14b8a6; --card-border-color-var: #14b8a6; }
        .border-purple { border-color: #8b5cf6; --card-border-color-var: #8b5cf6; }

#### 2.1.2. カードタイトルのグラデーションテキスト色 (.gradient- クラス)
        /* カードタイトルのグラデーションテキスト色 (新しい統一された色順) */
        .gradient-yellow {
            background: linear-gradient(to right, #f59e0b, #f97316); /* 黄からオレンジ */
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .gradient-orange {
            background: linear-gradient(to right, #f97316, #ef4444); /* オレンジから赤 */
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .gradient-red {
            background: linear-gradient(to right, #ef4444, #3b82f6); /* 赤から青 */
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .gradient-blue {
            background: linear-gradient(to right, #3b82f6, #14b8a6); /* 青からティール */
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .gradient-teal {
            background: linear-gradient(to right, #14b8a6, #8b5cf6); /* ティールから紫 */
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .gradient-purple {
            background: linear-gradient(to right, #8b5cf6, #6366f1); /* 紫からより深い紫/藍 */
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

- **カードタイトルのグラデーションテキスト**:
  - 各ボーダー色に対応したグラデーションを適用 (例: `.gradient-blue` は青系のグラデーション)。
- **リストアイテム (`section ul li`)**:
  - 左ボーダーに、親カードのボーダー色 (`--card-border-color-var`) を使用。

---

## 3. Webサイト構築プロンプトへの活用

このスタイリングガイドをWebサイト構築プロンプトとして使用する際は、以下の形式で指示します。

### 例:

「以下の仕様でWebサイトのHTMLとCSSを生成してください。

**テーマ:** Colorfulテーマ

**全体的なスタイル:**
- 共通スタイルガイドラインを適用してください。
- Colorfulテーマの配色とカードスタイリングを適用してください。

**レイアウト:**
- ヘッダー、メイン、フッターの3つのセクションで構成します。
- メインセクションには、複数の情報カードをグリッドレイアウトで配置します。

**コンポーネント:**
- サブカードコンポーネントを使用して、各情報を表示します。
- カードには、それぞれ異なる色のボーダーと、対応するグラデーションカラーのタイトルを付けてください。
- カード内には、ミニリンクカードを配置して関連リンクを示します。
- フッターには、CSVダウンロードボタンを配置してください。」
