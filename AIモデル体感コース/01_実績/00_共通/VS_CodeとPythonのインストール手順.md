## 【重要】社内環境での事前準備：インストール申請

### [PCソフトウェアインストール申請](https://jera.service-now.com/sp?id=sc_cat_item&sys_id=dabea11747c68e10aa4e1ec4116d4378&sysparm_category=00473723c30282107be0325c05013110)が必要なソフト

- **Visual Studio Code** (エディタ)
- **GitHub Copilot Enterprise** (VS Codeの拡張機能、有料)
  ⚠️ **注意**: Free Plan使用禁止
- **Python** (プログラミング言語)

---

## 1. VS Codeのセットアップ

### 1.1 VS Codeのインストール

**Visual Studio Code**は無料の高機能コードエディタです。

🔗 **[VS Code公式サイト](https://code.visualstudio.com/)**

サイトにアクセスし、「**Download for Windows**」をクリックしてインストーラーをダウンロード。

**インストール時の推奨設定:**
- ✅ **「PATHへの追加」**を有効化
- ✅ **「右クリックメニューに追加」**（ファイル・フォルダからVS Code起動可能）
- ✅ **「サポートされているファイルの種類に関連付け」**

### 1.2 日本語化（オプション）

VS Codeを起動し、以下の手順で日本語化:

1. 左側のアクティビティバーから**拡張機能アイコン**（四角が4つ並んだ形）をクリック
2. 検索バーに**`Japanese`**と入力
3. **「Japanese Language Pack for Visual Studio Code」**をインストール
4. 右下のダイアログで**「Change Language and Restart」**をクリック

### 1.3 プロジェクトフォルダを開く

1. **VS Codeを起動**
2. メニューバーから**「ファイル」→「フォルダーを開く...」**を選択
3. 対象のプロジェクトフォルダを選択して開く

### 1.4 GitHub Copilot Enterpriseのインストール

🤖 **GitHub Copilot Enterprise**は、AIがコードの記述を支援してくれる強力なツールです。

**インストール手順:**
1. 拡張機能ビューで**「GitHub Copilot」**と検索してインストール
2. **「GitHub Copilot Chat」**もインストール（チャット機能用）
3. 画面右下の指示に従い、GitHubアカウントでサインイン

💰 **注意**: GitHub Copilot Enterpriseは有料サービスです。
⚠️ **社内注意**: Free Plan使用禁止

---

## 2. Pythonのインストール

### 2.1 推奨バージョンの確認

Python 3.10.11（研修カリキュラム動作確認済）を推奨します。

### 2.2 公式サイトからダウンロード

Python公式サイトにアクセスします。

🔗 **[python.org 公式サイト](https://www.python.org/downloads/release/python-31011/)**

Filesの「**Windows installer (64-bit)**」をクリックしてインストーラー（python-3.10.11-amd64.exeファイル）をダウンロードします。

### 2.3 Windowsでのインストール手順

⚠️ **最重要: PATH設定の有効化**  
インストーラーの最初の画面で、画面下部にある「**Add python.exe to PATH**」というチェックボックスに**必ずチェックを入れてください**。これを有効にすると、コマンドプロンプトから簡単にPythonを実行でき、後の開発が非常にスムーズになります。

**インストール手順:**
1. **「Add python.exe to PATH」にチェック** ✅
2. **「Install Now」**をクリックしてインストール開始
3. ユーザーアカウント制御の確認画面で**「はい」**をクリック
4. **「Setup was successful」**のメッセージ表示で完了

### 2.4 インストール確認

**VS Codeのターミナル**を開き（`Ctrl+`` または 表示→ターミナル）、以下のコマンドを入力:

```powershell
py --version
```

`Python 3.10.11`のようにバージョン番号が表示されれば成功です。

また、パッケージマネージャーpipも確認:
```powershell
py -m pip --version