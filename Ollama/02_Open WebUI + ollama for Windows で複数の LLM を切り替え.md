[[ ローカル LLM ] Open WebUI + ollama for Windows で複数の LLM を切り替えて使ってみた #初心者 - Qiita](https://qiita.com/Yuzpomz/items/04a4e908c82937b84720)

# ollama の起動と確認

ollama は Windowws が起動したら自動的に起動していますが念のため確認をしますね

ブラウザで [http://localhost:11434](http://localhost:11434/) にアクセスします

[ Ollama is running ]  
の文字が表示されたらOKです。

起動していない場合は接続エラーの画面になります。ollama を起動してみましょう。  
ついでに ollama list で登録済みモデルが表示されます。

```
ollama
ollama serve
ollama list

NAME                 ID              SIZE      MODIFIED
qwen2.5:7b           845dbda0ea48    4.7 GB    2 days ago
```

# Open WebUI の起動と確認

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

# Open WebUI へのモデルの追加

左下のアイコンから 「設定」-->「 管理者画面」 を表示させて、「モデル」を表示させると「Ollama.com からモデルをプル」という項目があります。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2Fd0e37983-62d9-bc9d-389e-8f51aab4517a.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=bd6b0d891533925780ef4b05701ac7da)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2Fd0e37983-62d9-bc9d-389e-8f51aab4517a.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=bd6b0d891533925780ef4b05701ac7da)

ここにモデルタグを入力するとモデルがダウンロードされて open webui から使えるようになります。すぐに使えるモデルタグは ollama.com で検索して確認できます。

登録の終わったモデルは「モデルを選択」のところから確認できます。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F65abd7ae-6d9e-5a48-78db-0a783e356936.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=644a67c535861137dca5207d76e0bc5e)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F65abd7ae-6d9e-5a48-78db-0a783e356936.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=644a67c535861137dca5207d76e0bc5e)

# 複数のLLMを使ってみましょ

Open WebUI の左側メニューに「ワークスペース」というのがあるのでクリックして開くとモデルごとにプロンプトを入力して使えるようになっています。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2Fa5727533-6e52-d7b5-c175-a65b5470cea4.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9764b6471918ed647c95835942d5e8a0)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2Fa5727533-6e52-d7b5-c175-a65b5470cea4.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9764b6471918ed647c95835942d5e8a0)

## Qwen 2.5 さんにあいさつしてみた

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F05145cf9-b2bd-a8eb-2f75-ee613a8d994c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=88ffbf5952e7969046866de5ba6d6c8d)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F05145cf9-b2bd-a8eb-2f75-ee613a8d994c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=88ffbf5952e7969046866de5ba6d6c8d)

## granite 3 さんに高い山を聞いてみた

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2Ffbd47c49-c31a-772b-ec52-f3e2176d0e15.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6b16a15a8ea50816847ea8e10972413e)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2Ffbd47c49-c31a-772b-ec52-f3e2176d0e15.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6b16a15a8ea50816847ea8e10972413e)

英語の方が精度が高いようですね～

## Llama-3-ELYZA-JP-8B-q4 さんにあいさつしてみた

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F50fc1ac6-19f9-6e7b-c0b0-b066787363f5.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=100e976ea17eafb314a4d47e6a8f431a)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3920228%2F50fc1ac6-19f9-6e7b-c0b0-b066787363f5.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=100e976ea17eafb314a4d47e6a8f431a)

モデルの違いが分かって面白いですね。  
それではみなさんも快適な　ローカルLLMライフをお楽しみください！

