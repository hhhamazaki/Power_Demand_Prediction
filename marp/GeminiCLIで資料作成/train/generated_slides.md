---
marp: true
theme: ./marp-rules.md
backgroundImage: url('kokuban.PNG')
---

<section class="title-slide">

# Gemini CLIで資料作成

質と速度を両立する資料作成術

</section>

---

<section class="key-point-slide">

### では最初に

# 「AIプロダクト開発」とは？

私がイメージしていること

</section>

---

<section class="concept-slide">

# AIをソフトウェアの機能として搭載すること

</section>

---

<section class="bullet-list-slide">

# AI機能搭載の例

*   CursorやGensparkなどのAIネイティブなツール
*   GmailにGeminiによる執筆補助機能が足されるなど、既存のソフトウェアにAI機能が追加されるもの

</section>

---

<section class="bullet-list-slide">

# AIをソフトウェアの中で活躍させるには

*   AIの性能を引き出すためのプロンプトなどのチューニング
*   全体のアーキテクチャ設計
    *   どこでどんなデータを引っ張ってどんな処理を行なっていくのかを考えます

</section>

---

<section class="key-point-slide">

### では1点目のプロンプトチューニングにつきまして

# 日常と業務では一体何が違うのか？

</section>

---

<section class="concept-slide">

# 「インプットとアウトプットの幅の違い」が大きくあります

</section>

---

<section class="bullet-list-slide">

# 日常で使うプロンプト

*   そもそも一回だけ満足する結果が得られればいい
*   1つ使うの自分だけなので、入力するインプットの幅もそんなになければ、アウトプットの幅も想定しなくて良い

</section>

---

<section class="bullet-list-slide">

# 業務で使うプロンプト

*   アウトプットの幅も広く、且つそれなりの品質を担保しなければいけないところに難しさがある

</section>
