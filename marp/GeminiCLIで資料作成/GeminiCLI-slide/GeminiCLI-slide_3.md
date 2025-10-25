---
marp: true
theme: uncover
style: |-
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&family=Yuji+Syuku&display=swap');

  section {
    background-image: url('../kokuban.PNG');
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
  /* 強調したい理念やメッセージ用のスタイル */
  .key-message {
    font-family: 'Yuji Syuku', serif;
    font-size: 3em;
    text-align: center;
  }
  /* 画像を中央に配置するためのスタイル */
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

<style scoped>
section {
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
}
</style>

# Gemini CLIで資料作成
## 質と速度を両立する資料作成術

---

## イントロダクション

*   今回の動画ではGemini-CLIを用いて爆速で資料作成をしていく方法を解説します
*   先日発表されたGemini CLI、Claude Codeの対抗馬としても期待されますが
*   なんと言っても注目なのは無料枠
*   Gemini 2.5 Proという最強モデルが1日1000回まで呼べてしまいます

---

<p class="key-message">Gemini CLIで<br>爆速資料作成！</p>

---

## 資料作成のステップ

*   スライドのテンプレートを作成
*   台本からスライド生成
*   編集可能な資料に変換

---

<p class="key-message">品質を保ちつつ<br>速度を上げる！</p>

---

## 今回の資料作成の仕方

*   今回はMarpという技術を使って資料作成を行なっていきます
*   Marpはマークダウンで書かれた文書をスライドにしてくれる技術です

<!-- AI: Marpがマークダウンからスライドを生成するイメージ図 -->
<img src="https://placehold.co/600x400" alt="Marpによるスライド生成イメージ">

---

<p class="key-message">マークダウンを<br>Gemini CLIに書かせる！</p>

---

## 他の資料作成ツールとの比較

*   代表的なものはGensparkのAIスライド機能
*   台本を渡すと、結構いい感じのスライドをパパっと作ってくれます

---

## Gensparkの所感

*   かなり整っていて、ほぼほぼ「まあこれ使いながらそのまま話せるかな」という所感
*   「ちょっと文字が多過ぎるかな」
*   「いつもの黒板背景使いたいな」
*   細かい要望が出てくることもあります

---