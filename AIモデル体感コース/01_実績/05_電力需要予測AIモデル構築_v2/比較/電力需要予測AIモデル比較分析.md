# AIモデル比較分析：電力需要予測

## 1. はじめに

本ドキュメントは、電力需要予測プロジェクトにおいて採用されている複数のAIモデル（Keras, LightGBM, PyCaret, RandomForest）について、そのデータ処理、学習、予測、評価の各ロジックを詳細に分析し、比較検討することを目的としています。

**分析対象プロジェクト**: 電力需要予測AIモデル構築  
**対象環境**: Python 3.10.11 (推奨) / Python 3.13.3  
**分析日**: 2025年8月5日

## 1.1. プロジェクト構成概要

```
AI/
├── data/
│   ├── data.py                 # 基盤データ処理
│   ├── juyo-*.csv             # 電力需要実績
│   └── temperature-*.csv      # 気温データ
├── train/                     # モデル学習
│   ├── Keras/Keras_train.py
│   ├── LightGBM/LightGBM_train.py
│   ├── Pycaret/Pycaret_train.py
│   └── RandomForest/RandomForest_train.py
└── tomorrow/                  # 予測実行
    ├── data.py, temp.py       # 最新データ取得
    ├── Keras/Keras_tomorrow.py
    ├── LightGBM/LightGBM_tomorrow.py
    ├── Pycaret/Pycaret_tomorrow.py
    └── RandomForest/RandomForest_tomorrow.py
```

## 2. データ処理と特徴量エンジニアリング

電力需要予測モデルの基盤となるデータ処理は、`AI/data/data.py`、`AI/tomorrow/data.py`、`AI/tomorrow/temp.py`によって行われます。
これらのスクリプトは、過去の電力需要データと気温データを収集・前処理し、モデルが利用できる形式の特徴量を生成します。

### 2.1. 過去データの収集と前処理 (`AI/data/data.py`)

- **目的**: 複数年分の電力需要（`juyo-YYYY.csv`）と気温（`temperature-YYYY.csv`）データを統合し、モデル学習用の訓練データとテストデータを作成します。
- **詳細ロジック**:
    1.  **ファイル動的読み込み**: `data/juyo-*.csv`と`data/temperature-*.csv`を動的に検索し、対応する年（ファイル名から抽出）のファイルを読み込みます。
    2.  **CSV読み込み**: 
        - 電力需要データ: `skiprows=3`, `header=None`, `names=["DATE", "TIME", "KW"]`で読み込みます。`TIME`列は`HH:MM〜HH:MM`形式のため、`HH:MM`部分のみを抽出します。
        - 気温データ: `skiprows=5`, `header=None`, `names=["DATE", "TEMP"]`, `usecols=[0, 1]`で読み込みます。
    3.  **日時インデックス変換**: `DATE`と処理済みの`TIME`を結合し、`%Y/%m/%d %H:%M`形式で`datetime`型に変換し、DataFrameのインデックスに設定します。
    4.  **特徴量生成**: インデックスから`MONTH`（月）、`WEEK`（曜日、0=月曜）、`HOUR`（時間）を抽出して新たな特徴量とします。
    5.  **データマージ**: 電力需要データと気温データを日時インデックスをキーとして結合します。気温データは`reindex`を用いて電力需要データのインデックスに合わせます。
    6.  **欠損値処理**: マージ後に発生したNaN値を持つ行を削除します。
    7.  **One-hotエンコーディング**: `MONTH`, `WEEK`, `HOUR`, `TEMP`列に対して`pd.get_dummies`を用いてOne-hotエンコーディングを適用します。これにより、カテゴリカルな特徴量を数値データに変換します。
    8.  **データ分割**: 最終的な特徴量`X`と目的変数`y`（`KW`）を生成し、`sklearn.model_selection.train_test_split`を用いて訓練データとテストデータに分割します。この際、`shuffle=False`とすることで時系列順序を保持します。`test_size`は0.1（10%）に設定されています。
    9.  **CSV保存**: 生成された`X`, `y`, `X_train`, `X_test`, `y_train`, `y_test`はそれぞれ`data/X.csv`などのファイル名でCSVとして保存されます。

### 2.2. 最新データの収集と前処理 (`AI/tomorrow/data.py`, `AI/tomorrow/temp.py`)

- **目的**: 最新の電力需要実績データと将来の気温予測データを取得し、モデル予測用の特徴量と実績データを作成します。

#### 2.2.1. 電力需要実績データの更新 (`AI/tomorrow/data.py`)

