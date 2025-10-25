---
marp: true
theme: uncover
style: |-
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&family=Yuji+Syuku&display=swap');

  section {
    background-image: url('../kokuban.png');
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
---

<style scoped>
section {
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
}
</style>

# Gemini CLIで資料作成

---

## 今回の動画でわかること

- Gemini CLIで資料作成を爆速化する方法
- Marpで使えるテンプレート作成
- 台本からスライドを自動生成
- 編集可能な形式への変換

---

<p class="key-message">Gemini 2.5 Pro<br>1日1000回まで無料</p>

---

## 今回の資料作成の仕方

- Marpという技術を使って資料作成
- マークダウンでスライドを作成
- Gemini CLIにマークダウンを書かせる

---

<!-- AIがイラストを生成するためのコメント: スライド作成ツールGensparkのAIスライド機能のイメージ。スタイリッシュなUIで、スライドが自動生成されている様子。 -->
<div class="img-center">
  <img src="https://placehold.co/600x400" alt="GensparkのAIスライド機能のイメージ">
</div>

---

## Genspark AIスライドとの比較

- **Genspark**
  - 高品質なスライドを自動生成
  - 文字が多すぎることがある
  - デザインのカスタマイズが難しい

- **Gemini CLI + Marp**
  - 柔軟なカスタマイズ
  - いつもの黒板背景が使える

---

<p class="key-message">品質と速度を両立する</p>

---

## まとめ

- Gemini CLIとMarpで資料作成を効率化
- ぜひ活用してみてくださいね
