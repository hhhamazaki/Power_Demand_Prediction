---
marp: true
theme: uncover
backgroundColor: 
backgroundImage: url('kokuban.PNG')
color: 
style: |-
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');
  section {
    font-family: 'Noto Sans JP', sans-serif;
  }
---

# Marpスライド作成ルール

## 基本ルール

- **背景**: `kokuban.PNG` を背景画像として使用します。
- **フォント**: Googleフォントの 'Noto Sans JP' を使用します。
- **テキスト**: 基本的に白文字(#fff)です。強調したい部分は太字や色変更で対応します。
---
## スライドテンプレート

### 1. タイトルスライド

```markdown
---
marp: true
theme: uncover
backgroundColor: #000
backgroundImage: url('kokuban.PNG')
color: #fff
style: |
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');
  section {
    font-family: 'Noto Sans JP', sans-serif;
    text-align: center;
  }
  h1 {
    font-size: 60px;
  }
  p {
    font-size: 30px;
  }
---

# Gemini CLIで資料作成

質と速度を両立する資料作成術
```
---
### 2. 通常スライド（テキストのみ）

```markdown
---
marp: true
theme: uncover
backgroundColor: #000
backgroundImage: url('kokuban.PNG')
color: #fff
style: |
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');
  section {
    font-family: 'Noto Sans JP', sans-serif;
  }
---

## AIプロダクト開発のイメージ

AIをソフトウェアの機能として搭載すること

- **AIネイティブなツール**: Cursor, Genspark
- **既存ソフトウェアへの追加**: Gmailの執筆補助機能
```
---
### 3. スライド（テキスト+画像）

```markdown
---
marp: true
theme: uncover
backgroundColor: #000
backgroundImage: url('kokuban.PNG')
color: #fff
style: |
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');
  section {
    font-family: 'Noto Sans JP', sans-serif;
  }
---

## 日常と業務でのプロンプトの違い

インプットとアウトプットの幅が大きく異なる

![bg right:40%](https://placeholder.co/600x400)