- **目的**: TEPCOのWebサイトから最新の電力需要実績データをダウンロードし、既存のデータファイル（`data/juyo-YYYY.csv`）を更新します。
- **詳細ロジック**:
    1.  **既存データ読み込み**: `data/juyo-YYYY.csv`が存在する場合、既存のメタデータ（最初の3行）とデータを読み込みます。
    2.  **Webからのダウンロード**: 現在の年月に基づき、TEPCOの電力使用状況のZIPファイルURLを構築し、`requests`ライブラリでダウンロードします。
    3.  **ZIPファイル処理**: ダウンロードしたZIPファイル内のCSVを読み込み、`skiprows=14`, `nrows=24`, `usecols=[0, 1, 2]`でデータ部分を抽出します。列名は`["DATE", "TIME", "KW"]`に設定されます。
    4.  **データ結合と重複排除**: 既存データと新規データを結合し、`DATE`と`TIME`をキーとして重複行を削除します。
    5.  **CSV保存**: 更新されたデータを、元のメタデータと日本語ヘッダーを保持したまま`data/juyo-YYYY.csv`に保存します。この際、改行コードの処理に注意が払われています。
    6.  **予測対象実績データ抽出**: 更新された電力需要データから、`past_days`（デフォルト7日）分の実績値（`KW`）を抽出し、`tomorrow/Ytest.csv`として保存します。

#### 2.2.2. 気温予測データの取得 (`AI/tomorrow/temp.py`)

- **目的**: Open-Meteo APIから指定地点（緯度、経度）の気温予測データを取得し、予測モデル用の特徴量を作成します。
- **詳細ロジック**:
    1.  **APIリクエスト**: `latitude`, `longitude`, `timezone`, `past_days`, `forecast_days`（デフォルト7日）をパラメータとしてOpen-Meteo APIにリクエストを送信します。
    2.  **JSON解析**: 応答されたJSONデータから`hourly`キーの`time`と`temperature_2m`を抽出します。
    3.  **DataFrame作成**: 抽出したデータからDataFrameを作成し、`time`列を`datetime`型に変換します。
    4.  **特徴量生成**: `time`列から`MONTH`, `WEEK`, `HOUR`を抽出し、`TEMP`と共に予測モデルの入力特徴量とします。
    5.  **CSV保存**: 生成された特徴量データは`tomorrow/tomorrow.csv`として保存されます。

## 3. 各AIモデルの分析

本プロジェクトでは、Keras（ニューラルネットワーク）、LightGBM（勾配ブースティング）、PyCaret（自動機械学習）、RandomForest（アンサンブル学習）の4種類のモデルが電力需要予測に用いられています。各モデルの学習と予測のロジックを以下に詳述します。

### 3.1. Keras (ニューラルネットワーク)

- **学習スクリプト**: `AI/train/Keras/Keras_train.py`
- **予測スクリプト**: `AI/tomorrow/Keras/Keras_tomorrow.py`

#### 3.1.1. 学習プロセス

1.  **データ読み込み**: `Xtrain.csv`, `Xtest.csv`, `Ytrain.csv`, `Ytest.csv`を読み込みます。
2.  **データ標準化**: `sklearn.preprocessing.StandardScaler`を用いて`X_train`と`X_test`を標準化します。`fit`は`X_train`のみで行い、`transform`を両方に適用します。
3.  **モデルアーキテクチャ**: `Sequential`モデルを使用し、以下の層で構成されます。
    - 入力層: `Dense(64, input_dim=len(X_cols), activation='relu')`
    - 隠れ層: `Dense(64, activation='relu')`
    - 出力層: `Dense(1)` (回帰問題のため活性化関数なし)
4.  **コンパイル**: 損失関数は`mean_squared_error`、評価指標は`mean_absolute_error`を使用します。最適化関数はコメントアウトされていますが、`Adam`が候補として挙げられています。
5.  **学習**: `model.fit`を用いて学習を実行します。`epochs=200`, `validation_split=0.2`, `batch_size=128`が設定されています。`EarlyStopping`コールバックが`val_loss`を監視し、`patience=5`で早期終了します。
6.  **学習過程の可視化**: 学習中の損失（`loss`と`val_loss`）の推移をグラフ化し、`Keras_history.png`として保存します。
7.  **モデル保存**: 学習済みモデルは`pickle`を用いて`Keras_model.sav`として保存されます。
8.  **評価**: `model.evaluate`でテストデータに対する損失と精度を評価し、`r2_score`も算出します。
9.  **予測結果の保存と可視化**: テストデータに対する予測結果を`Keras_Ypred.csv`として保存し、実績値との比較グラフ（全体および直近7日間）を`Keras_Ypred.png`と`Keras_Ypred_7d.png`として保存します。
10. **評価指標**: RMSEとカスタムSCORE（`1.0 - RMSE / y_test.mean()`）を算出し、出力します。

