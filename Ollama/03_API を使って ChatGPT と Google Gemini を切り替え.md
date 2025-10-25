[[ Open WebUI ] で API を使って ChatGPT と Google Gemini を切り替えて使ってみた #初心者 - Qiita](https://qiita.com/Yuzpomz/items/ce920fe70a7bd69d055a)

# 事前確認: 外部サービスの API キーの入手

ChatGPT と Google Gemini のいずれも API Key を使用する必要があるので事前に取得しておきましょ

ChatGPT の API key

アカウントの新規作成やクレジットカードの登録が全部終わったら、 Dashboard --> API keys から新規作成できます。(Chat GPT を有料で使用していても API は別契約になります。無料枠は無いため応答を確認するには事前に購入しておく必要があります。)

Google Gemini の API key

アカウントの新規作成が終わったら Get API Key から新規作成できます。

### Open WebUI の起動と確認

Open WebUI を 起動します。

```
cd .venv
scripts/activate
open-webui serve --host 0.0.0.0 --port 8080

  ___                    __        __   _     _   _ ___
 / _ \ _ __   ___ _ __   \ \      / /__| |__ | | | |_ _|
| | | | '_ \ / _ \ '_ \   \ \ /\ / / _ \ '_ \| | | || |
| |_| | |_) |  __/ | | |   \ V  V /  __/ |_) | |_| || |
 \___/| .__/ \___|_| |_|    \_/\_/ \___|_.__/ \___/|___|
      |_|
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

ブラウザで [http://localhost:8080](http://localhost:8080/) にアクセスしてログインしましょう。

# Open WebUI で ChatGPT を設定

ChatGPTの場合は標準設定が使えます。  
Open WebUI の画面の左下のアイコンから 「設定」-->「 管理者画面」 を表示させて、「接続」を表示させると「OpenAI API」という項目があります。この右側にChatGPT の API key を入力して右下の「保存」ボタンを押しましょう。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2Fa4ead7f9-595f-4e21-60d4-f47c6a266ee7.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d783353f84d02979c495bfe2abdbc100)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2Fa4ead7f9-595f-4e21-60d4-f47c6a266ee7.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d783353f84d02979c495bfe2abdbc100)

保存ボタンを押すと接続が開始されます。接続が切れていると表示されないためその場合は右側のリロードボタンを押すと再接続されます。  
Key の入力に間違いがなければワークスペースにモデルの一覧が表示されます。たくさんありますね。  
[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F5e2a4e79-1c9e-dbc0-3222-ce595b4d7c99.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d872dddd2ffca9f782663c9e57b4c486)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F5e2a4e79-1c9e-dbc0-3222-ce595b4d7c99.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d872dddd2ffca9f782663c9e57b4c486)

### ChatPGT 4-o さんにあいさつしてみた

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F34f13c0a-1fcd-95c8-67be-08d77bbde97f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=1abe3d72e40c15d13d55a6c77c5d3c9b)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F34f13c0a-1fcd-95c8-67be-08d77bbde97f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=1abe3d72e40c15d13d55a6c77c5d3c9b)

有料なので少しだけお金を使ってお話してみました。どきどきしますね。

# Open WebUI で pipelines を使用

Open WebUI の接続画面で対応していない場合は外部ツールである pipelines を経由して使用できるようになっています。Open WebUI の環境と同じように Python3.11 環境で動く Python プログラムを起動してポート番号を登録する必要があります。

## pipelines の入手と起動

pipelines の情報は下記から入手できます。  
[https://github.com/open-webui/pipelines](https://github.com/open-webui/pipelines)

まずは説明書記載通りに実行してきますね。プログラムは別のものなので venv の環境は今回新しく作成しても問題ないです。

```
cd .venv
scripts/activate
git clone https://github.com/open-webui/pipelines.git
cd pipelines
pip install -r requirements.txt
```

インストールが終わったらコマンドで実行します。説明ページでは「sh ./start.sh」となっていますが、Windows 用には「start.bat」が用意されていますね。こちらを使います。

(.venv) PS C:\Users\h-ham\Open WebUI> cd .venv
(.venv) PS C:\Users\h-ham\Open WebUI\.venv> cd pipelines
(.venv) PS C:\Users\h-ham\Open WebUI\.venv\pipelines> .\start

```
.\start
INFO:     Uvicorn running on http://0.0.0.0:9099 (Press CTRL+C to quit)
```

デフォルトでは 9099 ポートを使用するようです。( start.bat で変更できます)

## Open WebUI で pipelines の登録と接続

それではこのパラメータを設定しちゃいましょ。  
Open WebUI の画面の左下のアイコンから 「設定」-->「管理者画面」 を表示させて、「パイプライン」を表示させると「パイプラインの管理」という項目があります。ここにURLを入力します。  
[http://localhost:9099]  
入力したら右下の「保存」を押します。接続に問題がないと新しい画面が現れて入力画面がでてきます。  
ここまでできれば準備完了です。

# Open WebUI のパイプラインに Google Gemini を設定

Open WebUI で pipelines の設定が完了したら使用したいサービスと通信するためのプログラムを Open WebUI に登録して利用可能にします。Open WebUI の Github テンプレートがあるのでそれを使わせてもらいましょ

## Google Gemini 用の pipeline をセットアップ

Open WebUI の画面の左下のアイコンから 「設定」-->「管理者画面」 を表示させて、「パイプライン」を表示させると「パイプラインの管理」という項目があります。現在は「Github URLからインストール」という項目が増えているはずです。ここにURLを入力し、保存ボタンを押します。  
[https://github.com/open-webui/pipelines/blob/main/examples/pipelines/providers/google_manifold_pipeline.py]  
接続に問題が無ければパイプラインバルブに[Google_Manifold_Pipeline(manifold)]と表示されます。

さらに下段に「Google Api Key」という入力項目があるので、ここに API Key を入力しておきましょ

https://aistudio.google.com/app/apikey
API_KEY	AIzaSyDL6Dm7T2iSvzC3MU7lKp-M6qvX4av18wc

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F21ec9684-bab0-3332-b47f-6eafc2b66624.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d4a946ad58f96b286bdc9d8e146b3251)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F21ec9684-bab0-3332-b47f-6eafc2b66624.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d4a946ad58f96b286bdc9d8e146b3251)

Key の入力に間違いがなければワークスペースにモデルの一覧が表示されます。たくさんありますね。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2Fea14c7db-534f-3963-5183-4dc5e81a0a2e.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d050a5e5a084ffceaf838e94f2298499)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2Fea14c7db-534f-3963-5183-4dc5e81a0a2e.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d050a5e5a084ffceaf838e94f2298499)

### Google: Gemini 1.5 Pro さんにあいさつしてみた

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F53f7b55c-122b-3340-9938-c1a098281cda.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d9c65e5a05b11af956dc511d186cc468)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F53f7b55c-122b-3340-9938-c1a098281cda.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d9c65e5a05b11af956dc511d186cc468)

日本語も自然に対応してくれていますね  
それではみなさんも快適なLLMライフをお過ごしください！
