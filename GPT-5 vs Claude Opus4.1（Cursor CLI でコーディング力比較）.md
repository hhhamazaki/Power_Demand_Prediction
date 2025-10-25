https://note.com/hirosuke_0520/n/na324f633a92a?sub_rt=share_pb

あなたはフルスタックエンジニア。
次の要件で **社内ミニCRM**（営業リード・案件・活動の管理ツール）を**1つのリポジトリ**で実装してください。
**禁止事項**: 外部SaaS/外部APIの利用（メール送信や認証も内製）。NPMパッケージの利用はOK。
>
## 技術スタック
>
* **フロント**: Next.js (App Router, TypeScript, React Server Components 可), Tailwind 任选
* **API**: Hono.js (TypeScript)
* **DB**: MySQL 8 以降
* **ORM**: Prisma
* **認証**: ローカルユーザー（email/password, bcrypt）。JWT発行→**HttpOnlyクッキー**で保持（SameSite=Lax, Secureは本番想定）。
* **Docker**: docker-compose で `web`（Next.js）, `api`（Hono）, `db`（MySQL） を起動。ホットリロード可。
>
## データモデル（Prisma schemaに反映）
>
* User: id, email(uniq), passwordHash, role('admin'|'member'), createdAt
* Company: id, name(uniq), domain?, notes?, createdAt
* Lead: id, companyId(FK), contactName, email?, phone?, source('web'|'referral'|'event'|'other'), status('new'|'qualified'|'lost'), score(int, default 0), createdAt
* Deal: id, leadId(FK), title, amount(decimal), stage('prospecting'|'proposal'|'negotiation'|'won'|'lost'), expectedCloseDate?, createdAt
* Activity: id, leadId(FK), type('note'|'task'|'call'|'email'), content, dueDate?, completed(boolean, default false), createdAt
>
## API要件（Hono 側）
>
* /auth/login \\[POST]: {email, password} → 成功でJWTをHttpOnlyクッキー設定
* /auth/logout \\[POST]
* /companies \\[GET/POST], /companies/\\:id \\[GET/PATCH/DELETE]
* /leads \\[GET/POST], /leads/\\:id \\[GET/PATCH/DELETE]
>
  * クエリ: `q`（名前/メール/電話のLIKE検索）, `page`, `pageSize`, `status`, `companyId`
* /deals \\[GET/POST], /deals/\\:id \\[GET/PATCH/DELETE]
* /activities \\[GET/POST], /activities/\\:id \\[GET/PATCH/DELETE]
* 認可: すべてのCRUDは**認証必須**。JWTミドルウェアで検証。
* バリデーション: zod でリクエストスキーマ検証。
* エラーフォーマット: `{error:{code:string,message:string}}` に統一。
* N+1禁止: Prisma `include/select` とインデックス設計で回避。
>
## フロント要件（Next.js 側）
>
* ルート:
>
  * /login: 認証フォーム（成功でダッシュボードへ）
  * /dashboard: KPIカード（本日作成のLeads数、Open Deals総額、今週期限の未完了Activities数）
  * /leads: 検索・フィルタ（status/company）、ページネーション、行クリックで詳細へ
  * /leads/\\[id]: Lead詳細＋関連Deals・Activitiesのタブ表示、Activitiesの追加・完了切替
  * /deals: **カンバンUI**（stageごとに列）。ドラッグ&ドロップでstage更新（楽観的更新→失敗時ロールバック）。
  * /companies: 一覧/新規/編集
* フォームはReact Hook Form + zodResolver。
* フェッチはNext.jsのサーバアクションまたはRoute Handler経由で**APIサーバ(Hono)へ**。
* ローディング/エンプティ状態/エラー表示を実装。
* アクセシビリティ配慮（フォームラベル、キーボードD\\&Dの代替ボタンでも更新可）。
>
## インフラ/運用
>
* `docker-compose.yml`:
>
  * db(MySQL): 永続ボリューム、ヘルスチェック
  * api: `./apps/api`, Port 8787（例）、`DATABASE_URL` を環境変数で注入
  * web: `./apps/web`, Port 3000、`API_BASE_URL` を環境変数で注入
* `Dockerfile` を web/api それぞれに用意（devはホットリロード）。
* `prisma migrate` と `prisma seed`（ダミーデータ生成: Companies 5件、Leads 50件、Deals 30件、Activities 100件）。
* `.env.example` を用意（DB, JWT\\_SECRET 等）。
>
## テスト
>
* API: Vitest + supertest で `/auth/login` 正常/異常, `/leads` 検索・ページネーション, `/deals` stage更新の冪等性 をカバー（最低5ケース）。
* E2E: Playwright で `login→lead作成→deal作成→kanbanでstage変更→activity完了` の1シナリオ。
>
## パフォーマンス/堅牢性
>
* ページネーションは**サーバ側**で実装（`limit/offset`）。
* インデックス: `Lead(status, createdAt)`, `Deal(stage)`, `Activity(leadId, completed, dueDate)` を作成。
* APIリトライ方針: フロントは書き込み系は**一回のみ**、失敗時はユーザーに再試行ボタン。
* CSRF: 状態変更系エンドポイントに**Originチェック**（同一オリジンのみ許可）。
>
## 期待する成果物
>
* リポジトリ直下の `README.md` に**起動手順**（`docker compose up -d`→ migrate/seed →アクセスURL）と**テスト実行方法**を明記。
* ディレクトリ構成、主要コード（Honoルーター、Nextページ/サーバアクション、Prismaスキーマ）、`docker-compose.yml`、各 `Dockerfile`。
* 主要画面のスクショ（開発サーバ実行後のキャプチャでOK）。
>
## 進め方
>
1. 最初に**タスク分割**と**ディレクトリ構成**、**ER図（テキストで可）**、**API仕様のOpenAPI草案**を10分相当で提示。
2. 承認後、実装→`README`→テスト→スクショの順に出力。
3. コードは**差分貼り付け可能な単位**で分割して提示。
>
## 評価基準
>
* 機能達成度（CRUD/検索/カンバン/認証）
* 信頼性（楽観的更新の失敗ロールバック、JWTと権限、N+1回避）
* 起動再現性（READMEどおりに立つか）
* テストの有無（API/E2E）
* コードの一貫性（型安全・責務分離）
>

このディレクトリ直下に{任意のディレクトリ名}というディレクトリを作り、そこをルートとしてください。

都度commitして下記リポジトリにpushしてください。
{事前に用意したGithubリポジトリURL}

実装を最後までやり切ってください。