#### 3.1.2. 予測プロセス

1.  **データ読み込み**: `Xtrain.csv`（標準化用）、`Ytest.csv`（比較用実績値）、`tomorrow.csv`（予測対象データ）を読み込みます。
2.  **データ標準化**: 学習時と同様に`StandardScaler`を用いて`Xtomorrow`を標準化します。
3.  **モデル読み込み**: `pickle`を用いて`Keras_model.sav`を読み込みます。
4.  **予測**: `model.predict`を用いて`Xtomorrow`に対する電力需要を予測します。
5.  **予測結果の保存と可視化**: 予測結果を`Keras_tomorrow.csv`として保存し、`Ytest.csv`との比較グラフを`Keras_tomorrow.png`として保存します。グラフのX軸は現在日から`past_days`（デフォルト7日）前を起点とした日時で表示されます。
6.  **評価指標**: RMSEとカスタムSCOREを算出し、出力します。

### 3.2. LightGBM (勾配ブースティング)

- **学習スクリプト**: `AI/train/LightGBM/LightGBM_train.py`
- **予測スクリプト**: `AI/tomorrow/LightGBM/LightGBM_tomorrow.py`

#### 3.2.1. 学習プロセス

1.  **データ読み込みと標準化**: Kerasと同様にデータを読み込み、`StandardScaler`で標準化します。
2.  **モデル取得**: `lightgbm.LGBMRegressor()`のデフォルト設定でモデルをインスタンス化します。
3.  **学習**: `model.fit`を用いて訓練データでモデルを学習させます。
4.  **モデル保存**: 学習済みモデルは`pickle`を用いて`LightGBM_model.sav`として保存されます。
5.  **評価**: `model.score`でテストデータに対するスコアを評価します。
6.  **予測結果の保存と可視化**: テストデータに対する予測結果を`LightGBM_Ypred.csv`として保存し、実績値との比較グラフ（全体および直近7日間）を`LightGBM_Ypred.png`と`LightGBM_Ypred_7d.png`として保存します。
7.  **評価指標**: RMSEとカスタムSCOREを算出し、出力します。

#### 3.2.2. 予測プロセス

1.  **データ読み込みと標準化**: 学習時と同様にデータを読み込み、`Xtomorrow`を標準化します。
2.  **モデル読み込み**: `pickle`を用いて`LightGBM_model.sav`を読み込みます。
3.  **予測**: `model.predict`を用いて`Xtomorrow`に対する電力需要を予測します。
4.  **予測結果の保存と可視化**: 予測結果を`LightGBM_tomorrow.csv`として保存し、`Ytest.csv`との比較グラフを`LightGBM_tomorrow.png`として保存します。グラフのX軸は現在日から`past_days`（デフォルト7日）前を起点とした日時で表示されます。
5.  **評価指標**: RMSEとカスタムSCOREを算出し、出力します。

### 3.3. PyCaret (自動機械学習)

- **学習スクリプト**: `AI/train/Pycaret/Pycaret_train.py`
- **予測スクリプト**: `AI/tomorrow/Pycaret/Pycaret_tomorrow.py`

#### 3.3.1. 学習プロセス

1.  **データ読み込み**: `Xtrain.csv`, `Xtest.csv`, `Ytrain.csv`, `Ytest.csv`を読み込みます。PyCaretは内部でデータ処理を行うため、明示的な標準化は行いません。
2.  **PyCaretセットアップ**: `pycaret.regression.setup`を用いてデータセットを設定します。`data`には`X_train`と`y_train`を結合したDataFrameを渡し、`target="KW"`と指定します。
3.  **モデル作成**: `create_model('lightgbm', fold=10)`を用いてLightGBMモデルを学習します。コメントアウトされていますが、`rf`（RandomForest）も選択肢として挙げられています。
4.  **モデル保存**: `pycaret.regression.save_model`を用いて学習済みモデルを`Pycaret_model.pkl`として保存します。
5.  **評価**: `model.score`でテストデータに対するスコアを評価します。
6.  **予測結果生成**: `pycaret.regression.predict_model`を用いてテストデータに対する予測値を生成します。PyCaretの予測結果はDataFrame形式で返されるため、`prediction_label`列を抽出し、一次元配列に変換します。
7.  **予測結果の保存と可視化**: テストデータに対する予測結果を`Pycaret_Ypred.csv`として保存し、実績値との比較グラフ（全体および直近7日間）を`Pycaret_Ypred.png`と`Pycaret_Ypred_7d.png`として保存します。
8.  **評価指標**: RMSEとカスタムSCOREを算出し、出力します。

