
## 概要

このドキュメントは、ワークフロー `Main.xaml`（リポジトリ内の現行ファイル）の構成を解析し、UiPath Studio 上で同等のワークフローを作成する手順を `サンプル.md` の様式に合わせて丁寧に記載したものです。

本ワークフローの主な処理フロー:
- プロジェクト相対パス `data.csv` を `Read CSV File` で読み込み、DataTable（変数名: `_out_ReadCsvFile_1__DataTable`）に格納する。
- 読み取った DataTable をそのまま `Append Csv File` を使って `データ.csv` に追記する。

（備考）元の XAML は `ueab:SequenceX` をルートに持ち、内部に `Sequence` を含んでいます。表示名は `Single Excel Process Scope`、内部 Sequence の DisplayName は `グループ` です。

## 前提条件

- UiPath Studio（プロジェクト形式）
- 必要なパッケージがインストールされていること（少なくとも `UiPath.CSV.Activities` / `UiPath.System.Activities` / `UiPath.Excel.Activities` 等）
- プロジェクト フォルダに以下のファイルが存在すること:
  - `data.csv`（読み取り元）
  - （追記先）`データ.csv` は存在してもよいし、無ければ新規作成されます

## 変数一覧（Main.xaml に定義されているもの）

- `Notes` : IWorkbookQuickHandle
  - XAML 内のデフォルト値: new WorkbookQuickHandle(workbookPath:="Project_Notebook.ja.xlsx", visible:=True, autoSave:=False, createNew:=True, readOnly:=False, isWorkspace:=True)
  - 本ワークフローでは参照用またはテンプレートとして配置されている可能性があります。
- `_out_ReadCsvFile_1__DataTable` : DataTable — `Read CSV File` の出力先

## アクティビティ一覧（順序・プロパティ）

1. ueab:SequenceX (DisplayName="Single Excel Process Scope")
   - ルートのコンテナ。内部に `Sequence` を持つ。
2. Sequence (DisplayName="グループ")
   - `ReadCsvFile` と `AppendCsvFile` を含む。
3. ReadCsvFile
   - DisplayName: `CSV を読み込み`
   - FilePath: `data.csv`（プロジェクト相対パス）
   - Delimitator / Delimiter: `Comma`
   - IncludeColumnNames: `False`
   - Output: `_out_ReadCsvFile_1__DataTable`
   - 注意: XAML 内では `ui:ReadCsvFile` 要素として定義されている。
4. AppendCsvFile
   - DisplayName: `CSV に追加`
   - FilePath: `データ.csv`（プロジェクト相対パス）
   - Delimitator: `Comma`
   - DataTable: `_out_ReadCsvFile_1__DataTable`

## UiPath Studio 上での作成手順（ステップ・バイ・ステップ）

1. UiPath Studio で新規プロジェクト、または対象プロジェクトを開く。
2. `Main.xaml` を新規作成するか既存の `Main.xaml` を開き、ルートに `Sequence`（または `Sequence` をラップする `SequenceX` 相当）を追加します。
   - 表示名（DisplayName）: `Single Excel Process Scope` とする。
3. 変数タブで以下の変数を定義します:
   - `Notes` : IWorkbookQuickHandle（必要に応じてデフォルト値を設定。XAML では WorkbookQuickHandle のインスタンスが Default に設定されている）
   - `_out_ReadCsvFile_1__DataTable` : DataTable
4. ルート `Sequence` の中にさらに `Sequence`（DisplayName: `グループ`）を入れ、そこでアクティビティを順に配置します。
5. `Activities` パネルから `Read CSV`（またはプロジェクトで使用されている `ReadCsvFile`）を `グループ` の先頭に追加します。
   - プロパティを設定:
     - `FilePath` に `data.csv` を指定（プロジェクト相対パス）
     - `Delimiter` を `Comma` に設定
     - `IncludeColumnNames` を `False` に設定（XAML に合わせる場合）
     - `Output` に `_out_ReadCsvFile_1__DataTable` を指定
6. `Append CSV`（`AppendCsvFile`）アクティビティを追加し、次のプロパティを設定します:
   - `FilePath` に `データ.csv` を指定
   - `Delimiter` を `Comma` に設定
   - `DataTable` に `_out_ReadCsvFile_1__DataTable` を指定
7. 必要なら ViewState や表示名（DisplayName）を XAML と同等に整える。VisualTree の階層が `SequenceX` → `Sequence` → アクティビティ の順になっていることを確認する。
8. 保存して、プロジェクトのルートに `data.csv` を置いた状態でデバッグ実行する。

## テスト手順

1. プロジェクト フォルダに `data.csv` が存在することを確認する。
2. UiPath Studio で `Main.xaml` を開き、デバッグを開始する。
3. 実行後、同じフォルダに `データ.csv` が作成されているか、既存ファイルへ追記されているかを確認する。
4. 読み書きが期待通りになっていない場合はログや例外メッセージを確認する。

## よくあるトラブルと対処

- `Read CSV` が失敗する / DataTable が null になる
  - ファイルパス（相対パス/絶対パス）の確認、ファイルの存在とアクセス権を確認する。
  - CSV のエンコーディング（Shift-JIS / UTF-8 等）による影響があるため、アクティビティの `Encoding` を設定してみる。
- 追記先の `データ.csv` が壊れる / 期待した列順や区切りにならない
  - 区切り文字（Delimiter）が正しいか確認する。XAML は `Comma` を指定している。
  - ヘッダー行の有無（IncludeColumnNames）やカラム順を明示的に制御する必要がある場合、先に `Write CSV` でヘッダを書き、`Append` を使うなど設計を見直す。
- 既定の `Notes` 変数が不要な場合
  - XAML にテンプレート的に配置されている可能性があるため、不要であれば削除しても良い（ただし参照されていないか確認）。

## 補足（XAML の特記事項）

- 元の XAML では多数の名前空間参照（`TextExpression.NamespacesForImplementation`）とアセンブリ参照が含まれています。UiPath が自動で付与する要素なので、基本的には気にする必要はありませんが、外部アクティビティを使う場合は該当パッケージがプロジェクトにあることを確認してください。
- `ReadCsvFile` の `IncludeColumnNames` が `False` に設定されている点は注意が必要です。ヘッダーを期待する downstream 処理がある場合は `True` にするなど調整してください。

---

