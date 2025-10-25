# Webサイト スタイリングガイド

このドキュメントは、**JennyPortal** のWebサイト構築に使用されるスタイリングのガイドラインを定義します。

**共通スタイル** と **テーマ固有のスタイル（Colorfulテーマ）** に分けて記述します。

## 1. 共通スタイル

全てのテーマで共通して適用される基本的なレイアウト、コンポーネント、タイポグラフィのスタイルです。

### 1.1. 基本レイアウト

- **全体**: スムーズスクロールを有効化
    
- **ボックスモデル**: 全要素で `box-sizing: border-box` を適用
    

#### body

- フレックスボックスレイアウト（縦方向）
    
- 最小高さはビューポートの100%
    
- 基本フォントサイズ: `1.05em`
    
- 行の高さ: `1.6`
    

#### main

- 最大幅: `1600px`、中央揃え
    
- 半透明の背景: `rgba(26, 32, 44, 0.9)`
    
- ブラー効果: `backdrop-filter: blur(16px)`
    
- 角丸: `border-radius: 24px`
    

#### section

- 角丸: `border-radius: 10px`
    
- 下マージン: `margin-bottom: 35px`
    
- ホバー時のアニメーション: `transform: translateY(-5px)`
    

#### footer

- 中央揃え
    

### 1.2. タイポグラフィ

- **基本フォント**: `'Noto Sans JP', sans-serif`
    
- **見出しフォント**: `'Orbitron', sans-serif`
    

#### section h2

- フォントサイズ: `1.8em`
    
- フォントウェイト: `700`
    

#### .sub-card h3

- フォントサイズ: `1.3em`
    
- フォントウェイト: `700`
    

### 1.3. コンポーネント

#### .sub-card-container

- レスポンシブなグリッド: `grid-template-columns: repeat(auto-fit, minmax(300px, 1fr))`
    
- カード間スペース: `20px`
    

#### .sub-card

- 角丸: `border-radius: 8px`
    
- ホバー時アニメーション: `transform: translateY(-3px)`
    
- 全体がクリック可能なリンク
    
- ツールチップ表示と `Ctrl+クリック` で新規タブ
    

#### .mini-link-card

- フレックスレイアウトで横並び
    
- 小さな角丸: `border-radius: 6px`
    
- ホバー時アニメーション: `transform: translateY(-2px)`
    
- ツールチップ表示と `Ctrl+クリック` で新規タブ
    

#### .download-button

- 角丸: `border-radius: 5px`
    
- フォント: `'Orbitron'` を使用
    

### 1.4. レスポンシブデザイン

- **1200px以下**: `.sub-card` の最小幅を `280px` に調整
    
- **768px以下**:
    
    - `main` と `section` のパディングを縮小
        
    - `.sub-card` を2カラムレイアウトに調整
        
- **480px以下**:
    
    - `.sub-card` を1カラムレイアウトに調整
        
    - 各見出しのフォントサイズを縮小
        

## 2. Colorfulテーマ 固有スタイル

カラフルで視覚的に魅力的なテーマのスタイルです。

### 2.1. 配色

- **基本背景**: `linear-gradient(135deg, #1a202c 0%, #2d3748 100%)`
    
- **テキスト色**: `#e0e0e0`
    

#### カード背景

- `section`: `#2a2a4a`
    
- `.sub-card`: `rgba(42, 42, 74, 0.7)`
    

#### section h2

- 色: `#667eea`
    
- 下線: `#667eea`
    

#### section > p

- 色: `#e0e0e0`
    

### 2.2. カードのスタイリング

#### 難度に応じたボーダー色

- `.border-green`: `#22c55e`
    
- `.border-blue`: `#3b82f6`
    
- `.border-teal`: `#14b8a6`
    
- `.border-yellow`: `#f59e0b`
    
- `.border-orange`: `#f97316`
    
- `.border-pink`: `#ec4899`
    
- `.border-purple`: `#8b5cf6`
    
- `.border-red`: `#ef4444`
    

#### カードタイトルのグラデーション

- 各ボーダー色に対応したグラデーション（例: `.gradient-yellow`）
    

#### section ul li

- 左ボーダーに `--card-border-color-var` を使用
    

## 3. Webサイト構築プロンプトへの活用

このスタイリングガイドを**Webサイト構築プロンプト**として使用する際は、以下の形式で指示します。

### 例:

以下の仕様でWebサイトのHTMLとCSSを生成してください。

- **テーマ**: Colorfulテーマ
    

#### 全体的なスタイル:

- 共通スタイルガイドラインを適用してください
    
- Colorfulテーマの配色とカードスタイリングを適用してください
    

#### レイアウト:

- ヘッダー、メイン、フッターの3セクション構成
    
- メインセクションには、複数の情報カードをグリッドレイアウトで配置
    

#### コンポーネント:

- `.sub-card` を使って各情報を表示
    
- 各カードには異なる色のボーダーと、対応するグラデーションカラーのタイトルを付ける
    
- カード内に `.mini-link-card` を配置し、関連リンクを示す
    
- フッターには `.download-button` を配置し、CSVダウンロード機能を提供