#### 3.3.2. 予測プロセス

1.  **データ読み込み**: `Ytest.csv`（比較用実績値）、`tomorrow.csv`（予測対象データ）を読み込みます。
2.  **モデル読み込み**: `pycaret.regression.load_model`を用いて`Pycaret_model.pkl`を読み込みます。
3.  **予測**: `pycaret.regression.predict_model`を用いて`tomorrow.csv`に対する電力需要を予測します。学習時と同様に`prediction_label`列を抽出し、一次元配列に変換します。
4.  **予測結果の保存と可視化**: 予測結果を`Pycaret_tomorrow.csv`として保存し、`Ytest.csv`との比較グラフを`Pycaret_tomorrow.png`として保存します。グラフのX軸は現在日から`past_days`（デフォルト7日）前を起点とした日時で表示されます。
5.  **評価指標**: RMSEとカスタムSCOREを算出し、出力します。

### 3.4. RandomForest (アンサンブル学習)

- **学習スクリプト**: `AI/train/RandomForest/RandomForest_train.py`
- **予測スクリプト**: `AI/tomorrow/RandomForest/RandomForest_tomorrow.py`

#### 3.4.1. 学習プロセス

1.  **データ読み込みと標準化**: Kerasと同様にデータを読み込み、`StandardScaler`で標準化します。
2.  **モデル取得**: `sklearn.ensemble.RandomForestRegressor()`のデフォルト設定でモデルをインスタンス化します。
3.  **学習**: `model.fit`を用いて訓練データでモデルを学習させます。
4.  **モデル保存**: 学習済みモデルは`pickle`を用いて`RandomForest_model.sav`として保存されます。
5.  **評価**: `model.score`でテストデータに対するスコアを評価します。
6.  **予測結果の保存と可視化**: テストデータに対する予測結果を`RandomForest_Ypred.csv`として保存し、実績値との比較グラフ（全体および直近7日間）を`RandomForest_Ypred.png`と`RandomForest_Ypred_7d.png`として保存します。
7.  **評価指標**: RMSEとカスタムSCOREを算出し、出力します。

#### 3.4.2. 予測プロセス

1.  **データ読み込みと標準化**: 学習時と同様にデータを読み込み、`Xtomorrow`を標準化します。
2.  **モデル読み込み**: `pickle`を用いて`RandomForest_model.sav`を読み込みます。
3.  **予測**: `model.predict`を用いて`Xtomorrow`に対する電力需要を予測します。
4.  **予測結果の保存と可視化**: 予測結果を`RandomForest_tomorrow.csv`として保存し、`Ytest.csv`との比較グラフを`RandomForest_tomorrow.png`として保存します。グラフのX軸は現在日から`past_days`（デフォルト7日）前を起点とした日時で表示されます。
5.  **評価指標**: RMSEとカスタムSCOREを算出し、出力します。

## 4. 共通の評価指標と可視化

すべてのモデルで共通して以下の評価指標が用いられ、予測結果の可視化が行われます。

-   **RMSE (Root Mean Squared Error)**: 予測値と実績値の差の二乗平均の平方根。誤差の大きさを絶対値で示し、値が小さいほど精度が高いことを意味します。
    -   計算式: `mse ** 0.5`
-   **SCORE (カスタム評価指標)**: `1.0 - RMSE / y_test.mean()`。実績値の平均に対するRMSEの割合を1から引いたもので、1に近いほど精度が高いことを意味します。

可視化は`matplotlib.pyplot`を用いて行われ、予測値と実績値の時系列グラフがPNG形式で保存されます。グラフにはモデル名がタイトルとして付与され、X軸は日付または時間、Y軸は電力（kW）を示します。

## 5. モデル間の比較観点

各モデルの分析に基づき、以下の観点から比較を行うことができます。

