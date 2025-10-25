[[ ローカル LLM ] Open WebUI + ollama for Windows + Qwen2.5 で自宅にローカルLLMをセットアップ #初心者 - Qiita](https://qiita.com/Yuzpomz/items/35965a44c958aafbde53)

[Python Releases for Windows | Python.org](https://www.python.org/downloads/windows/)
3.11.9

### 1.1 ollama for Windows のダウンロードとインストール

[Download Ollama on Windows](https://ollama.com/download)

インストールが完了すると ollama が起動済みの状態で自動的にプロンプトが開きます。  
ダウンロード済みモデルを呼び出す場合は ollama run _MODELNAME_ で使用できます。

例）モデルダウンロードと呼び出し

```
ollama pull gemma2:2b
ollama pull qwen3:1.7b
ollama run qwen3:1.7b
```

モデルのダウンロードが始まります  
pull を実行するとダウンロード済みモデルが更新されます

ollama ですぐに使える LLM モデルはこちらから検索  
[https://ollama.com/library](https://ollama.com/library)

### 1.2 ollama for Windows の動作確認

デフォルトではブラウザで下記にアクセスできます。  
[http://localhost:11434](http://localhost:11434/)

メッセージのみの画面が表示されます。ここまで確認できれば次に進みましょ。

### 2.1 Open WebUI のための venv 環境準備

依存関係を調べるの大変なので新規venv環境を作ることをお勧め。

```
py --list-paths
python -m venv .venv
python -m venv .venv --clear
py -3.11 -m venv .venv
```

venv 環境に入って、Pythonのバージョンを確認

```
cd .venv
scripts/activate
python -V
deactivate
```

### 2.2 open-webui のインストール

```
cd .venv
scripts/activate
python -m pip install --upgrade pip
pip install open-webui
deactivate
```

完了後、起動コマンドを実行

```
cd .venv
scripts/activate
open-webui serve



  ___                    __        __   _     _   _ ___
 / _ \ _ __   ___ _ __   \ \      / /__| |__ | | | |_ _|
| | | | '_ \ / _ \ '_ \   \ \ /\ / / _ \ '_ \| | | || |
| |_| | |_) |  __/ | | |   \ V  V /  __/ |_) | |_| || |
 \___/| .__/ \___|_| |_|    \_/\_/ \___|_.__/ \___/|___|
      |_|
```

### 2.3 open-webui の動作確認

デフォルトではブラウザで下記にアクセスできます。  
[http://localhost:8080](http://localhost:8080/)

TCP 8080番はいろんなアプリで使われるので同時起動しないように注意しましょう

フルネーム	hidetoshi.hamazaki
メールアドレス	h-hamazaki@nifty.com
パスワード	hh15243514

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2Fcd4771a3-32df-b289-3e19-8acfa414ef29.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7caeaa22a3764ea7dd77856086b49a64)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2Fcd4771a3-32df-b289-3e19-8acfa414ef29.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7caeaa22a3764ea7dd77856086b49a64)

日本語環境を自動的に検知しているようですね。  
メールアドレス、アカウント、パスワードを適当に入力し、セルフサインアップしてログインします。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F06d5ba9e-e24e-9f4c-fffb-9ee392ebf892.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d6f7f8e75f38a97c7b1d67cca2b5bc10)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F06d5ba9e-e24e-9f4c-fffb-9ee392ebf892.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d6f7f8e75f38a97c7b1d67cca2b5bc10)

ログインすると見たことのある画面が現れます。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F94a34225-aca8-14d5-43db-11c21c205ab4.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=517cd6d1c953dbe5e05123b6b311343a)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F94a34225-aca8-14d5-43db-11c21c205ab4.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=517cd6d1c953dbe5e05123b6b311343a)

使用したい LLM モデルの切り替えは左上のスイッチで行います。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2Fd1c7fc93-dd09-4c64-ef57-1599de00009a.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=025c71dc794dc1c6323c3da41759e79b)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2Fd1c7fc93-dd09-4c64-ef57-1599de00009a.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=025c71dc794dc1c6323c3da41759e79b)

ollama で run されてたらすでに表示されていると思います。

OpenAI API 互換の環境設定については左下のアカウントのアイコンから設定画面に移動できます。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F35bd1380-db60-33ff-ec99-f9059753fb66.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=00a1a07c17df3cd13c6ff9c876cf86be)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F35bd1380-db60-33ff-ec99-f9059753fb66.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=00a1a07c17df3cd13c6ff9c876cf86be)

チャットをしばらく使っていないとVRAMからフラッシュされるみたいですね、便利！  
それではみなさんも快適な　ローカルLLMライフをお楽しみください！
