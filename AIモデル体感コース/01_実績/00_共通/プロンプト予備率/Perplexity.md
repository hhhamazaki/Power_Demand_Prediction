# TEPCO管内OCCTO範囲で、OCCTO予備率を予測する機械学習モデル構築。

***

### 【OCCTO予備率予測の必要特徴量と入手方法】

| 特徴量カテゴリ | 代表的な特徴量 | 主な入手方法・情報元 |
| :-- | :-- | :-- |
| 需要関連 | ピーク負荷予測値<br>過去需要実績<br>カレンダー情報（季節・曜日等） | - OCCTO「系統情報サービス」<br>（CSVダウンロード可）[^1][^2]<br>- TEPCO「でんき予報」公式サイト（当日～週次実績/予測）[^3] |
| 気象関連 | 気温、湿度、日射量、風速<br>気象予測値 | - 気象庁オープンデータ<br>- 日本気象協会API/CSV[^4]<br>- 一部公的/民間API（Weathermap, tenki.jpなど）[^5] |
| 供給関連 | 稼働発電容量（火力/原子力/水力/揚水）<br>設備点検・計画停止予定 | - OCCTO/TEPCO発電設備情報（定期レポート・年度計画報告資料）<br>- OCCTO広域予備率Web公表システム（CSVダウンロード）[^6][^1] |
| 再生可能エネルギー関連 | 太陽光・風力出力予測<br>出力実績 | - OCCTO/TEPCOの再エネ出力報告・予測データ<br>- 再エネ事業者・送配電会社公開データ[^5] |
| 調整力・需給バランス関連 | 需要予測誤差統計値<br>迅速起動可容量<br>DP/DR実行量 | - OCCTO・経済産業省/調整力報告・需給分析資料[^7] |
| 系統・運用制約 | 系統転送可能容量<br>連系線容量<br>エリア間送電状況 | - OCCTO系統情報サービス[^2]<br>- 広域予備率Web公表システム[^6] |


***

### 各特徴量の具体的な入手手順・データ形式

#### 需要・供給・予備力（エリア毎・30分 or 1時間単位）

- OCCTO広域予備率Web公表システムで**CSVダウンロード可**

```
https://web-kohyo.occto.or.jp/kks-web-public/
CSV出力例（列名）：日付,時刻,エリア名,需要(MW),供給力(MW),予備力(MW),予備率(%)
```


#### 気象データ

- **気象庁オープンデータ（CSV形式/REST API）**で過去・予測値取得
- **日本気象協会API/CSV**や外部サービスAPIで30分-1時間ごとの気象情報取得可能[^4][^5]


#### 発電設備・再エネ出力実績

- TEPCO公式またはOCCTOの発電計画・設備点検スケジュール/運用報告参照
- 一部は年度計画資料（PDF/Excel等）の数値を抽出・整理


#### 再生可能エネルギー出力/予測

- 再エネ事業者サイトや送配電サイトで広域 or 地域の発電出力実績・予測一覧をCSV等でダウンロード[^5]


#### 調整力・需給バランス情報

- 経済産業省の需給実績評価/LOLP・LOLE/EUE推計値や調整力市場情報として一部報告資料から抜粋[^7]


#### 系統制約・系統運用情報

- OCCTO「系統情報サービス」のCSVダウンロード機能で広域送電容量（連系線等）やエリア運用制約を取得

***

### 運用上のポイント

- **データ取得はCSV/APIで自動化可能**（Pythonでスクリプト化推奨）
- **全特徴量共通：日付・時刻カラム必須、エリア名一意化推奨**
- **データ統合時はタイムスタンプ単位で結合**
- 統合後データ整形・欠損処理、不整合補正など前処理実装が必須

***

### 参考：入手先まとめURL例

- OCCTO広域予備率Web公表：https://web-kohyo.occto.or.jp/kks-web-public/
- でんき予報（TEPCO）：https://www.tepco.co.jp/forecast/
- OCCTO系統情報サービス：https://www.occto.or.jp/keitoujouhou/
- 気象庁オープンデータ：https://www.data.jma.go.jp/
- 経産省電力・ガス委員会資料：https://www.meti.go.jp/shingikai/enecho/denryoku_gas/

***

これらを統合することで、TEPCO管内OCCTO予備率予測の高精度な機械学習モデルが構築可能です。[^6][^1][^2][^7][^4][^5]
<span style="display:none">[^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^20][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://qiita.com/99nyorituryo/items/87096493cc657f4fc726

[^2]: https://note.com/takuroumi/n/n2894f793771b

[^3]: https://www.tepco.co.jp/forecast/

[^4]: https://www.wxbc.jp/wp-content/uploads/2019/12/seminar_191203_fukuoka_03.pdf

[^5]: https://www.nedo.go.jp/content/100905936.pdf

[^6]: https://web-kohyo.occto.or.jp/kks-web-public/

[^7]: https://www.rieti.go.jp/jp/publications/dp/19j060.pdf

[^8]: https://www.meti.go.jp/shingikai/enecho/denryoku_gas/denryoku_gas/pdf/069_03_00.pdf

[^9]: https://www.enecho.meti.go.jp/committee/council/basic_policy_subcommittee/mitoshi/cost_wg/pdf/cost_wg_20250206_01.pdf

[^10]: https://www.nedo.go.jp/content/800026067.pdf

[^11]: https://www.env.go.jp/content/900449402.pdf

[^12]: https://repos.env.go.jp/web/dat/report/r02-01/r02-01_whole.pdf

[^13]: https://www.nedo.go.jp/content/800012502.pdf

[^14]: https://www.renewable-ei.org/pdfdownload/activities/REI_Agora_Japan_grid_FullREport_JP_WEB.pdf

[^15]: https://www.nedo.go.jp/content/100925949.pdf

[^16]: https://www.egc.meti.go.jp/activity/emsc_electricity/pdf/0014_07_02.pdf

[^17]: https://www.tepco.co.jp/about/ir/library/annual_report/pdf/202210tougou5-j.pdf

[^18]: https://www.kantei.go.jp/jp/singi/index/bukka/pdf/siryou1-1.pdf

[^19]: https://www.enegaeru.com/30-minutedemanddataanalysisguide

[^20]: https://sucra.repo.nii.ac.jp/record/18193/files/GD0000936.pdf