-   **精度**: 各モデルのRMSEとSCOREを比較し、最も予測精度の高いモデルを特定します。Kerasはニューラルネットワークの複雑なパターン認識能力、LightGBMとRandomForestは決定木ベースのアンサンブル学習の堅牢性、PyCaretは自動化されたモデル選択の利点があります。
-   **学習時間**: 各モデルの学習にかかる時間を比較します。一般的に、LightGBMは高速な学習が特徴であり、Kerasはモデルの複雑性やデータ量によって学習時間が変動します。
-   **予測時間**: 各モデルが予測を生成するのにかかる時間を比較します。リアルタイム予測の要件がある場合に重要となります。
-   **複雑性**: モデルの内部構造やハイパーパラメータの調整の複雑性を比較します。Kerasは層の設計や活性化関数の選択など、より詳細な設計が必要ですが、LightGBMやRandomForestは比較的少ないパラメータで高い性能を発揮することがあります。PyCaretは自動化により複雑性を隠蔽します。
-   **データのスケーリング要件**: KerasやRandomForest、LightGBMは特徴量のスケーリング（標準化）を明示的に行っていますが、PyCaretは内部で処理を行うため、ユーザーが意識する必要がありません。
-   **解釈性**: モデルがどのように予測を導き出したかの解釈のしやすさを比較します。決定木ベースのモデル（LightGBM, RandomForest）は、ニューラルネットワーク（Keras）よりも一般的に解釈性が高いとされます。

## 6. 実装課題と推奨事項

### 6.1. Python環境別の対応状況

| モデル | Python 3.10.11 | Python 3.13.3 | 対応状況 |
|---|---|---|---|
| **Keras** | ✅ TensorFlow 2.15.0 | ⚠️ TensorFlow 2.20.0rc0 | 3.13.3ではRC版のため注意 |
| **LightGBM** | ✅ LightGBM 4.6.0 | ✅ LightGBM 4.6.0 | 両環境で安定 |
| **PyCaret** | ✅ PyCaret 3.3.2 | ❌ 未インストール | **3.13.3では利用不可** |
| **RandomForest** | ✅ scikit-learn 1.7.1 | ✅ scikit-learn 1.7.1 | 両環境で安定 |

### 6.2. 各モデルの実装上の特徴

#### 6.2.1. Keras (ニューラルネットワーク)
**特徴**:
- 複雑な非線形関係の学習が可能
- EarlyStopping による過学習防止
- 学習履歴の可視化機能

**実装上の注意点**:
- Python 3.13.3ではTensorFlow RC版のため不安定の可能性
- モデルアーキテクチャの設計が精度に大きく影響
- 学習時間が他モデルより長い傾向

#### 6.2.2. LightGBM (勾配ブースティング)
**特徴**:
- 高速な学習と予測
- デフォルトパラメータでも高い性能
- メモリ効率が良好

**実装上の注意点**:
- 特徴量の重要度分析が容易
- 時系列データに適した手法
- 過学習の制御が比較的容易

#### 6.2.3. PyCaret (自動機械学習)
**特徴**:
- 自動的なモデル選択と比較
- 内部でのデータ前処理自動化
- 複数アルゴリズムの一括評価

**実装上の重大な問題**:
- **Python 3.13.3環境では利用不可**
- モデルの内部処理がブラックボックス化
- カスタマイズの自由度が制限される

#### 6.2.4. RandomForest (アンサンブル学習)
**特徴**:
- 安定した予測性能
- 過学習に対する耐性
- 特徴量重要度の評価が可能

**実装上の注意点**:
- 大量のデータでも安定動作
- ハイパーパラメータ調整の影響が比較的小さい
- 解釈性が高い

### 6.3. 推奨開発環境

#### ✅ **推奨: Python 3.10.11**
```bash
# 理由
- 全モデル（Keras, LightGBM, PyCaret, RandomForest）が利用可能
- 安定したライブラリバージョン
- 長期サポートの実績

# 必須ライブラリ
pip install pandas==2.1.4 numpy==1.26.4 scikit-learn==1.7.1
pip install tensorflow==2.15.0 lightgbm==4.6.0 pycaret==3.3.2
pip install matplotlib==3.7.5 requests==2.32.4
```

#### ⚠️ **Python 3.13.3使用時の制約**
```bash
# 制約事項
- PyCaretモデルは利用不可
- TensorFlow RC版による不安定性
- numpy 2.x系での互換性問題の可能性

# 対応方法
pip install pycaret==3.3.2  # 手動インストール必要
# または PyCaret無しでの開発
```

### 6.4. 最終推奨事項

1. **開発環境**: Python 3.10.11を推奨
2. **メインモデル**: LightGBM（安定性と性能のバランス）
3. **サブモデル**: RandomForest（安定性重視）
4. **実験的モデル**: Keras（高精度追求時）
5. **比較用**: PyCaret（Python 3.10.11環境でのみ利用）

**プロジェクト成功のためには、まずPython 3.10.11環境での全モデル実装を完了させ、その後Python 3.13.3での対応を検討することを強く推奨します。**