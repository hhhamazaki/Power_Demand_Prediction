# GitHub Copilot プロンプト集 (2025年8月版)

## 概要

本プロンプト集は、**GitHub Copilot**での効果的なプロンプトテンプレートと活用パターンを体系的に整理したリファレンスです。開発フローごとの最適化されたプロンプト例と、その実践的な使用方法を提供します。

### 主要な新機能（2025年版）

- 🤖 **GitHub Copilot Chat**: 自然言語での対話型コード支援
- 🔧 **GitHub Copilot Edits**: 複数ファイルの一括編集
- 🧠 **Copilot Agents**: 専門化されたAIエージェント（@workspace, @terminal, @vscode）
- 📂 **ワークスペース参照**: プロジェクト全体のコンテキスト理解
- 🔄 **インライン補完**: リアルタイムコード生成の高度化

---

プロジェクトのルートディレクトリに **`.github/copilot-instructions.md`** ファイルを作成することで、GitHub Copilotに対してプロジェクト全体に適用されるカスタム指示を与えることができます。

**例: `.github/copilot-instructions.md`**

```markdown
## 全体的なルール
- テストが通らない限りコミットしない
- 可読性の高いコードを心がける
- 不要なライブラリの導入を避ける
- セキュリティベストプラクティスに従う

## コーディング規約
- Python: PEP 8に準拠、type hintsを使用
- JavaScript/TypeScript: ESLintルールに従う
- 関数・変数名は英語で、説明的に命名
- コメントよりも説明的な変数名を優先

## フレームワーク固有
- Django: クラスベースビューを優先
- React: 関数コンポーネント + Hooksを使用
- Express.js: async/awaitパターンを使用
```

### プロンプトファイルの準備

再利用可能なプロンプトを **`.github/prompts/`** フォルダに保存することで、Copilot Chatから簡単に呼び出して利用することができます。

#### 実用的なプロンプトファイル例

**1. コード補完 (`.github/prompts/complete-code.md`)**

```markdown
---
mode: ask
---
このコードの続きを補完してください。
- 既存のコードスタイルに合わせる
- 型安全性を重視する
- エラーハンドリングを含める
- 適切なコメントを付与
```

**2. コードの解釈 (`.github/prompts/explain-code.md`)**

```markdown
---
mode: ask
---
このコードの動作や意図を解説してください。
- 主要な処理の流れを段階的に説明
- 重要な変数や関数の役割を明記
- 依存関係やアーキテクチャについても言及
- 初学者にも分かるように簡潔に
```

**3. コードリファクタリング (`.github/prompts/refactor.md`)**

```markdown
---
mode: ask
---
このコードのリファクタリング提案をしてください。
- 可読性を最優先する
- 複雑度を下げる（ネストの深さ軽減、関数分割）
- パフォーマンス改善が可能なら提案
- 外部仕様は変更しない
- SOLID原則に従う
```

**4. 単体テストの生成 (`.github/prompts/add-unit-tests.md`)**

```markdown
---
mode: ask
---
このコードに包括的な単体テストを作成してください。
- フレームワーク: pytest（Python）/ Jest（JavaScript/TypeScript）
- 正常系・異常系・境界値テストを含める
- テストケースの説明コメントを入れる
- 外部APIコールはモック化する
- カバレッジ90%以上を目指す
```

**5. セキュリティレビュー (`.github/prompts/security-review.md`)**

```markdown
---
mode: ask
---
このコードをセキュリティの観点でレビューしてください。
- OWASP Top 10の脆弱性をチェック
- 入力値検証の不備を指摘
- 認証・認可の実装を確認
- 機密情報の漏洩リスクを評価
- 具体的な修正提案を提示
```

**6. パフォーマンス最適化 (`.github/prompts/optimize-performance.md`)**

```markdown
---
mode: ask
---
このコードのパフォーマンスを最適化してください。
- 時間計算量・空間計算量を改善
- データベースクエリの効率化
- メモリ使用量の削減
- 非同期処理の活用
- ボトルネックの特定と解決策を提示
```

**7. ドキュメント生成 (`.github/prompts/generate-docs.md`)**

