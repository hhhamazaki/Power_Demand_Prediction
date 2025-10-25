
# GitHub Pages デプロイ完全マニュアル

（例：プロジェクト名 Power_Demand_Prediction）

## 1. ローカル環境での準備

1. プロジェクトフォルダに移動
    
    ```
    cd C:\Users\hamazaki\Obsidian\AIモデル体感コース\01_実績\Power_Demand_Prediction\AI\dashboard
    ```
    
2. Git リポジトリを初期化
    
    ```
    git init
    ```
    
3. ファイルをステージング
    
    ```
    git add index.html
    ```
    
4. 初回コミット
    
    ```
    git commit -m "Add Power_Demand_Prediction"
    ```
    

---

## 2. GitHub リポジトリの作成

1. GitHub にログインし、**New repository** を作成
    - Owner: hhhamazaki
    - Repository name: Power_Demand_Prediction
2. 作成後、表示される **HTTPS または SSH のリポジトリ URL** をコピー

[hhhamazaki/Power_Demand_Prediction](https://github.com/hhhamazaki/Power_Demand_Prediction)

---

## 3. リモート接続とプッシュ

1. リモートを追加
    
    ```
    git remote add origin https://github.com/hhhamazaki/Power_Demand_Prediction.git
    ```
    
    - もし `Operation not permitted` エラーが出た場合：
        - 既存のリモートを削除
            
            ```
            git remote remove origin
            ```
            
        - `.git/config` の権限を確認し、必要なら修正
            
            ```
            takeown /f .git\config

            ```
            
        - 再度 `git remote add origin ...` を実行
2. ブランチ名を `main` に変更
    
    ```
    git branch -M main
    ```

1. **リモートの変更を取得する**:
    
    `git pull origin main`
    
    - これにより、リモートリポジトリの変更がローカルに統合されます。


1. **リモートの変更をプルする際にオプションを追加**:
    
    `git pull origin main --allow-unrelated-histories`
    
    - これにより、リモートの`main`ブランチから変更を取得し、ローカルの`main`ブランチにマージします。

2. GitHub へプッシュ
    
    ```
    git push -u origin main
    ```
    
    - ネットワーク障害で失敗した場合は再実行

---

## 4. GitHub Pages の設定

1. GitHub のリポジトリページ → **Settings → Pages**
2. **Build and deployment** を
    - Source: _Deploy from a branch_
    - Branch: _main_
    - Folder: _/(root)_  
        に設定し保存
3. 数分後、自動的に公開 URL が生成される
    
    ```
    https://hhhamazaki.github.io/Power_Demand_Prediction/
    ```
    

---

## 5. 動作確認

1. 上記 URL にアクセス
2. ページが表示されるか確認
3. ボタンやスクリプトが正しく動作するかテスト
4. 404 エラーが出た場合はリロード、または数分待機

---

## 6. トラブルシューティングまとめ

- **`Permission denied` / `Operation not permitted`**  
    → `.git/config` の権限確認、既存リモート削除後に再設定
- **`git push` タイムアウト**  
    → ネットワーク再接続後に再実行
- **公開されない**  
    → Settings → Pages の設定を再確認（Branch: main, Folder: /(root)）
- **404 エラー**  
    → 数分待機してからリロード
