---
marp: true
theme: uncover
backgroundImage: url('../GeminiCLIで資料作成/jera/デジタル部門_中扉.jpg')
backgroundSize: cover
style: |-
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&family=Yuji+Syuku&display=swap');
  section {
    background-size: cover;
    font-family: 'Noto Sans JP', sans-serif;
    color: #111;
    padding: 60px;
    text-align: left !important;
  }
  h1, h2, h3, h4 {
    color: #111;
    text-align: left !important;
    margin: 0;
    padding: 0 20px;
  }
  h1 { font-size: 2.2em; }
  h2 { font-size: 1.8em; }
  h3 { font-size: 1.5em; }
  p, ul, li, blockquote {
    font-size: 1.1em;
    text-align: left !important;
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
  .no-wrap-title {
    font-size: 1.6em;
    white-space: nowrap;
    text-align: left !important;
    margin-bottom: 0.5em;
  }
  .desc-left {
    text-align: left !important;
    font-size: 1.1em;
    margin-left: 1em;
    text-indent: -1em;
  }
  .bullet-list {
    margin-left: 0;
    padding-left: 1em;
    font-size: 1.1em;
  }
---

<!-- スライド1: タイトルスライド -->
<style scoped>
section {
  background-image: url('../GeminiCLIで資料作成/jera/デジタル部門_表紙.jpg');
  text-align: left !important;
}
</style>

# AI活用ローコード開発
#### 部門横断_人財育成・コーディング混成チーム

---

<!-- スライド2: 全体像 -->
<style scoped>
section {
  text-align: left !important;
}
.no-wrap-title {
  font-size: 2em;
  white-space: nowrap;
  text-align: left !important;
  margin-bottom: 0.5em;
}
.desc-left {
  text-align: left !important;
  font-size: 1.1em;
  margin-left: 2em;
}
</style>

<div class="no-wrap-title">AI活用の全体像</div>
<div class="desc-left">従来の開発プロセスを革新する5つのステップ</div>

---
見習いエンジニア向け：AI活用ローコード開発を導入
![width:1200px height:580px](スキルレベル.png)

---

<!-- スライド3: フェーズ1 -->
<style scoped>
section {
  text-align: left !important;
}
.no-wrap-title {
  font-size: 1.6em;
  white-space: nowrap;
  text-align: left !important;
  margin-bottom: 0.5em;
}
.bullet-list {
  margin-left: 0;
  padding-left: 1em;
  font-size: 1.1em;
}
</style>

<div class="no-wrap-title">1. RPAワークフロー作成フェーズ</div>
<div class="bullet-list">• ユーザー自身がローコード開発ツールを使用<br>
• 直感的なUIで業務ロジックを視覚化<br>
• RPAワークフロー.xamlとして保存・管理</div>

---
UiPath_GUI：直感的なUIで業務ロジックを視覚化
![width:1200px height:580px](UiPath_GUI.png)

---
UiPathワークフロー.xaml
![width:1200px height:580px](UiPath_xaml.png)

---

<!-- スライド4: フェーズ2 -->
<style scoped>
section {
  text-align: left !important;
}
.no-wrap-title {
  font-size: 1.6em;
  white-space: nowrap;
  text-align: left !important;
  margin-bottom: 0.5em;
}
.bullet-list {
  margin-left: 0;
  padding-left: 1em;
  font-size: 1.1em;
}
</style>

<div class="no-wrap-title">2. 設計書AI生成フェーズ</div>
<div class="bullet-list">• AIがRPAワークフロー.xamlの内容を解析<br>
• 構造化されたマークダウン形式で設計書.mdを生成<br>
• 可読性が高く、保守性に優れた文書を作成</div>

---
設計書.md：構造化されたマークダウン形式
![width:1200px height:580px](設計書.png)

---

<!-- スライド5: フェーズ3 -->
<style scoped>
section {
  text-align: left !important;
}
.no-wrap-title {
  font-size: 1.6em;
  white-space: nowrap;
  text-align: left !important;
  margin-bottom: 0.5em;
}
.bullet-list {
  margin-left: 0;
  padding-left: 1em;
  font-size: 1.1em;
}
</style>

<div class="no-wrap-title">3. コードAI生成フェーズ</div>
<div class="bullet-list">• 設計書.mdをベースにPythonコードを生成<br>
• 実行可能なワークフロー.pyファイルを作成<br>
• 高品質で保守性の高いコードを生成</div>

---
Pythonワークフロー.py：実行可能
![width:1200px height:580px](Python.png)

---

<!-- スライド6: フェーズ4 -->
<style scoped>
section {
  text-align: left !important;
}
.no-wrap-title {
  font-size: 1.6em;
  white-space: nowrap;
  text-align: left !important;
  margin-bottom: 0.5em;
}
.bullet-list {
  margin-left: 0;
  padding-left: 1em;
  font-size: 1.1em;
}
</style>

<div class="no-wrap-title">4. WebアプリAI生成フェーズ</div>
<div class="bullet-list">• 設計書.mdからシステム.htmlを生成<br>
• UIを含む完全なWebアプリを作成<br>
• レスポンシブデザインで様々なデバイスに対応</div>

---
Webアプリ 経費管理システム.html
![width:1200px height:580px](Webアプリ.png)

---

<!-- スライド7: フェーズ5 -->
<style scoped>
section {
  text-align: left !important;
}
.no-wrap-title {
  font-size: 1.6em;
  white-space: nowrap;
  text-align: left !important;
  margin-bottom: 0.5em;
}
.bullet-list {
  margin-left: 0;
  padding-left: 1em;
  font-size: 1.1em;
}
</style>

<div class="no-wrap-title">5. プレゼン資料AI生成フェーズ</div>
<div class="bullet-list">• 設計書.mdからスライド資料を作成<br>
• pdfやpptx形式で出力<br>
• 関係者への説明・共有に最適化された資料を生成</div>
