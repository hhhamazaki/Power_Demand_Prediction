# 🔋 TEPCO管内OCCTO範囲における予備率予測モデル構築：特徴量設計と入手方法

## 1. 予備率の定義と重要性

**予備率（％）=（供給力 − 予測需要）÷ 予測需要 × 100**

OCCTOの予備率は電力の安定供給を評価する上で極めて重要な指標です。特に3%を下回ると「電力需給逼迫注意報」が発令され、社会経済活動に直接的な影響を与えます。2024年度にはマイナスを記録する日も現れており、高精度な予測モデルの必要性が高まっています。

## 2. 機械学習モデル構築に必要な特徴量とデータ入手方法

### 🎯 需要関連特徴量

#### 2.1 気象データ（最重要要因）

**データソース** | **入手方法** | **特徴量** | **更新頻度**
---|---|---|---
**日本気象協会（JWA）ENeAPI** | [専用API](https://weather-jwa.jp/service/eneapi) | 気温、湿度、日射量、風速、降水量（9kmメッシュ） | 毎時更新
**気象庁XML API** | [高度利用ポータル](http://www.data.jma.go.jp/developer/index.html) | アメダス観測値、メッシュ予報データ | 10分毎～1時間毎
**民間気象サービス** | Weather X API（日本気象協会） | 高解像度気象予測データ | 毎6時間更新

**具体的な特徴量設計：**
```python
# エネルギー関連特徴量の例
temp_squared = temperature ** 2  # 空調負荷の非線形関係
comfort_index = 0.85 * temperature + 0.15 * humidity  # 不快指数
hdd_cdd = calculate_heating_cooling_degree_days(temperature)  # 暖房・冷房度日
```

#### 2.2 過去電力需要実績

**データソース** | **入手方法** | **フォーマット**
---|---|---
**TEPCO過去電力使用実績** | [でんき予報](https://www.tepco.co.jp/forecast/html/download-j.html) | CSV（5分間隔、1時間平均）
**OCCTO広域予備率システム** | [CSVダウンロード](https://web-kohyo.occto.or.jp/kks-web-public/download) | 30分毎エリア別需要データ

### ⚡ 供給関連特徴量

#### 2.3 発電設備・供給力データ

**データソース** | **入手方法** | **データ内容**
---|---|---
**OCCTO設備運用計画** | 公開委員会資料、月次報告書 | 火力・原子力・水力・揚水設備容量
**OCCTO供給計画取りまとめ** | 年次公開レポート | 電源種別計画容量、定期点検スケジュール
**再エネ出力予測** | 気象データから独自推計 + JEPX再エネインデックス | 太陽光・風力発電出力予測

#### 2.4 調整力・需給バランス情報

**調整力データ** | **データソース** | **取得方法**
---|---|---
迅速起動可能リソース容量 | OCCTO需給調整力検討会資料 | 月次委員会資料PDF
需給調整市場調達状況 | OCCTO公開資料 | 市場結果公表データ
デマンドレスポンス実施可能量 | TEPCO・各社公開データ | Webスクレイピング

### 💹 市場・系統制約関連特徴量

#### 2.5 JEPX市場データ（極めて重要）

**JEPX APIを活用した自動データ取得**

JEPXは[翌日市場取引システムAPI仕様書](https://www.jepx.jp/system/documents/pdf/dah_api_specifications.pdf)を公開しており、以下のAPIが利用可能です：

**主要API一覧**
```json
{
  "市場結果照会": "DAH1050",  // エリアプライス・システムプライス取得
  "約定照会": "DAH1004",      // 約定結果ダウンロード  
  "清算照会": "DAH9001"       // 清算データダウンロード
}
```

**APIリクエスト例（市場結果照会）：**
```python
import requests
import json

def get_jepx_market_results(delivery_date):
    url = "https://api.jepx.jp/dah1050"
    headers = {"Content-Type": "application/json"}
    payload = {"deliveryDate": delivery_date}
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()
```

## 3. 実装推奨アーキテクチャ

### 🚀 推奨モデル：LightGBM

**LightGBM**が最適な選択肢であることが明確になりました：

**LightGBMの優位性：**
- 高精度：複雑な非線形関係の学習が可能
- 高速処理：大量の特徴量を効率的に処理  
- 説明可能性：SHAP値による特徴量重要度分析
- 実績：電力需要予測で高い予測精度を実現

### 🔧 データパイプライン設計

```python
# 推奨技術スタック
orchestration = "Apache Airflow"
feature_store = "Tide / 自社ETL"
model_serving = "FastAPI + MLflow"
monitoring = "Prometheus + Grafana"
```

**自動データ取得パイプライン例：**
```python
# OCCTO CSVダウンロード自動化
def download_occto_reserve_data(date_from, date_to):
    base_url = "https://web-kohyo.occto.or.jp/kks-web-public/download/downloadCsv"
    params = {
        "jhSybt": "02",  # 翌々日ブロック情報
        "tgtYmdFrom": date_from,
        "tgtYmdTo": date_to
    }
    response = requests.get(base_url, params=params)
    return pd.read_csv(StringIO(response.text))
```

## 4. 特徴量エンジニアリング戦略

### 🎛️ 高度な特徴量設計

**時系列特徴量：**
```python
# ラグ特徴量（周期性活用）
df['demand_lag_24h'] = df['demand'].shift(24)  # 24時間前
df['demand_lag_168h'] = df['demand'].shift(168)  # 1週間前同時刻
df['demand_ma_7d'] = df['demand'].rolling(168).mean()  # 過去7日移動平均

# 気象要因の非線形変換
df['temp_cooling_threshold'] = np.maximum(0, df['temperature'] - 25)**2
df['temp_heating_threshold'] = np.maximum(0, 18 - df['temperature'])**2
```

**組み合わせ特徴量：**
```python
# 市場要因×気象要因
df['price_temp_interaction'] = df['jepx_price'] * df['temperature']
df['supply_weather_risk'] = df['renewable_forecast_std'] * df['cloud_cover']
```

## 5. モデル評価・運用戦略

### 📊 評価指標とベンチマーク

**主要評価指標：**
- **RMSE**（点推定精度）：< 2.0%を目標
- **MAPE**（相対誤差）：< 15%を目標  
- **Coverage**（予測区間）：95%信頼区間の実現率 > 90%
- **季節別精度**：夏季・冬季のピーク時精度評価

### 🔄 継続的モデル改善

**モデル更新ポリシー：**
```python
# 自動モデル更新トリガー
model_performance_threshold = 2.5  # RMSE閾値
if current_rmse > model_performance_threshold:
    trigger_model_retraining()
    send_alert_to_ml_team()
```

## 6. 実装スケジュール

**Phase 1（PoC - 6-8週間）**
- OCCTOデータ取得自動化
- 基本LightGBMモデル構築
- 初期精度評価

**Phase 2（Pilot - 8-12週間）**  
- JEPX API統合
- 高度特徴量エンジニアリング
- リアルタイム予測システム

**Phase 3（本番化 - 12-16週間）**
- 運用監視システム構築
- SHAPによる説明可能性実装
- パフォーマンス最適化

## 7. コスト・ROI分析

**データ取得コスト（月額推定）：**
- 日本気象協会ENeAPI：¥32,000～
- JEPX会員費：¥120,000（年額）
- 開発・運用人件費：¥2,000,000～（初期）

**期待ROI：**
- 予測精度向上による需給調整コスト削減
- 停電リスク低減による社会的損失回避
- 効率的な調整力調達による費用最適化

---

この包括的な設計により、TEPCO管内におけるOCCTO予備率の高精度予測が実現可能です。特に、OCCTOの公開CSVダウンロード機能とJEPX APIの活用により、安定的なデータパイプラインの構築が可能となり、電力の安定供給に大きく貢献することが期待されます。