```markdown
---
mode: ask
---
このコードの包括的なドキュメントを作成してください。
- API仕様（OpenAPI/Swagger形式）
- 関数・クラスのdocstring
- 使用例とサンプルコード
- セットアップと設定手順
- トラブルシューティング情報
```

**8. コードレビュー (`.github/prompts/code-review.md`)**

```markdown
---
mode: ask
---
このコードを総合的にコードレビューしてください。
- 可読性・保守性・拡張性の観点で評価
- コーディング規約への準拠状況
- 潜在的なバグや問題点を指摘
- アーキテクチャ上の改善提案
- 優先度付きで改善点をリストアップ
```

#### プロンプトファイルの活用方法

**セットアップ:**
1. プロジェクトルートに **`.github/prompts/`** フォルダを作成
2. 再利用したい指示内容を `.md` ファイルとして保存
3. VS CodeのCopilot Chatで使用

**呼び出し方法:**
```
# エージェント + プロンプトファイルの組み合わせ
@workspace #refactor
@editor #add-unit-tests
@terminal #optimize-performance

# 複数ファイルを対象とした操作
@workspace #security-review
```

---

## 2025年版 新機能の活用法

### 🤖 Copilot Agents の活用

**@workspace**: プロジェクト全体のコンテキストを理解
```
@workspace この機能をプロジェクト全体で統一するためのリファクタリング提案
```

**@terminal**: コマンドライン操作を支援
```
@terminal Dockerコンテナを起動してPythonアプリをデバッグ実行したい
```

**@vscode**: VS Code固有の操作を支援
```
@vscode このプロジェクトに適したデバッグ設定を作成して
```

### 🔧 GitHub Copilot Edits の活用

複数ファイルにまたがる大規模なリファクタリングや機能追加に使用:

1. **Ctrl+Shift+I** でCopilot Editsパネルを開く
2. 変更したいファイルを選択
3. 自然言語で変更内容を指示
4. 提案された変更を確認・適用

### 📂 ワークスペース参照の活用

プロジェクト全体の一貫性を保つための機能:

```
# 例: 新機能追加時
@workspace 既存のAPIパターンに合わせてユーザー管理機能を追加して

# 例: 設定統一
@workspace プロジェクト全体でログフォーマットを統一して
```

---

## 実践的な活用パターン

### 1. 新機能開発フロー

```markdown
1. @workspace #explain-requirements (要件の詳細化)
2. @workspace #design-architecture (アーキテクチャ設計)
3. @editor #complete-code (実装)
4. @editor #add-unit-tests (テスト作成)
5. @workspace #security-review (セキュリティ確認)
```

### 2. レガシーコード改善フロー

```markdown
1. @editor #explain-code (既存コードの理解)
2. @editor #refactor (リファクタリング)
3. @editor #add-unit-tests (テストカバレッジ向上)
4. @workspace #update-docs (ドキュメント更新)
```

### 3. バグ修正フロー

```markdown
1. @workspace #analyze-bug (バグ原因の特定)
2. @editor #fix-bug (修正実装)
3. @editor #add-regression-tests (回帰テスト追加)
4. @workspace #impact-analysis (影響範囲の分析)
```

---

## チーム設定とベストプラクティス

### 組織レベルでの設定

1. **利用ポリシーの策定**: セキュリティ要件、コード品質基準
2. **共通プロンプトの整備**: チーム標準のプロンプトファイル作成
3. **レビュープロセスの統合**: Copilot生成コードのレビュー基準
4. **トレーニング実施**: チームメンバーへの活用方法教育

### セキュリティ考慮事項

- 機密情報をプロンプトに含めない
- 生成されたコードは必ず人間がレビュー
- ライセンス問題のチェック
- 依存関係の脆弱性確認

---

## 次のステップ

GitHub Copilotの導入と設定が完了したら、以下のステップで習熟度を向上させましょう:

1. **基本機能の習得**: 日常の開発ワークフローに組み込む
2. **高度な機能の探索**: エージェント機能、ワークスペース参照の活用
3. **チーム標準化**: 組織でのプロンプト共有と品質向上
4. **継続的改善**: 使用データを基にした効果測定と改善

GitHub Copilotは単なるツールではなく、開発チームの生産性と品質向上を支援するパートナーです。適切な設定と活用により、その真価を発揮できるでしょう。
