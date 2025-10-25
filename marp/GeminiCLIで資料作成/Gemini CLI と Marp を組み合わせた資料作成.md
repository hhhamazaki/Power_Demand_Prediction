## Gemini CLI の利点
 - Gemini 2.5 Pro モデルが 1 日 2000 回まで無料で利用可能。
 - Google 検索能力が強力。
 - Claude Code と比較して、Windows での利用が容易でアクセスしやすい。
 - 無料で得た入力データが学習に使われる可能性があるため、個人 Google アカウントや無課金 API キーの使用には注意が必要 (ワークスペースアカウントや課金 API キー、VATEX AI の API は大丈夫)。

## Marp の活用
 - Markdown で書かれた文章をスライドに変換する技術。
 - CSS を使って見た目を細かく調整でき、プロンプトでスライドの分割も制御可能。
 - PDF、PowerPoint、HTML、画像など様々な形式で出力できる。
 - 自分でテンプレートを作成することで、自分専用のスライド AI エージェントを作成できる。

## セットアップ手順
1. **Node.js のインストール**: Gemini CLI の動作環境として必要。公式サイトからインストーラーをダウンロードして実行。
2. **Gemini CLI のインストール**: ターミナルで `npm install -g @google/gemini-cli` を実行。
3. **Gemini CLI の起動とログイン**: `gemini` と入力して起動し、Google アカウントでログインまたは API キーを入力。
4. **Marp のプレビュー環境の整備**: AI コーディングエディター「Cursor」(または VS Code 拡張機能が扱えるエディター) をインストールし、「Marp for VS Code」拡張機能を追加。これにより Markdown ファイルのプレビューが可能になる。

## 資料作成のワークフロー
1. **プロンプト (テンプレート) の作成**:
   - プロンプトで希望の見た目や雰囲気を伝える。
   - 既存のスライド画像や台本を Gemini CLI に読み込ませて、スタイリング、文体、レイアウトパターンを学習させる。
   - '@ファイル名' でファイルを Gemini に読み込ませることができる。
2. **資料の生成**:
   - 作成したルールを参考に、Marp の Markdown 形式で資料を生成するよう Gemini CLI に指示。
3. **フィードバックと改善**:
   - 生成されたスライドをプレビューし、問題点 (例: 文字サイズが大きすぎる) があればフィードバック。
   - Marp で PDF に出力し、その PDF を Gemini CLI に読み込ませて分析・修正案を提案させる。
   - 修正が完了したら、これまでのフィードバックを反映させるようにルールファイルを更新し、次回の生成に活かす。
   - デザインの自由度が高く、様々な表現を試すことができる。

## 最終的な編集
 - Marp の PowerPoint 出力機能はまだ実験段階。
 - Canva を活用: Marp で作成した PDF を Canva にアップロードすると、テキストや画像が個別に編集可能な状態になるため、最終的な微調整やデザインの仕上げに非常に有効。

この方法により、AI を活用して資料作成の品質を保ちつつ、大幅な時間短縮が期待できます。

### Sources:
 - [https://github.com/google/gemini-cli](https://www.google.com/search?q=https://github.com/google/gemini-cli)
 - [https://www.youtube.com/watch?v=xzdllOuaP44](https://www.google.com/search?q=https://www.youtube.com/watch%3Fv%3DxzdllOuaP44)
 - [https://note.com/ai_saburou/n/necd2d5de3da2](https://www.google.com/search?q=https://note.com/ai_saburou/n/necd2d5de3da2)
    - '@ファイル名' でファイルを Gemini に読み込ませることができる。
