<!--
marp: true
theme: uncover
style: |
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');
  section {
    background-color: #191970;
    font-family: 'Noto Sans JP', sans-serif;
    color: #fff;
    padding: 60px;
  }
  h1, h2, h3, h4, h5, h6 {
    color: #fff;
    text-align: left;
  }
  h1 {
    font-size: 3em;
    text-align: center;
  }
  h2 {
    font-size: 2.2em;
    border-bottom: 2px solid #0000FF;
    padding-bottom: .3em;
  }
  a {
    color: #0000FF;
  }
  .left-half {
    float: left;
    width: 50%;
    padding-right: 30px;
  }
  .right-half {
    float: right;
    width: 50%;
    padding-left: 30px;
  }
  .center {
    text-align: center;
  }
-->

# Canva風 Marp スタイルテンプレート

## 1. グローバルスタイル

Canvaのデザインを参考に、紺色を基調としたモダンでクリーンなスタイルです。

- **テーマ:** `uncover`
- **背景色:** `#191970` (紺色)
- **フォント:** `Noto Sans JP`
- **アクセントカラー:** `#0000FF` (青)

## 2. レイアウトパターン

### パターン1: タイトルスライド

**用途:** プレゼンテーションのタイトルや、各セクションの区切り。

**Marpコード:**
```markdown
---
<!-- _class: center -->
# 会社の使命と目標
---
```

### パターン2: 2カラムレイアウト（テキスト＆画像）

**用途:** 左にテキスト、右に画像を配置する、最も基本的なレイアウト。

**Marpコード:**
```markdown
---
<div class="left-half">

## 会社の使命と目標
年末までに達成したい目標

</div>
<div class="right-half">

![bg right](https://images.unsplash.com/photo-1505373877841-8d25f7d46678?q=80&w=2012&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D)

</div>
---
```

### パターン3: 箇条書き

**用途:** 目次や要点のリストアップ。

**Marpコード:**
```markdown
---
## 目次
* パート1: ミッション
* パート2: 主な目標
* パート3: 重要な企業戦略
* パート4: まとめ
---
```

### パターン4: 強調メッセージ

**用途:** 特に伝えたいメッセージを中央に大きく表示。

**Marpコード:**
```markdown
---
<!-- _class: center -->
## コミュニティとお客様の生活で真の違いを生み出したいから
---
```
