
## 概要

このドキュメントは、ワークフロー `Main.xaml` の構成と、UiPath Studio 上で同等のワークフローを作成する手順を丁寧に説明します。

主な処理フロー:
- CSV ファイル `Data\HE_KKS.csv` を読み込み、DataTable `Dt_HE_KKS` に格納。
- 文字列変数 `FileName` に値（例: `HE_A100`）を設定。
- `Dt_HE_KKS` の列 "機能場所" が `FileName` で始まる行だけを抽出して `DtFileName` に保存。
- 抽出結果 `DtFileName` を `Data\{FileName}.csv` として書き出す。

## 前提条件

- UiPath Studio（プロジェクト形式）
- 必要なパッケージ（例: UiPath.System.Activities, UiPath.CSV.Activities, UiPath.Excel.Activities）がプロジェクトにインストールされていること
- プロジェクト フォルダに以下のファイル/フォルダが存在すること:
  - `Data\HE_KKS.csv`（入力）

## 変数一覧（Main.xaml に定義されているもの）

- `Notes` : IWorkbookQuickHandle（デフォルト値: new WorkbookQuickHandle(... )）。本ワークフローでは参照用に配置されている可能性あり。
- `Dt_HE_KKS` : DataTable — `Read CSV File` の出力先
- `FileName` : String — 出力ファイル名（拡張子なし）。例: `HE_A100`
- `DtFileName` : DataTable — フィルタ後の出力用

## アクティビティ一覧（順序）

1. Sequence (DisplayName="Single Excel Process Scope")
2. Read CSV File
   - DisplayName: CSV を読み込み
   - FilePath: `Data\HE_KKS.csv`
   - Delimitator: `Comma`
   - Output: `Dt_HE_KKS`
3. Multiple Assign
   - DisplayName: 複数代入
   - 操作: `FileName = "HE_A100"`（AssignOperation）
4. Filter Data Table
   - DisplayName: データ テーブルをフィルター
   - DataTable: `Dt_HE_KKS`
   - OutputDataTable: `DtFileName`
   - FilterRowsMode: Keep
   - SelectColumnsMode: Remove
   - Filters: 1 条件
     - Column: `["機能場所"]`
     - Operator: `STARTSWITH`
     - Operand: `[FileName]`
     - BooleanOperator: `And`（単一条件でも指定されている）
5. Write CSV File
   - DisplayName: CSV に書き込み
   - DataTable: `DtFileName`
   - FilePath: `["Data\\" + FileName + ".csv"]`（式）
   - AddHeaders: True
   - Delimitator: `Comma`
   - ShouldQuote: True

## UiPath Studio 上での作成手順（ステップ・バイ・ステップ）

1. 新規プロジェクトまたは既存プロジェクトを開く。
2. メインのワークフロー（例: `Main.xaml`）を開き、ルートに `Sequence` を配置する。表示名を「Single Excel Process Scope」とする。
3. 変数タブで以下を定義する:
   - `Dt_HE_KKS` : DataTable
   - `FileName` : String
   - `DtFileName` : DataTable
   - （必要なら）`Notes` : IWorkbookQuickHandle（デフォルト値は XAML にあわせて設定）
4. `Activities` パネルから `Read CSV`（CSV を読み込むアクティビティ）を追加し、プロパティを設定する:
   - `FilePath` に `Data\\HE_KKS.csv` を指定（プロジェクト相対パス）
   - `Delimiter` を `Comma` にする
   - `Output` に `Dt_HE_KKS` を指定
5. `Multiple Assign`（複数代入）を配置し、AssignOperation を追加して `FileName` に文字列 `HE_A100` を代入する。
   - もしくは単純な `Assign` で `FileName = "HE_A100"` としても良い。
6. `Filter Data Table` を追加し、以下を設定する:
   - `DataTable` に `Dt_HE_KKS`
   - `OutputDataTable` に `DtFileName`
   - `FilterRowsMode` を `Keep`
   - `SelectColumnsMode` を `Remove`（列指定で絞るなら使用）
   - `Filters` を追加: カラムに `"機能場所"` を指定（XAML の表現では `['機能場所']` のように指定されている）、Operator を `StartsWith`、Operand に `FileName` を指定
     - UiPath のエディタでは Operand に変数 `FileName` を選択する。
7. `Write CSV` を追加し、`DataTable` に `DtFileName`、`FilePath` に式 `"Data\\" + FileName + ".csv"` を設定する。`AddHeaders` を True にする。
8. 保存してデバッグ実行。`

## テスト手順

1. `Data` フォルダに `HE_KKS.csv` があることを確認。
2. `FileName` を `HE_A100` のまま実行する。
3. 実行後、`Data\HE_A100.csv` が作成され、`機能場所` 列が `HE_A100` で始まる行のみ含まれていることを確認する。

## よくあるトラブルと対処

- CSV のエンコーディングが原因で読み込めない: `Read CSV` の `Encoding` 設定やファイルの BOM を確認する。
- カラム名の表記ゆれ: `機能場所` の全角/半角スペースや余分な不可視文字に注意。XAML では `"機能場所"` と正確に一致させる。
- `Dt_HE_KKS` が null になる: `Read CSV` が失敗している可能性。ファイルパスや存在確認、アクセス権を確認する。
- 出力ファイルが作成されない: `Write CSV` の `FilePath` 式が正しく評価されているか確認（プロジェクト相対パス vs 絶対パス）。
- 必要パッケージがない: `UiPath.CSV.Activities` や `UiPath.System.Activities` 等がインストールされていることを確認する。

## 補足（XAML の特記事項）

- `FilePath` に `Data\\HE_KKS.csv` をハードコードしている点、及び `Write CSV` で式 `["Data\\"+FileName+".csv"]` を使っている点に注意。
- `Filter Data Table` の `Column` と `Operand` が InArgument で指定されており、XAML 内では `[
  "機能場所"
]` や `FileName` の InArgument 参照として表現されている。

---

