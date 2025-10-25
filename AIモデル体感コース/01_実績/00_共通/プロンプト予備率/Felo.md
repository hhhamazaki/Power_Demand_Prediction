## Overview

電力の安定供給を維持する上で極めて重要な指標であるOCCTO（電力広域的運営推進機関）の広域予備率を、機械学習を用いて高精度に予測するモデルの構築は、需給逼迫の早期警戒や効率的な電力運用に不可欠です。この予測モデルの精度は、入力する特徴量の質と量に大きく依存します。

本レポートでは、TEPCO管内を対象としたOCCTO予備率予測モデルの構築に必要な特徴量を「需要」「供給」「市場・系統」の3つの観点から網羅的に整理し、それぞれのデータの具体的な入手方法を詳述します。特に、OCCTOが提供するCSVダウンロード機能や、JEPX（日本卸電力取引所）が公開するAPI仕様書に基づいたプログラムによるデータ取得方法に焦点を当てます。これにより、安定的かつ自動化されたデータ収集パイプラインの設計と、それに続く高精度な予測モデル開発への道筋を明確に示します。

## 詳細レポート

### 広域予備率の定義と重要性

広域予備率とは、電力供給の余力を示す指標であり、電力の安定供給を評価する上で中心的な役割を果たします[8]。この値は、電力広域的運営推進機関（OCCTO）によって計算・公表されています[8][14]。予備率は以下の計算式で定義されます。

**予備率 (%) = (供給力 - 需要) / 需要 × 100**

ここで「供給力」は発電所の稼働可能容量の合計を指し、「需要」はその時点での電力消費量の予測値です。予備率が安定的に確保されていることは、発電所の計画外停止や需要の急増といった不測の事態に対応できることを意味します[6]。

特に、予備率が3%を下回ると「電力需給逼迫注意報」が発令され、節電協力が要請されるなど、社会経済活動に直接的な影響が及びます[8]。近年、再生可能エネルギーの導入拡大や燃料価格の変動により、予備率が低下する事態が頻発しており、2024年度にはマイナスを記録する日も現れました[6]。これは、電力不足、すなわち停電のリスクが予告されている状態を示します[6]。

