---
marp: true
theme: uncover
backgroundImage: url('../jera/デジタル部門_中扉.jpg')
backgroundSize: cover
style: |
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&family=Yuji+Syuku&display=swap');
  section {
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

# Gemini CLIで爆速資料作成

## 無料枠で最強モデル！

---

## 今回の動画で解説すること

*   Gemini-CLIを用いた爆速資料作成方法
*   Claude Codeの対抗馬としても期待されるGemini CLI
*   注目すべきは無料枠：Gemini 2.5 Proが1日1000回まで利用可能

---

## 資料作成のプロセス

1.  Gemini CLIでスライドテンプレートを作成
2.  テンプレートに沿って台本からスライド生成
3.  編集可能な資料に変換

---

<p class="key-message">資料作成の品質を保ちつつ<br>速度を上げる方法を解説！</p>

---

# 今回の資料作成の仕方

## Marpを活用

*   Marpはマークダウンで書かれた文書をスライドに変換する技術
*   このマークダウン部分をGemini CLIに記述させる

---

## Marpによるスライド作成イメージ

<!-- AIが詳細なイラストを生成できるよう、具体的な描写: MarkdownコードがMarpによって美しいスライドに変換される様子。左側にMarkdownコード、右側に完成したスライドのビジュアル。 -->
<img src="https://placehold.co/600x400" alt="MarkdownからMarpスライドへの変換イメージ">

---

## 他の資料作成ツールとの比較

### GensparkのAIスライド機能

*   台本から高品質なスライドを自動生成
*   ほぼそのまま利用可能な完成度

---

## Gensparkの課題

*   「文字が多すぎる」と感じる場合がある
*   「いつもの黒板背景を使いたい」など、細かい要望に対応しにくい

---

<p class="key-message">Gemini CLIとMarpで<br>あなたの理想のスライドを！</p>