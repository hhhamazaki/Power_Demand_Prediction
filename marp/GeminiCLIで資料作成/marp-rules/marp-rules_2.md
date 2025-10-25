---
marp: true
theme: uncover
style: |-
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&family=Yuji+Syuku&display=swap');
  section {
    background-image: url('./kokuban.jpg');
    background-size: cover;
    font-family: 'Noto Sans JP', sans-serif;
    color: #111;
    padding: 60px;
  }
  h1, h2, h3, h4 {
    color: #111;
    text-align: center;
    margin: 0;
    padding: 0 20px;
    text-shadow: 2px 2px 4px #fff, 0 0 2px #eee, 0 0 1px #eee;
  }
  h1 { font-size: 1.7em; }
  h2 { font-size: 1.4em; }
  h3 { font-size: 1.15em; }
  p, ul, li, blockquote {
    font-size: 0.95em;
    text-shadow: 1px 1px 3px #fff, 0 0 2px #eee;
  }
  .key-message {
    font-family: 'Yuji Syuku', serif;
    font-size: 2.1em;
    text-align: center;
    color: #111;
    text-shadow: 3px 3px 6px #fff, 0 0 2px #eee, 0 0 1px #eee;
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

<!-- タイトルスライドの例 -->
# Marpテンプレートの使用例

---

<!-- キーメッセージスライドの例 -->
<p class="key-message">未来感あふれる<br>プレゼンテーション</p>

---

<!-- 定義・箇条書きスライドの例 -->
## 特徴

- 美しい黒板風の背景
- モダンなフォントの組み合わせ
- フレキシブルなレイアウト
- レスポンシブな画像表示

---

<!-- 図解・イラストスライドの例 -->
## 画像表示の例

<!-- AIによる未来的なテクノロジーのイラスト -->
<div class="img-center">
<img src="https://placehold.co/600x400" alt="テクノロジーイメージ">
</div>

---

<!-- フレックスボックスレイアウトの例 -->
## フレックスボックスレイアウト

<div class="flex-container">
<div class="flex-item">
<img src="https://placehold.co/350x200" alt="項目1">
<h3>項目1</h3>
<p>説明テキスト</p>
</div>
<div class="flex-item">
<img src="https://placehold.co/350x200" alt="項目2">
<h3>項目2</h3>
<p>説明テキスト</p>
</div>
</div>

---

<!-- コードブロックの例 -->
## コードブロックの表示

```javascript
console.log("Hello, Marp!");
```
