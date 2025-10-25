[Markdownプレビューのカスタマイズ #mermaid - Qiita](https://qiita.com/Lulu-Lemur/items/7c0aa3d943efc75b703a)

## テーマの編集

1. VSCodeの拡張機能「Markdown Preview Enhanced」をインストール
2. 「Ctrl + ,」で設定を開く
3. `Markdown Preview Enhanced:preview theme`
4. テーマなどを好みのものに変更

## カスタムCSSの設定方法

1. 「Ctrl + Shift + P」で検索欄を出す
2. `Markdown Preview Enhanced: Customize CSS`
3. `style.less`が開くので編集

```
/* Please visit the URL below for more information: */
/*   https://shd101wyy.github.io/markdown-preview-enhanced/#/customize-css */ 

.markdown-preview.markdown-preview {
@linkcolor : #6DC1FF;
@themecolor : #224B8B;
@accentcolor : #ff8c00;
h1 {
  background-color: #21305f;  /* 薄い水色 */
  color: #FFFFFF;                /* 黒文字 */
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 30px;
}

h2 {
  position: relative;
  font-size: 1.8em;
  color: #FFFFFF;
  margin-bottom: 20px; /* 下線スペース確保 */
}

h2::before {
  content: "";
  position: absolute;
  left: 0;
  bottom: 0;          /* 親の下端に合わせる */
  width: 100%;
  border-bottom: 1px solid #c7def0; /* 下の白線 */
}

h2::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: 0;          /* 親の下端に合わせる */
  width: 30%;
  border-bottom: 3px solid #ff9800; /* 上のオレンジ線 */
}


h3 {
  font-size: 1.4em;
  // padding: 0.2em;/*文字周りの余白*/
  padding-left: 0.9em;
  color: #FFFFFF;/*文字色*/
  border-left: solid 8px @themecolor;/*左線（実線 太さ 色）*/
}
h4 {
  font-size: 1.1em;
  // padding: 0.2em;/*文字周りの余白*/
  padding-left: 0.9em;
  color: #FFFFFF;/*文字色*/
  border-left: solid 2px #545466;/*左線（実線 太さ 色）*/
}


/* コードブロック全体 */
// pre, code {
//   font-family: "Fira Code", Consolas, monospace;
//   font-size: 14px;
//   line-height: 1.5;
//   color: #ffffff;         /* 通常文字は白 */
//   background: #000000;    /* 黒背景 */
//   padding: 8px 12px;
//   border-radius: 6px;
//   overflow-x: auto;
//   display: block;
//   white-space: pre-wrap;  /* 折り返し有効 */
// }
/* ブロックコード（```で囲む） */
pre, pre code {
  display: block;
  background: #000000;     /* 背景黒 */
  color: #ffffff;          /* 文字白 */
  padding: 8px 12px;
  border-radius: 6px;
  overflow-x: auto;
  white-space: pre-wrap;
}

/* インラインコード（`a` のようなもの） */
code:not(pre code) {
  display: inline;          /* 行全体ではなく文字だけハイライト */
  background: #000000;      /* 背景黒 */
  color: #ffffff;           /* 文字白 */
  padding: 0 4px;           /* 文字周りの余白 */
  border-radius: 3px;
}


/* コメント (#で始まる行など) */
code .comment {
  color: #888888;          /* 灰色 */
  font-style: italic;
}

/* コマンドやキーワード */
code .keyword {
  color: #ff9500;          /* オレンジ系 */
  font-weight: bold;
}

/* 数値、パス、メールアドレスなど */
code .number, code .path {
  color: #00bfff;          /* 水色系 */
}

/* シェルのプロンプト（ユーザー名や $ 等） */
code .prompt {
  color: #50fa7b;          /* 緑 */
  font-weight: bold;
}

/* コマンド置換 $(...) の色を白に */
code .subst, code .shell-subst {
  color: #f30d0d; /* 通常文字と同じ白 */
}
}
```

## Mermaidテーマ設定

mermaidで作図すると線が背景に溶け込んでしまっていたので、ダークモードに適応してくれるよう設定変更。  
`"markdown-preview-enhanced.mermaidTheme": "dark"`を検索

