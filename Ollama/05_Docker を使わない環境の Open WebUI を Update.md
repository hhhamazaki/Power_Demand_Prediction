[[ Open WebUI ] [ ローカルLLM ] Docker を使わない環境の Open WebUI を Update しました（起動スクリプトもメンテナンス） #ollama - Qiita](https://qiita.com/Yuzpomz/items/34fc708a7cbebd2c0166)
### pip を使って Update していきます。

```
cd .venv
scripts/activate
python -m pip install --upgrade pip
pip list | findstr open-webui
python -m pip install --upgrade open-webui
pip list | findstr open-webui
    open-webui                               0.4.8
```

0.4.8 にアップデートできました！（終わり）

# UI など変更点の確認

モデルの管理画面に変更があるようですね。

### ワークスペースで表示するモデルの登録

以前のバージョンでは利用可能モデルすべて表示されていましたが、デフォルトは「未登録」になったため使用したいモデルのプロファイルをいくつか登録しておきます。  
ワークスペースの画面でプラスのアイコンをクリックするとモデルのプロファイル作成画面が表示されます。「Model Name」と「ベースモデル」だけ入力すれば作成できました。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F45959cee-45e6-f66f-c532-571d1532e25d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=f008f7a6a5869a04ee0f9a63394846a0)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F45959cee-45e6-f66f-c532-571d1532e25d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=f008f7a6a5869a04ee0f9a63394846a0)

このプロファイルはアカウントごとに作成され、文字通り自分用のワークスペースになります。

リクエストパラメータのモデルごとの設定もここでできるようになってますね。（下記はご参考まで）

"temperature": 0.2,  
"top_p": 0.8,  
"repetition_penalty": 1.1,  
"max_tokens": 512

### 複数モデルの1画面表示

3つのモデルを同時に表示させてみました。応答の違いが分かりやすいですね。  
（画面の設定上では制限が無さそうでしたが4つ以上登録すると最初のモデルから消えてしまうようです。）

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2Fc1dc8194-8d0c-1692-e22d-b7da628a723b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2721c1765404a10f6f16ab431788c6f5)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2Fc1dc8194-8d0c-1692-e22d-b7da628a723b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2721c1765404a10f6f16ab431788c6f5)

### 使いたいモデルを優先して表示する設定

Open WebUI は設定済みの利用可能なモデルを使えますが数十個のモデルがあると管理が大変ですよね。管理者画面のモデル設定でデフォルトモデルとモデルの並び方を設定できます（デフォルトはアルファベット降順にソートされています。）。使わないモデルは明示的にOFFにできます。

環境設定については左下のアカウントのアイコンから  
「管理者パネル」> 「設定」 > 「モデル」　  
に移動して設定できます。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F40cf7591-0f44-2c70-eb28-9693e61b449f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=074a36709e370e9fe9301b00229993c3)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F40cf7591-0f44-2c70-eb28-9693e61b449f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=074a36709e370e9fe9301b00229993c3)

# 起動スクリプトもメンテナンスしました

ollama for windows + WSL + pipelines + local LLM + 外部サービスのAPI を同時に使用できる環境ができましたが起動管理が大変ですね。とりあえず起動用バッチだけ作成しましたので記録のために残しておきます（デフォルトで ollama は Windows のスタートアップに入るのでスクリプトでは操作していません）。

Start_Open-WebUI.bat

```
start "" cmd /c wsl -d Ubuntu bash -c "cd /home/user && /home/user/startqwen2vl2binstruct.sh"
C:
cd C:\.venv
call scripts\activate.bat
cd C:\.venv\pipelines
start "" cmd /c start.bat
cd C:\.venv
open-webui serve
```

それではみなさんも快適な ローカルLLM ライフをお楽しみください！