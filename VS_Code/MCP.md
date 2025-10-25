[Discover and install MCP Servers in VS Code](https://code.visualstudio.com/mcp)

MarkItDown

PDFドキュメント全文を末尾まで一字一句正確に解析しろ。
Markitdown-mcpを使って抜け漏れ無くMarkdown（.md）ファイルに変換しろ。

[MarkItDown-MCPをuvでセットアップする #Claude - Qiita](https://qiita.com/samplebang/items/7726cb8d5176144dd3e8)

## MarkItDown-MCPのインストール方法

これからMarkItDown-MCPを使う方のために、インストール方法を説明します。

1. MarkItDown-MCP 本体をインストール
2. uv をインストール　←ここから公式手順と異なる
3. uv で初回セットアップを実行　
4. Claude Desktop の設定ファイルを編集

### 1. MarkItDown-MCP 本体をインストール

```
py -m pip install markitdown-mcp
```

### 2. uv をインストール

uv は、一時的な仮想環境を自動で構築し、ツールを実行するための便利なユーティリティです。

```
choco install uv -y
```

### 3. uv で初回セットアップを実行

このコマンドを実行すると、uv が内部に小規模な仮想環境を作成し、markitdown-mcp の実行に必要なコンポーネントをダウンロード・準備します。

```
uv tool run markitdown-mcp --help
```

初回実行時: ネットワーク環境にもよりますが、30秒〜60秒程度かかることがあります。これは、必要なファイル（依存関係）をダウンロードし、キャッシュを生成するためです。  
2回目以降: キャッシュが利用されるため、数秒で起動します。

## 使用方法

Claude Desktop を再起動したら、チャット欄に以下のようなコマンドを入力してみましょう。

```
convert_to_markdown("https://example.com")
```

ローカルのPDFファイルを指定する場合は以下のように指示してあげればOKです。 (ファイルパスはご自身の環境に合わせて変更してください)

```
convert_to_markdown("file:///C:/Users/ユーザー名/Documents/test.pdf")
```



