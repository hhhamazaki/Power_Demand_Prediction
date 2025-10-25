---
marp: true
theme: gaia
_class: lead
paginate: true
backgroundColor: #fff
backgroundImage: 'url(./デジタル部門/デジタル部門_表紙.jpg)'

style: |
  /* 表紙タイトルとサブタイトル */
  section.lead h1 {
    font-size: 72px;   /* デフォルト相当 */
    line-height: 1;
    margin: 40px 0 80px 0;
    text-align: center;
  }
  section.lead h2 {
    font-size: 46px;   /* デフォルト相当 */
    line-height: 1;
    margin: 0;
    text-align: center;
    font-weight: normal;
  }

  /* 2ページ目以降の基本設定 */
  section.top-left {
    display: flex;
    flex-direction: column;
    justify-content: flex-start; /* 上端寄せ */
    align-items: flex-start;
    margin: 0;
    padding: 40px 60px;
    height: 100%;
    text-align: left;
  }

  /* 見出し（大） */
  section.top-left h2 {
    font-size: 48px;   /* ← フォントサイズは戻す */
    margin-left: 20px;
    margin-bottom: 50px;
    line-height: 1;  /* ← 行間は調整済みを維持 */
  }

  /* 小見出し */
  section.top-left h3 {
    font-size: 40px;   /* ← フォントサイズは戻す */
    margin: 2px 0 2px 20px;       /* 上下2px 左20px */
    line-height: 1.5;  /* ← 行間は調整済みを維持 */
  }

  /* 通常の本文テキスト */
  section.top-left p {
    font-size: 36px;  /* ← 少し小さめ */
    line-height: 0; /* 行間は調整済みを維持 */
  }

  /* 箇条書き */
  section.top-left ul {
    list-style-position: outside;   /* マーカーを外側に */
    margin-left: 2em;               /* 全体の開始位置 */
    padding-left: 0;                /* 内側余白を消す */
  }

  /* 箇条書き項目 */  
  section.top-left li {
    font-size: 36px;
    line-height: 01;    /* タイトに */
    margin: 2px 0 0 0; /* 上2px 下0 */
    padding-left: 0em;          /* テキスト開始位置 */
    text-indent: -0em;          /* ぶら下げインデント */
    }


  /* 小見出し直下の箇条書き */
    section.top-left h3 + ul {
    margin-top: 4px;   /* 小見出しとの間隔を詰める */
    }

    section.top-left h3 + ul li {
    font-size: 36px;
    line-height: 1; /* 行間は少し余裕を残す */
    margin-top: 2px;   /* 項目間隔をタイトに */
    }

    section::after {
    position: absolute;
    bottom: 0px;          /* 下からの距離 */
    left: 50%;             /* 横方向中央 */
    transform: translate(-1%, 45%); /* 中央揃え */
    font-size: 18px;       /* ページ番号のサイズ */
    color: #333;           /* 色 */
    line-height: 1;            /* 行間を詰めて下に寄せる */
    padding-bottom: 0;         /* 余計な内側余白を消す */
    }   

  /* 市民開発・フロー画像だけを厳密に中央かつ幅制限（他画像は不変） */
  section.top-left img[src="市民開発.PNG"],
  section.top-left img[src="フロー.PNG"] {
    display: block;
    margin-left: auto;
    margin-right: auto;
    margin-top: 24px;
    max-width: 1100px;
    width: auto;
    height: auto;
    box-sizing: border-box;
    object-fit: contain;
  }
---
#### 【開発力強化】開発、保守案件の内製化に向けた育成計画策定

# AI教育コンテンツ作成

#### デジタルソリューション統括部
#### 部門横断課題　人材育成チーム
2025年10月2日​

---

<!-- _class: top-left -->

<!-- backgroundImage: url(./デジタル部門/デジタル部門_背景.jpg) -->

## 背景と意義

### 🌍背景

- 「AIの進化」が「働き方」を根本から刷新する歴史的な変革期

### 💎チャンス到来

- 市場価値の高い「AIドリブン人財」「ハイパフォーマー」になる

### 🔥意義

- 「スキル習得」が組織変革の起点

### ※学習する非エンジニアが、学習するAIを駆使して、<br>　学習しないプロを凌駕する時代

---

<!-- _class: top-left -->

## 3つの成⻑⽬標

### 🎯実践スキル習得

- AI×自動化ツール「操作スキル」
- 思考プロセス「言語化スキル」（コンテクスト構造化）
- コード「読解スキル」

### 🧠AIの特性と「限界」を理解

- 最適な「AIモデル選択」センス養成

### ⚡ハイパフォーマンス体験

- 劇的な生産性向上をAIで再現

---

<!-- _class: top-left -->

## ローコード市⺠開発の役割

### 「②市民開発」が、

### 「①現場オンボーディング」と「③プロ開発」を橋渡し

<img src="市民開発.PNG">

---

<!-- _class: top-left -->

## 5つの体験フロー

###### 「①ローコード開発」～「④アプリ開発」「⑤AIモデル構築」を100%内製

<img src="フロー.PNG">

## 生産性の飛躍的インパクトを体感

---

<!-- _class: top-left -->

## 期待する成果

### ✨短期間で成果を実証

- AI補助で「非エンジニア」が圧倒的パフォーマンスを発揮

### ⚡スピードとクオリティを両⽴

- コード開発‧ドキュメント作成‧分析プロセスを高速化

#
#
### さらに「プロ開発者」も、

- 「豊富な経験知」と「AI機能」を融合、「コード品質」チェック
- #### ベンダー成果物レビュー・アプリ内製など模範事例を創出

---

<!-- _class: top-left -->

## 今後の展望

### 📈コンテンツ全社展開

- 非エンジニアから全社員へ
- ターゲット拡大（キャリア自律）

### 🤝部⾨コラボ強化

- DPPアプリ内製
- ML回帰分析モデル応用
  LNG･NH3タンク在庫、GT圧縮機フィルタ･脱硫M/E差圧を予測

### 🎯成功事例の共有

- AI×自動化ツール連携
- 市民開発ドキュメント自動生成：実用レベル（採用済！）

---

<!-- _class: lead -->

<!-- backgroundImage: url(./デジタル部門/デジタル部門_中扉.jpg) -->

### 2025年10月2日16時

# デジタル部門の新人が、

# 第一歩を踏み出しました！

## このビジョンに共感したら、即アクセス！

### https://jeragroup.sharepoint.com/sites/Jenny1/SitePages/AIモデル体感コース.aspx