![OCCTO（電力広域的運営推進機関）の広域予備率Web公表システムの画面[8]](https://de-denkosha.co.jp/datsutanso/wp-content/uploads/2025/08/DT0804-001-1024x513.jpg)

2025年1月からは、需給バランス評価の精度向上のため、週間および翌々日計画の広域予備率計算に「調整力必要量」が新たに計上されるよう変更されました[3]。これにより、予備率の定義がより実態に即したものとなり、予測モデルにおいてもこの変更を考慮する必要があります。

### 予測モデル構築のための特徴量とデータ入手方法

高精度な予備率予測モデルを構築するには、需要、供給、そして市場動向に関連する多様なデータを特徴量として組み込むことが不可欠です。以下に、主要な特徴量とその具体的なデータ入手方法を整理します。

| 分類 | 特徴量 | データソース | 入手方法 |
| :--- | :--- | :--- | :--- |
| **需要関連** | **過去の電力需要実績** (MW) | OCCTO 広域予備率Web公表システム | CSVダウンロード [5][10] |
| | **気象データ** (気温、湿度、日射量等) | 気象庁、気象情報提供事業者 | 気象庁ウェブサイト、専用API [1][39] |
| | **カレンダー情報** (曜日、祝日、季節) | - | プログラムで自動生成 |
| **供給関連** | **広域ブロック供給力** (MW) | OCCTO 広域予備率Web公表システム | CSVダウンロード [5][10] |
| | **発電設備の供給計画** (電源種別毎) | OCCTO 供給計画の取りまとめ | OCCTOウェブサイトで公開される報告書 [11] |
| | **再生可能エネルギー出力予測** | - | 気象予測データから独自に推計、または専門APIを利用 [1][39] |
| | **発電所の計画停止情報** | OCCTO 供給計画の取りまとめ | OCCTOウェブサイトで公開される報告書 [11] |
| **市場・系統** | **JEPXスポット市場価格** (円/kWh) | JEPX (日本卸電力取引所) | JEPXウェブサイト、公式API [16][33] |
| | **連系線利用状況** | OCCTO 広域予備率Web公表システム | CSVダウンロード（連系線情報） [2][5] |
| | **需給調整市場の約定結果** | OCCTO | OCCTOウェブサイトで公開される委員会資料等 [45] |

### プログラムによるデータ取得：APIとCSVダウンロードの活用

モデルの継続的な運用と精度維持のためには、手動でのデータ収集ではなく、プログラムによる自動化されたデータパイプラインの構築が鍵となります。

**OCCTO：CSVファイルの直接ダウンロード**

OCCTOの「広域予備率Web公表システム」は、Webサイト上での閲覧だけでなく、過去のデータをCSV形式でダウンロードする機能を提供しています[5][10]。この機能は、特定のURLにパラメータを付与することで、直接CSVデータを取得することが可能です[10]。

- **ダウンロード用URLの例**:
  `https://web-kohyo.occto.or.jp/kks-web-public/download/downloadCsv?jhSybt=02&tgtYmdFrom=2025/10/10&tgtYmdTo=2025/10/10`
  - `jhSybt`: 情報種別（例: `02`は翌々日ブロック情報）
  - `tgtYmdFrom`, `tgtYmdTo`: 対象期間

取得できるCSVファイルには、30分ごとの各エリア・広域ブロックの需要、供給力、予備力、予備率などが含まれています[10][23]。

```csv
"対象年月日","時刻","ブロックNo","エリア名","広域ブロック需要(MW)","広域ブロック供給力(MW)","広域ブロック予備力(MW)","広域予備率(%)","広域使用率(%)","エリア需要(MW)","エリア供給力(MW)","エリア予備力(MW)"
"2022/08/02","00:30","2","東京","50433.828","58811.602","8377.774","16.61","85.75","34906","40360","5454"
"2022/08/02","00:30","2","中部","50433.828","58811.602","8377.774","16.61","85.75","15527.828","17863.702","2335.874"
...
```

**JEPX：翌日市場取引システムAPIの活用**

JEPXは、翌日市場（スポット市場）の取引システムと連携するためのWeb-API仕様書を公開しています[33]。このAPIを利用することで、市場価格や約定結果などの重要な特徴量をプログラムで自動取得できます[21][37]。APIはJSON形式でデータを提供します[33]。

特に重要なAPIとして「市場結果照会（DAH1050）」があり、これによりエリアプライスやシステムプライスを取得できます[33]。

**API機能一覧（抜粋）**
| 機能名 | API名 | 説明 |
| :--- | :--- | :--- |
| 入札 | DAH1001 | 入札データをサーバに送信します。 |
| 約定照会 | DAH1004 | 通常入札の約定結果をダウンロードします。 |
| **市場結果照会** | **DAH1050** | **市場結果（エリアプライス等）をダウンロードします。** |
| 清算照会 | DAH9001 | 翌日市場の清算データをダウンロードします。 |

*出典: ＡＰＩ仕様書 （翌日市場取引システム）[33]*

APIリクエストとレスポンスは以下のようなJSON形式となります。

**リクエストボディ部（例）**
![入札リクエストのJSONデータ例[33]](https://api.felo.ai/images/s/17MUlepxBL)

**レスポンスボディ部（例）**
![約定結果照会のレスポンスJSONデータ例[33]](https://api.felo.ai/images/s/iey6H4DlXF)

これらのAPIを活用することで、需給の逼迫度合いを反映する市場価格をリアルタイムに近い形で特徴量に組み込むことが可能となり、予測精度を大幅に向上させることが期待できます[24][26]。

### モデルアーキテクチャと特徴量エンジニアリング

**モデル選択**
収集した多様な特徴量を効果的に学習させるため、勾配ブースティング木（Gradient Boosting Decision Tree）の一種である**LightGBM**や**XGBoost**の採用が推奨されます。これらのモデルは、数値データとカテゴリカルデータの混在に強く、特徴量間の複雑な非線形関係を捉える能力に長けています。

**特徴量エンジニアリング**
生のデータをそのままモデルに入力するのではなく、予測に有効な情報を引き出すための特徴量エンジニアリングが重要です。
- **ラグ特徴量**: 1日前、1週間前の同時刻の需要や予備率。電力需要の周期性を捉えます。
- **移動平均**: 過去3時間、24時間の需要や価格の移動平均。短期的なトレンドを平滑化します。
- **気象特徴量の非線形変換**: 気温の2乗項（冷暖房需要の非線形な増加を表現）や、気温と湿度の交互作用項（不快指数など）。
- **供給力の変動**: 計画停止容量や再エネ出力予測値を、総供給力に対する割合として正規化します。

### 結論と今後の展望

TEPCO管内におけるOCCTO予備率の機械学習による予測は、OCCTOやJEPXが提供する公的データを活用することで十分に実現可能です。成功の鍵は、CSVダウンロードや公式APIを駆使して、需要、供給、市場価格といった多角的なデータを安定的かつ自動的に収集するデータパイプラインを構築することにあります。

今後は、気象庁が提供するアンサンブル気象予測データを取り込み、予報の不確実性そのものを特徴量としてモデルに学習させることや[1]、デマンドレスポンスの発動実績などを加えることで、さらなる予測精度の向上が期待されます。このような高精度な予測モデルは、電力システムのレジリエンス強化と、再生可能エネルギーが主力となる未来の電力網の安定運用に大きく貢献するでしょう。
[1] https://www.sciencedirect.com/science/article/pii/S2352484725002458
[2] https://web-kohyo.occto.or.jp/kks-web-public/
[3] https://www.occto.or.jp/occtosystem2/oshirase/2024/241218_oshirase.html
[4] https://www.spglobal.com/commodity-insights/en/news-research/latest-news/natural-gas/040121-most-japan-regions-to-have-low-feb-2022-reserve-power-supply-capacity-occto
[5] https://web-kohyo.occto.or.jp/kks-web-public/download
[6] https://project.nikkeibp.co.jp/energy/atcl/19/feature/00001/00099/
[7] https://www.cmegroup.com/education/articles-and-reports/introduction-to-the-japanese-power-market.html
[8] https://de-denkosha.co.jp/datsutanso/trivia/wide-area-power-reserve/
[9] https://www.renewable-ei.org/en/activities/column/REupdate/20250818.php
[10] https://qiita.com/99nyorituryo/items/87096493cc657f4fc726
[11] https://beyond-coal.jp/en/news/occto-electricity-supply-plan2024/
[12] https://x.com/occto_jp/status/1973982528764866930
[13] https://japanenergyhub.com/news/occto-fy2025-ten-year-power-demand-forecast/
[14] https://ene-fro.com/article/ef458_a1/
[15] https://powergrid.chuden.co.jp/denkiyoho/index.html
[16] https://www.jepx.jp/electricpower/market-data/spot/
[17] https://web-kohyo.occto.or.jp/kks-web-public/
[18] https://www.jepx.jp/system/documents/pdf/dah_api_specifications.pdf?timestamp=1759104000028
[19] https://note.com/takuroumi/n/n2894f793771b
[20] https://qiita.com/InvestorX/items/f1649d046a8405bdca8e
[21] https://www.occto.or.jp/occtosystem2/renkeihoushiki.html
[22] https://enechain.co.jp/news/enechain-to-offer-esquarelive-for-jepx-in-2026
[23] https://qiita.com/99nyorituryo/items/87096493cc657f4fc726
[24] https://project.nikkeibp.co.jp/ms/atcl/19/news/00001/04200/?ST=msb
[25] https://sgforum.impress.co.jp/article/3243
[26] https://www.jwa.or.jp/service/weather-and-data/weather-and-data-03/
[27] https://sgforum.impress.co.jp/article/3243?page=0%2C2
[28] https://www.enegaeru.com/10-yearforecastofjpex-prices
[29] https://www.mlit.go.jp/report/press/road01_hh_001930.html
[30] https://qiita.com/darshu/items/eae3385fcba93e62e5c9
[31] https://www.jepx.jp/system/documents/
[32] https://kankyo-ichiba.jp/
[33] https://www.jepx.jp/system/documents/pdf/dah_api_specifications.pdf?timestamp=1759104000028
[34] https://www.occto.or.jp/occtosystem2/renkeihoushiki.html
[35] https://www.jepx.jp/system/documents/pdf/nf_api_specifications.pdf?timestamp=1759104000030
[36] https://www.occto.or.jp/keitoujouhou/
[37] https://enechain.co.jp/news/enechain-to-offer-esquarelive-for-jepx-in-2026
[38] https://www.occto.or.jp/occtosystem2/kikaku_shiyou/index.html
[39] https://weather-jwa.jp/service/eneapi
[40] https://qiita.com/99nyorituryo/items/87096493cc657f4fc726
[41] https://www.enegaeru.com/about-jepx
[42] https://note.com/takuroumi/n/n2894f793771b
[43] https://www.jwa.or.jp/news/2017/08/4507/
[44] https://www.enegaeru.com/procedures-keypointsforgridinterconnectionapplication
[45] https://www.eprx.or.jp/contact/jukyuchoseishijo/faq.html