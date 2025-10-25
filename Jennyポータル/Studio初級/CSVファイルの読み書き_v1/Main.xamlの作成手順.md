
## 概要

このドキュメントは、ワークフロー `Main.xaml` の構成と、UiPath Studio 上で同等のワークフローを作成する手順を丁寧に説明します。

本ワークフローの主な処理:
- プロジェクト直下の `data.csv` を `Read CSV File` で読み込み、DataTable に格納する。
- 読み込んだ DataTable をそのまま `Write CSV File` で `データ.csv` として書き出す（ヘッダー付き、引用あり）。

## 前提条件

- UiPath Studio（プロジェクト形式）
- 必要なパッケージ（例: `UiPath.System.Activities`, `UiPath.CSV.Activities`, `UiPath.Excel.Activities`）がプロジェクトにインストールされていること
- プロジェクト フォルダに以下のファイルが存在すること:
  - `data.csv`（読み込み元）

## 変数一覧（`Main.xaml` に定義されているもの）

- `Notes` : IWorkbookQuickHandle（デフォルト値: new WorkbookQuickHandle(workbookPath:="Project_Notebook.ja.xlsx", visible:=True, autoSave:=False, createNew:=True, readOnly:=False, isWorkspace:=True)）。参照用に配置されています。
- `_out_ReadCsvFile_1__DataTable` : DataTable — `Read CSV File` の出力先

※ 本 XAML は変数名に自動生成風の `_out_ReadCsvFile_1__DataTable` を使用しています。実運用では分かりやすい変数名（例: `Dt_Input`）に変更しても構いません。

## アクティビティ一覧（順序）

1. SequenceX (DisplayName="Single Excel Process Scope")
   - SequenceX の内部に通常の `Sequence (DisplayName="グループ")` が入っています。
2. Read CSV File
   - DisplayName: CSV を読み込み
   - FilePath: `data.csv`
   - Delimitator / Delimiter: `Comma`
   - Output: `_out_ReadCsvFile_1__DataTable`
3. Write CSV File
   - DisplayName: CSV に書き込み
   - DataTable: `_out_ReadCsvFile_1__DataTable`
   - FilePath: `データ.csv`
   - AddHeaders: True
   - Delimitator: `Comma`
   - ShouldQuote: True

## UiPath Studio 上での作成手順（ステップ・バイ・ステップ）

1. 新規プロジェクトまたは既存プロジェクトを開く。プロジェクトルートに `data.csv` を配置しておく。
2. `Main.xaml` を作成または開き、ルートに `Sequence` を配置する。表示名を `Single Excel Process Scope` にする（本 XAML では `ueab:SequenceX` を使用していますが、通常の `Sequence` で代替可能です）。
3. 変数タブで以下を定義する:
   - `Notes` : IWorkbookQuickHandle（必要ならデフォルト値を XAML と合わせて設定）
   - `_out_ReadCsvFile_1__DataTable` : DataTable
4. `Activities` パネルから `Read CSV`（CSV を読み込むアクティビティ）を追加し、プロパティを設定する:
   - `FilePath` に `data.csv` を指定（プロジェクト相対パス）
   - `Delimiter` を `Comma` にする
   - `Output` に `_out_ReadCsvFile_1__DataTable` を指定
5. `Write CSV` を追加し、プロパティを設定する:
   - `DataTable` に `_out_ReadCsvFile_1__DataTable` を指定
   - `FilePath` に `データ.csv` を指定（プロジェクト相対パス）
   - `AddHeaders` を True にする
   - `Delimiter` を `Comma` にする
   - `ShouldQuote` を True にする（本 XAML の設定に合わせる）
6. 必要に応じて `Sequence` のネスト（例: `グループ` という表示名の `Sequence`）を作成し、上記アクティビティを内包させる。
7. 保存してデバッグ実行。

## テスト手順

1. プロジェクトルートに `data.csv` が存在することを確認する（内容は任意の CSV）。
2. `Main.xaml` を実行する。
3. 実行後、プロジェクトルートに `データ.csv` が作成され、`data.csv` と同等の内容（ヘッダー付き）が出力されていることを確認する。

## よくあるトラブルと対処

- CSV が読み込めない/文字化けする: `Read CSV` の `Encoding` を確認するか、ファイルの BOM をチェックする。
- ファイルパスの誤り: `data.csv` と `データ.csv` のパスがプロジェクト相対または絶対で正しいか確認する。
- 出力が空になる/想定と違う: `Read CSV` の出力先変数名が間違っていないか、変数のスコープがアクティビティよりも上位になっているか確認する。
- 必要パッケージが不足: `UiPath.CSV.Activities` や `UiPath.System.Activities` 等がインストールされているか確認する。

## 補足（XAML の特記事項）

- 本 XAML は `ueab:SequenceX`（Single Excel Process Scope）→ `Sequence`（グループ）という構造を取っています。UiPath Studio の通常の `Sequence` で同じ動作を再現できます。
- `Notes` 変数は Workbook 用のハンドルとして配置されていますが、このワークフローの主要処理（CSV の読み書き）では使われていません。将来的に Excel 処理を追加する場合に利用される想定です。

---

