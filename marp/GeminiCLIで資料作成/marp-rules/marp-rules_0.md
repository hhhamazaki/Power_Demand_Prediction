marp: true
## Marpスライド作成ルール
このドキュメントは、与えられた台本に基づき、Marp形式のスライドを生成するためのルールを定義します。

### 1. グローバルスタイル
スライド全体に適用されるスタイルです。
- **テーマ:** `uncover`
- **背景画像:** `kokuban.PNG` を全面に敷きます。
- **フォント:** 基本は `Noto Sans JP`、キーメッセージなど、特に強調したい箇所では手書き風の `Yuji Syuku` を使用します。

YAML
```
---
marp: true
theme: uncover
style: |
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&family=Yuji+Syuku&display=swap');
  section {
    background-image: url('./kokuban.PNG');
    background-size: cover;
    font-family: 'Noto Sans JP', sans-serif;
    color: #fff;
    padding: 60px;
  }
  h1, h2, h3, h4 {
    color: #fff;
    text-align: center;
    margin: 0;
    padding: 0 20px;
  }
  h1 { font-size: 2.2em; }
  h2 { font-size: 1.8em; }
  h3 { font-size: 1.5em; }
  p, ul, li, blockquote {
    font-size: 1.1em;
  }
  .key-message {
    font-family: 'Yuji Syuku', serif;
    font-size: 3em;
    text-align: center;
  }
  .img-center {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 80%;
  }
  img {
    max-height: 100%;
    max-width: 100%;
    width: 600px;
    height: 400px;
  }
  .flex-container {
    display: flex;
    justify-content: space-around;
    align-items: flex-start;
    gap: 20px;
  }
  .flex-item {
    flex: 1;
    text-align: center;
  }
  .flex-item img {
    width: 100%;
    height: auto;
    max-width: 350px;
  }
  .flex-item h3 {
    font-size: 1.2em;
  }
  .flex-item p {
    font-size: 1em;
  }
  pre {
    width: 80%;
    background: #333;
    padding: 1em;
    border-radius: 5px;
    margin: 0 auto;
  }
  pre code {
    font-size: 1.5em;
  }
---
```
---
### 2. スライド生成の基本ルール
- 台本のセクション（例：「イントロ」「結論」など）ごとに、内容を解釈し、最適なレイアウトパターンを適用してスライドを生成します。
- 台本の `v-` のようなマーカーは、スライドの区切り（`---`）として扱います。
- 台本のテキストは、スライドのタイトルや補足説明として使用しますが、画像によって内容が伝わる場合は、冗長なテキストを削除します。
---
### 3. 画像とプレースホルダー
視覚的な理解を助けるため、画像を積極的に活用します。
- **画像化の判断:** 台本の内容が抽象的、比較的、または図解に適している場合、画像を挿入します。
- **プレースホルダー:** すぐに利用できる画像がない場合は、以下のプレースホルダーを使用します。

HTML
```
<img src="https://placehold.co/600x400" alt="[画像の簡単な説明]">
```
- **AI生成のためのコメント:** 画像タグの直前に、AIが詳細なイラストを生成できるよう、具体的で描写的なHTMLコメントを必ず追加します。
- **悪い例:**
- **良い例:**
---
### 4. スライドのレイアウトパターン

#### パターン1: タイトルスライド
- **目的:** 新しいトピックや質問を提示する。
- **Marpコード例:**

Markdown
```
<style scoped>
section {
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
}
</style>
## Q. シングルターン vs マルチターン
---
```
---
#### パターン2: キーメッセージスライド
- **目的:** そのセクションで最も伝えたい核心的なメッセージを提示する。
- **Marpコード例:**

Markdown
```
<p class="key-message">AIは"会話"で<br>迷子になる</p>
---
```
---
#### パターン3: 定義・箇条書きスライド
- **目的:** 用語の定義を述べたり、複数の要素をリストアップする。
- **Marpコード例:**

Markdown
```
---
## この動画でわかること
* なぜAIは長話が苦手なのか？
* AIの力を最大限に引き出す「一発指示」のコツ
---
```
---
#### パターン4: 図解・イラストスライド
- **目的:** 概念やアイデアを、イラストや図を用いて視覚的に説明する。
- **Marpコード例:**

Markdown
```
---
## AIが"迷子"になるプロセス
```