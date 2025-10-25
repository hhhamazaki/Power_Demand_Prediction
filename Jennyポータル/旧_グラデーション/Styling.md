# JennyPortal スタイルガイド

このドキュメントは、JennyPortalウェブサイトの主要なスタイリング要素とTailwind CSSの活用方法をまとめたものです。

## 1. 全体的なテーマとカラーパレット

- **テーマ**: クリーン、モダン、インタラクティブ、グラデーション
    
- **フォント**: `'Noto Sans JP', sans-serif` (日本語の読みやすさを重視)
    
- **カラーパレット**:
    
    - 背景グラデーション: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)` (青から紫へのグラデーション)
        
    - メインテキストカラー: `#334155` (濃い青灰色)
        
    - カード/コンテナ背景: `bg-white bg-opacity-95 backdrop-blur-lg` (白を基調とした半透明でぼかし効果)
        
    - ボタン/ナビゲーションタブのグラデーション:
        
        - 通常: `from-purple-500 to-indigo-500`
            
        - ホバー: `from-purple-600 to-indigo-600`
            
        - アクティブ: `from-indigo-600 to-purple-700`
            
    - ボタンテキスト色: `text-gray-800` (通常), `text-white` (アクティブ時)
        
    - リンク/アクセントカラー: `text-purple-600`, `text-blue-600`, `text-orange-600`, `text-red-600`, `text-cyan-600`, `text-indigo-700` (各カードのテーマに合わせた色)
        

## 2. 基本スタイル

```
body {
    font-family: 'Noto Sans JP', sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* 背景グラデーション */
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #334155; /* メインテキストカラー */
}
```

## 3. アニメーション

### 3.1. フェードインアニメーション (`fadeIn`)

タブコンテンツの表示時に使用されるアニメーション。

```
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.tab-content.active {
    animation: fadeIn 0.5s ease-in-out;
}
```

### 3.2. カードのホバーエフェクト

コンテンツカードとコースカードに適用される、わずかな浮き上がりとシャドウの変化。

```
.content-card, .course-card {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.content-card:hover, .course-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}
```

### 3.3. ボタンのクリックアニメーション

ボタンとナビゲーションタブに適用される、クリック時の縮小効果。

```
.btn, .nav-tab {
    transition: transform 0.15s ease-in-out, background-color 0.3s ease, color 0.3s ease, box-shadow 0.3s ease;
}
.btn:active, .nav-tab:active {
    transform: scale(0.95);
}
```

## 4. コンポーネントスタイル

### 4.1. コンテナ (`.container`)

コンテンツを中央に配置し、背景に半透明のホワイトとぼかし効果を適用。

```
.container {
    max-width: 4xl; /* Tailwind: max-w-4xl */
    margin-left: auto; /* Tailwind: mx-auto */
    margin-right: auto; /* Tailwind: mx-auto */
    background-color: white; /* Tailwind: bg-white */
    background-opacity: 0.95; /* Tailwind: bg-opacity-95 */
    backdrop-filter: blur(16px); /* Tailwind: backdrop-blur-lg */
    border-radius: 3rem; /* Tailwind: rounded-3xl */
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); /* Tailwind: shadow-xl */
    padding: 1.5rem; /* Tailwind: p-6 */
    padding-md: 2rem; /* Tailwind: md:p-8 */
    margin-top: 2rem; /* Tailwind: my-8 */
    margin-bottom: 2rem; /* Tailwind: my-8 */
}
```

### 4.2. ナビゲーションタブ (`.nav-tab`)

丸みを帯びたボタン形式のナビゲーション。

```
.nav-tab {
    padding-x: 1.5rem; /* Tailwind: px-6 */
    padding-y: 0.75rem; /* Tailwind: py-3 */
    border-radius: 9999px; /* Tailwind: rounded-full */
    font-weight: 600; /* Tailwind: font-semibold */
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); /* Tailwind: shadow-lg */
}
/* アクティブ/ホバー時のグラデーションとテキスト色はTailwindクラスで動的に変更 */
```

### 4.3. コンテンツカード (`.content-card`)

各タブコンテンツのメインカード。

```
.content-card {
    background-color: white; /* Tailwind: bg-white */
    padding: 1.5rem; /* Tailwind: p-6 */
    border-radius: 1rem; /* Tailwind: rounded-2xl */
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); /* Tailwind: shadow-md */
    margin-bottom: 1.5rem; /* Tailwind: mb-6 */
}
```

### 4.4. コースカード (`.course-card`)

セクション内の詳細コンテンツを示すカード。グラデーション背景が特徴。

```
.course-card {
    padding: 1.25rem; /* Tailwind: p-5 */
    border-radius: 0.75rem; /* Tailwind: rounded-xl */
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); /* Tailwind: shadow-lg */
    color: white; /* Tailwind: text-white */
    text-align: center; /* Tailwind: text-center */
    display: flex; /* Tailwind: flex */
    flex-direction: column; /* Tailwind: flex-col */
}
/* 各カードのグラデーションはTailwindクラスで個別に設定 */
/* 例: bg-gradient-to-br from-blue-500 to-purple-600 */
```

### 4.5. ボタン (`.btn`)

カード内の詳細リンクボタン。

```
.btn {
    background-color: white; /* Tailwind: bg-white */
    padding-x: 1rem; /* Tailwind: px-4 */
    padding-y: 0.5rem; /* Tailwind: py-2 */
    border-radius: 9999px; /* Tailwind: rounded-full */
    font-weight: 500; /* Tailwind: font-medium */
}
/* 各ボタンのテキスト色はTailwindクラスで個別に設定 */
/* 例: text-purple-600 */
```

## 5. スクロールバーのカスタマイズ

```
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
}
::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
    background: #555;
}
```

## 6. タイポグラフィ

- **h2**: `text-3xl font-bold text-indigo-700 mb-4 border-b-2 border-indigo-300 pb-2`
    
- **h4 (コースカードタイトル)**: `text-xl font-semibold mb-2`
    
- **p (説明文)**: `text-gray-700 mb-6`, `text-sm mb-4`
    
- **リスト (`ul li`)**: `list-disc list-inside ml-4 text-sm text-left`
    

## 7. レスポンシブデザイン

Tailwind CSSのブレークポイント (`md:`, `lg:`) を活用し、グリッドレイアウトやパディングなどが画面サイズに応じて自動的に調整されます。

- **コンテナ**: `p-6` (モバイル) -> `md:p-8` (中画面以上)
    
- **グリッドレイアウト**: `grid-cols-1` (モバイル) -> `md:grid-cols-2` (中画面以上) -> `lg:grid-cols-3` (大画面以上)