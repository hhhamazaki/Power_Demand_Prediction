/**
 * ExpenseApp.js - メインアプリケーションコントローラー
 * 
 * UiPathコーディング規約準拠
 * - 依存性注入パターンの実装
 * - ES6クラス構文の使用
 * - イベントドリブンアーキテクチャ
 * - パフォーマンス最適化
 * 
 * @author リファクタリングプロジェクト
 * @version 2.0.0
 */

import { ValidationService } from './services/ValidationService.js';
import { StorageService } from './services/StorageService.js';
import { ExpenseService } from './services/ExpenseService.js';
import { ErrorHandler } from './utils/ErrorHandler.js';
import { PerformanceUtils, VirtualScrollManager } from './utils/PerformanceUtils.js';
import { ChartManager } from './components/ChartManager.js';
import { CONSTANTS } from './utils/Constants.js';

/**
 * メインアプリケーションクラス
 * 全体的なアプリケーション制御とページルーティングを管理
 */
export class ExpenseApp {
    constructor() {
        this.services = {};
        this.components = {};
        this.performanceMetrics = {};
        this.isInitialized = false;
        
        // パフォーマンス測定開始
        this.performanceMetrics.initStart = performance.now();
        
        // サービス初期化
        this.initializeServices();
        
        // イベントリスナー設定
        this.initializeEventListeners();
        
        // 仮想スクロール管理
        this.virtualScrollManager = null;
        
        // 現在のページトラッキング
        this.currentPage = 'dashboard';
        
        // データキャッシュ
        this.dataCache = new Map();
    }

    /**
     * サービス依存性注入とインスタンス化
     */
    initializeServices() {
        try {
            // コアサービス初期化
            this.services.errorHandler = new ErrorHandler();
            this.services.validationService = new ValidationService();
            this.services.storageService = new StorageService();
            this.services.expenseService = new ExpenseService(
                this.services.validationService,
                this.services.storageService,
                this.services.errorHandler
            );
            
            // コンポーネント初期化
            this.components.chartManager = new ChartManager();
            
            // パフォーマンスユーティリティ初期化（静的関数とクラスをラップ）
            this.components.performance = {
                debounce: PerformanceUtils.debounce,
                throttle: PerformanceUtils.throttle,
                VirtualScrollManager: VirtualScrollManager
            };
            
            console.log('✅ サービス初期化完了');
        } catch (error) {
            console.error('❌ サービス初期化エラー:', error);
            this.services.errorHandler?.handle(error, 'サービス初期化中にエラーが発生しました');
        }
    }

    /**
     * アプリケーション初期化
     */
    async initialize() {
        if (this.isInitialized) {
            console.warn('⚠️ アプリケーションは既に初期化済みです');
            return;
        }

        try {
            console.log('🚀 ExpenseApp初期化開始');
            
            // DOM準備確認
            if (document.readyState === 'loading') {
                await new Promise(resolve => {
                    document.addEventListener('DOMContentLoaded', resolve);
                });
            }

            // ページ解析とルーティング
            this.detectCurrentPage();
            
            // ページ固有の初期化
            await this.initializePage();
            
            // 仮想スクロール設定
            this.initializeVirtualScrolling();
            
            // グローバルエラーハンドリング設定
            this.setupGlobalErrorHandling();
            
            // パフォーマンス測定終了
            this.performanceMetrics.initEnd = performance.now();
            this.performanceMetrics.initDuration = this.performanceMetrics.initEnd - this.performanceMetrics.initStart;
            
            console.log(`✅ ExpenseApp初期化完了 (${this.performanceMetrics.initDuration.toFixed(2)}ms)`);
            this.isInitialized = true;
            
        } catch (error) {
            console.error('❌ アプリケーション初期化エラー:', error);
            this.services.errorHandler.handle(error, 'アプリケーションの初期化中にエラーが発生しました');
        }
    }

    /**
     * 現在のページを検出
     */
    detectCurrentPage() {
        const path = window.location.pathname;
        const hash = window.location.hash;
        
        if (path.includes('expense-register') || hash.includes('register')) {
            this.currentPage = 'register';
        } else if (path.includes('expense-report') || hash.includes('report')) {
            this.currentPage = 'report';
        } else if (path.includes('settings') || hash.includes('settings')) {
            this.currentPage = 'settings';
        } else if (path.includes('completion') || hash.includes('completion')) {
            this.currentPage = 'completion';
        } else {
            this.currentPage = 'dashboard';
        }
        
        console.log(`📍 現在のページ: ${this.currentPage}`);
    }

    /**
     * ページ固有の初期化処理
     */
    async initializePage() {
        const pageInitializers = {
            dashboard: () => this.initializeDashboard(),
            register: () => this.initializeExpenseRegister(),
            report: () => this.initializeExpenseReport(),
            list: () => this.initializeExpenseList(),
            settings: () => this.initializeSettings(),
            completion: () => this.initializeCompletion(),
            'expense-form': () => this.initializeExpenseRegister()
        };

        const initializer = pageInitializers[this.currentPage];
        if (initializer) {
            await initializer();
        }
    console.log('[LOG] this:', this);
    console.log('[LOG] window.appController:', window.appController);
    }

    // グローバルから呼ばれるページ切替
    showPage(pageKey) {
        const pages = {
            home: 'home-page',
            'expense-register': 'expense-register-page',
            'expense-list': 'expense-list-page',
            reports: 'reports-page',
            settings: 'settings-page',
            completion: 'completion-page',
            'expense-form': 'expense-form-page'
        };

        Object.values(pages).forEach(id => {
            const el = document.getElementById(id);
            if (el) el.classList.add('hidden');
        });

        const targetId = pages[pageKey] || pages.home;
        const target = document.getElementById(targetId);
        if (target) target.classList.remove('hidden');

        // 状態更新とページ初期化
        this.currentPage = pageKey === 'home' ? 'dashboard'
                         : pageKey === 'reports' ? 'report'
                         : pageKey === 'expense-register' ? 'register'
                         : pageKey === 'expense-list' ? 'list'
                         : pageKey;

        this.initializePage();
    }

    // 経費一覧ページ初期化
    async initializeExpenseList() {
        try {
            const expenses = await this.services.expenseService.getAllExpenses();
            this.renderExpenseTable(expenses);
        } catch (error) {
            console.error('❌ 経費一覧初期化エラー:', error);
            this.services.errorHandler.handle(error, '経費一覧の読み込み中にエラーが発生しました');
        }
    }

    /**
     * ダッシュボード初期化
     */
    async initializeDashboard() {
        console.log('📊 ダッシュボード初期化中...');
        
        try {
            // 統計データ取得
            const stats = await this.services.expenseService.getStatistics();
            
            // ダッシュボードカード更新
            this.updateDashboardCards(stats);
            
            // 最近の経費一覧表示 - feature removed
            
            console.log('✅ ダッシュボード初期化完了');
        } catch (error) {
            console.error('❌ ダッシュボード初期化エラー:', error);
            this.services.errorHandler.handle(error, 'ダッシュボードの読み込み中にエラーが発生しました');
        }
    }

    /**
     * 経費登録ページ初期化
     */
    async initializeExpenseRegister() {
        console.log('📝 経費登録ページ初期化中...');
        
        try {
            // フォーム要素取得
            const form = document.getElementById('expense-form');
            // 登録ハブ（expense-register-page）ではフォームが無いため、その場合は早期リターン
            if (!form) return;

            // フォーム送信イベント（多重バインド防止）
            if (!form.dataset.bound) {
                form.addEventListener('submit', this.handleExpenseSubmit.bind(this));
                form.dataset.bound = 'true';
            }
            
            // リアルタイムバリデーション
            this.setupRealTimeValidation();
            
            // カテゴリ選択肢設定
            this.setupCategoryOptions();
            
            console.log('✅ 経費登録ページ初期化完了');
        } catch (error) {
            console.error('❌ 経費登録ページ初期化エラー:', error);
            this.services.errorHandler.handle(error, '経費登録ページの初期化中にエラーが発生しました');
        }
    }

    /**
     * 経費レポートページ初期化
     */
    async initializeExpenseReport() {
        console.log('📈 経費レポートページ初期化中...');
        
        try {
            // 経費データ読み込み
            await this.loadExpenseReport();
            
            // Chart.js初期化
            await this.components.chartManager.initialize();
            
            // チャート描画
            await this.renderCharts();
            
            // テーブルソート機能
            this.setupTableSorting();
            
            console.log('✅ 経費レポートページ初期化完了');
        } catch (error) {
            console.error('❌ 経費レポートページ初期化エラー:', error);
            this.services.errorHandler.handle(error, 'レポートページの初期化中にエラーが発生しました');
        }
    }

    /**
     * 設定ページ初期化
     */
    async initializeSettings() {
        console.log('⚙️ 設定ページ初期化中...');
        
        try {
            // 設定値読み込み
            this.loadUserSettings();
            
            // 設定変更イベント
            this.setupSettingsHandlers();
            
            console.log('✅ 設定ページ初期化完了');
        } catch (error) {
            console.error('❌ 設定ページ初期化エラー:', error);
            this.services.errorHandler.handle(error, '設定ページの初期化中にエラーが発生しました');
        }
    }

    /**
     * 完了ページ初期化
     */
    async initializeCompletion() {
        console.log('🎉 完了ページ初期化中...');
        
        try {
            // 完了コード表示
            this.displayCompletionCodes();
            
            console.log('✅ 完了ページ初期化完了');
        } catch (error) {
            console.error('❌ 完了ページ初期化エラー:', error);
            this.services.errorHandler.handle(error, '完了ページの初期化中にエラーが発生しました');
        }
    }

    /**
     * イベントリスナー初期化
     */
    initializeEventListeners() {
        // デバウンス機能付きリサイズハンドラー
        const debouncedResize = this.components.performance?.debounce(
            () => this.handleWindowResize(),
            CONSTANTS.PERFORMANCE_CONFIG.DEBOUNCE_DELAY
        ) || (() => this.handleWindowResize());
        
        window.addEventListener('resize', debouncedResize);
        
        // パフォーマンス監視
        this.setupPerformanceMonitoring();
    }

    /**
     * 仮想スクロール初期化
     */
    initializeVirtualScrolling() {
        const tableContainer = document.querySelector('.expense-table-container');
        const table = document.querySelector('.expense-table tbody');

        // 仮想スクロールはテーブルの tbody に対して行う（wrapper を置換して生JSONを表示する問題を防ぐ）
        if (tableContainer && table) {
            this.virtualScrollManager = new this.components.performance.VirtualScrollManager(
                table, // tbody を渡す
                60  // itemHeight
            );
            console.log('✅ 仮想スクロール初期化完了');
        }
    }

    /**
     * 経費テーブル行のレンダリング
     */
    renderExpenseTableRow(expense, index) {
        const isProcessed = (expense.status === (CONSTANTS.STATUS_TYPES?.PROCESSED || '処理済み'));
        const statusKey = this.getStatusKey(expense.status);
        return `
        <tr data-testid="expense-row-${index}">
                <td>${this.escapeHtml(expense.title || expense.description || '')}</td>
                <td>${this.escapeHtml(expense.type || expense.category || '')}</td>
                <td class="text-right">¥${Number(expense.amount || 0).toLocaleString()}</td>
                <td>${this.escapeHtml(expense.remark || '')}</td>
                <td>${this.escapeHtml(String(expense.code || ''))}</td>
                <td class="status-${statusKey}">${this.getStatusText(expense.status)}</td>
                <td>${this.formatDateForCsv(expense.date)}</td>
                <td>
            ${!isProcessed ? `<button class="btn btn-secondary" onclick="appController.markExpenseProcessed('${expense.id}')">処理</button>` : ''}
            <button class="btn btn-danger" onclick="appController.deleteExpense('${expense.id}')">削除</button>
                </td>
            </tr>
        `;
    }

    /**
     * 経費フォーム送信処理
     */
    async handleExpenseSubmit(event) {
        event.preventDefault();
        // 前回の完了コードをクリア（最新の登録結果のみを表示するため）
        try {
            this.services.storageService.saveCompletionCodes?.([]);
        } catch (_) {}
        
        const submitButton = event.target.querySelector('button[type="submit"]');
        
        try {
            // ボタン無効化
            submitButton.disabled = true;
            submitButton.classList.add('loading');
            
            // フォームデータ取得
            const formData = new FormData(event.target);
            const expenseData = {
                title: formData.get('title') || '',
                type: formData.get('type') || '',
                amount: parseFloat(formData.get('amount')) || 0,
                date: formData.get('date') || '',
                remark: formData.get('remark') || ''
            };

            // 経費追加
            const result = await this.services.expenseService.addExpense(expenseData);
            
            if (result && (result.success || result.id)) {
                // 成功メッセージ
                this.services.errorHandler.showToast('経費が正常に登録されました', 'success');
                
                // フォームリセット
                event.target.reset();
                
                // キャッシュクリア
                this.clearDataCache();
                
                // 完了コード保存（前回分をクリアし今回分のみ保持）
                if (result.code && typeof this.services.storageService.saveCompletionCodes === 'function') {
                    this.services.storageService.saveCompletionCodes([String(result.code)]);
                }

                // 完了ページへ
                this.showPage('completion');
            }
            
        } catch (error) {
            console.error('❌ 経費登録エラー:', error);
            this.services.errorHandler.handle(error, '経費の登録中にエラーが発生しました');
        } finally {
            // ボタン復元
            submitButton.disabled = false;
            submitButton.classList.remove('loading');
        }
    }

    /**
     * ダッシュボードカード更新
     */
    updateDashboardCards(stats) {
        const setText = (id, text) => {
            const el = document.getElementById(id);
            if (el) el.textContent = text;
        };

        // 合計金額
        setText('dashboard-total-amount', `¥${(stats.totalAmount || 0).toLocaleString()}`);
        const amountSmall = document.getElementById('dashboard-total-amount-small');
        if (amountSmall) amountSmall.textContent = (stats.totalCount || 0) > 0 ? '集計済み' : 'データなし';

        // 登録件数
        setText('dashboard-total-count', `${stats.totalCount || 0}`);
        const countSmall = document.getElementById('dashboard-total-count-small');
        if (countSmall) countSmall.textContent = (stats.totalCount || 0) > 0 ? '集計済み' : 'データなし';

        // 処理率
    const total = stats.totalCount || 0;
    const processed = stats.processedCount || 0;
    // 小数第一位まで表示
    const rate = total > 0 ? (processed / total) * 100 : 0;
    setText('dashboard-processing-rate', `${Number(rate).toFixed(1)}%`);
        const prSmall = document.getElementById('dashboard-processing-rate-small');
        if (prSmall) prSmall.textContent = `処理済み: ${processed}件 / 全体: ${total}件`;
    }

    // ...loadRecentExpenses removed per project request...

    // 行アクション: 処理済に更新
    async markExpenseProcessed(expenseId) {
        try {
            await this.services.expenseService.updateExpenseStatus(
                expenseId,
                CONSTANTS.STATUS_TYPES?.PROCESSED || '処理済み'
            );
            this.services.errorHandler.showToast('処理済に更新しました', 'success');
            // 画面リフレッシュ
            await this.initializePage();
        } catch (error) {
            console.error('❌ ステータス更新エラー:', error);
            this.services.errorHandler.handle(error, 'ステータス更新中にエラーが発生しました');
        }
    }

    // 一括: 未処理を処理済に
    async markPendingAsProcessed() {
        try {
            const all = await this.services.expenseService.getAllExpenses();
            const target = all.filter(e => e.status !== (CONSTANTS.STATUS_TYPES?.PROCESSED || '処理済み'));
            let updated = 0;
            for (const e of target) {
                await this.services.expenseService.updateExpenseStatus(
                    e.id,
                    CONSTANTS.STATUS_TYPES?.PROCESSED || '処理済み'
                );
                updated++;
            }
            this.services.errorHandler.showToast(`${updated}件を処理済にしました`, 'success');
            await this.initializePage();
        } catch (error) {
            console.error('❌ 一括ステータス更新エラー:', error);
            this.services.errorHandler.handle(error, '一括更新中にエラーが発生しました');
        }
    }

    // 一括: 全件処理済に
    async markAllAsProcessed() {
        try {
            const all = await this.services.expenseService.getAllExpenses();
            let updated = 0;
            for (const e of all) {
                if (e.status !== (CONSTANTS.STATUS_TYPES?.PROCESSED || '処理済み')) {
                    await this.services.expenseService.updateExpenseStatus(
                        e.id,
                        CONSTANTS.STATUS_TYPES?.PROCESSED || '処理済み'
                    );
                    updated++;
                }
            }
            this.services.errorHandler.showToast(`${updated}件を処理済にしました`, 'success');
            await this.initializePage();
        } catch (error) {
            console.error('❌ 全件処理済エラー:', error);
            this.services.errorHandler.handle(error, '全件処理済中にエラーが発生しました');
        }
    }

    // ステータスの表示/クラス用キーに変換
    getStatusKey(status) {
        const P = CONSTANTS.STATUS_TYPES || { PENDING: '未処理', PROCESSED: '処理済み' };
        if (status === P.PROCESSED || status === 'processed') return 'processed';
        if (status === P.PENDING || status === 'pending') return 'pending';
        return 'unknown';
    }

    // ステータスの表示テキスト
    getStatusText(status) {
        const P = CONSTANTS.STATUS_TYPES || { PENDING: '未処理', PROCESSED: '処理済み' };
        if (status === P.PROCESSED || status === 'processed') return P.PROCESSED;
        if (status === P.PENDING || status === 'pending') return P.PENDING;
        return status;
    }

    /**
     * チャート描画
     */
    async renderCharts() {
        try {
            // 表示用の元データ（全件）取得
            const allExpenses = await this.services.expenseService.getAllExpenses();

            // 月別チャート描画（index_refactored.html の canvas ID に合わせる）
            await this.components.chartManager.createMonthlyChart(allExpenses, 'monthlyChart');

            // カテゴリ別チャート描画
            await this.components.chartManager.createCategoryChart(allExpenses, 'categoryChart');
        } catch (error) {
            console.error('❌ チャート描画エラー:', error);
            this.services.errorHandler.handle(error, 'チャートの描画中にエラーが発生しました');
        }
    }

    /**
     * リアルタイムバリデーション設定
     */
    setupRealTimeValidation() {
        const fields = [
            { id: 'title', validate: (v) => this.services.validationService.validateTitle(v) },
            { id: 'type', validate: (v) => this.services.validationService.validateCategory(v) },
            { id: 'amount', validate: (v) => this.services.validationService.validateAmount(v) },
            { id: 'remark', validate: (v) => this.services.validationService.validateRemark(v) }
        ];

        fields.forEach(({ id, validate }) => {
            const field = document.getElementById(id);
            if (field) {
                const run = () => {
                    const result = validate(field.value);
                    const errorElement = document.querySelector(`#${id}-error`);
                    if (result.isValid) {
                        field.classList.remove('error');
                        if (errorElement) errorElement.textContent = '';
                    } else {
                        field.classList.add('error');
                        if (errorElement) errorElement.textContent = result.message;
                    }
                };
                const debouncedValidation = this.components.performance?.debounce(
                    run,
                    CONSTANTS.PERFORMANCE_CONFIG.DEBOUNCE_DELAY
                ) || run;
                field.addEventListener('input', debouncedValidation);
                field.addEventListener('blur', run);
            }
        });
    }

    /**
     * フィールドバリデーション
     */
    validateField(fieldName, value) {
        try {
            const result = this.services.validationService.validateField(fieldName, value);
            const field = document.getElementById(fieldName);
            const errorElement = document.querySelector(`#${fieldName}-error`);
            
            if (result.isValid) {
                field.classList.remove('error');
                if (errorElement) errorElement.textContent = '';
            } else {
                field.classList.add('error');
                if (errorElement) errorElement.textContent = result.message;
            }
            
            return result.isValid;
        } catch (error) {
            console.error(`❌ ${fieldName}バリデーションエラー:`, error);
            return false;
        }
    }

    /**
     * グローバルエラーハンドリング設定
     */
    setupGlobalErrorHandling() {
        window.addEventListener('error', (event) => {
            console.error('❌ グローバルエラー:', event.error);
            this.services.errorHandler.handle(event.error, 'アプリケーションでエラーが発生しました');
        });

        window.addEventListener('unhandledrejection', (event) => {
            console.error('❌ 未処理のPromise拒否:', event.reason);
            this.services.errorHandler.handle(event.reason, '非同期処理でエラーが発生しました');
        });
    }

    // HTML側のonclickから呼ばれるブリッジ: フォーム送信
    submitExpense() {
        const form = document.getElementById('expense-form');
        if (form) {
            const evt = new Event('submit', { bubbles: true, cancelable: true });
            form.dispatchEvent(evt);
        }
    }

    // CSVファイルの取り込み
    async handleFileUpload(event) {
        // 入力要素を取得（event.target が input でない場合はIDから探す）
        const inputEl = (event && event.target && event.target.files) ? event.target
            : document.getElementById('expense-file-upload') || document.getElementById('settings-import-csv');
        const file = inputEl?.files?.[0];
        if (!file) return;

        // 処理中は入力を無効化して多重送信を防止
        try {
            inputEl.disabled = true;
        } catch (_) {}

        // ファイル検証（サイズ/拡張子）
        try {
            const vr = this.services.validationService?.validateFile?.(file);
            if (vr && !vr.isValid) {
                this.services.errorHandler.showToast(vr.message || '不正なファイルです', 'warning');
                try { inputEl.value = ''; inputEl.disabled = false; } catch(_) {}
                return;
            }
        } catch (_) {}

        // 前回の完了コードをクリア（最新の取り込み結果のみを表示するため）
        try {
            this.services.storageService.saveCompletionCodes?.([]);
        } catch (_) {}

        try {
            const text = await file.text();
            const rawLines = text.split(/\r?\n/).filter(l => l.trim());
            if (rawLines.length === 0) throw new Error('CSVが空です');

            // 簡易CSVパーサ（引用符対応）
            const parseCsvLine = (line) => {
                const out = [];
                let cur = '';
                let inQuotes = false;
                for (let i = 0; i < line.length; i++) {
                    const ch = line[i];
                    if (ch === '"') {
                        if (inQuotes && line[i+1] === '"') { cur += '"'; i++; }
                        else { inQuotes = !inQuotes; }
                    } else if (ch === ',' && !inQuotes) {
                        out.push(cur);
                        cur = '';
                    } else {
                        cur += ch;
                    }
                }
                out.push(cur);
                return out.map(s => s.trim());
            };

            // ヘッダー判定（日本語ヘッダー対応）
            const firstFields = parseCsvLine(rawLines[0]);
            // ヘッダー候補を拡充（コード・ステータスも許容）
            const headerNames = ['タイトル','種別','金額','備考','コード','ステータス','登録日','日付'];
            const hasHeader = firstFields.some(f => headerNames.includes(f));

            let startIndex = 0;
            // 既定は5列（タイトル, 種別, 金額, 登録日, 備考）
            let indexMap = { title: 0, type: 1, amount: 2, date: 3, remark: 4, code: -1, status: -1 };
            if (hasHeader) {
                // 動的に列インデックスを決定
                const idx = (nameList) => nameList.reduce((acc, n) => acc !== -1 ? acc : firstFields.indexOf(n), -1);
                indexMap = {
                    title: idx(['タイトル','件名','名称']),
                    type: idx(['種別','カテゴリ','カテゴリー']),
                    amount: idx(['金額','金額(円)']),
                    date: idx(['登録日','日付','日時']),
                    remark: idx(['備考','メモ','摘要']),
                    code: idx(['コード','管理番号','code','Code','CODE']),
                    status: idx(['ステータス','状態','status','Status','STATUS'])
                };
                startIndex = 1;
            } else {
                // ヘッダーなし: エクスポート仕様（7列）か旧5列想定かで分岐
                if (firstFields.length >= 7) {
                    // エクスポート順: [タイトル, 種別, 金額, 備考, コード, ステータス, 登録日]
                    indexMap = { title: 0, type: 1, amount: 2, remark: 3, code: 4, status: 5, date: 6 };
                } else {
                    // 旧来型: 先頭が日付なら[日付, タイトル, 種別, 金額, 備考]、そうでなければ[タイトル, 種別, 金額, 登録日, 備考]
                    const isDate = /^\d{4}[\/-]\d{1,2}[\/-]\d{1,2}$/.test(firstFields[0]);
                    if (isDate) {
                        indexMap = { date: 0, title: 1, type: 2, amount: 3, remark: 4, code: -1, status: -1 };
                    } else {
                        indexMap = { title: 0, type: 1, amount: 2, date: 3, remark: 4, code: -1, status: -1 };
                    }
                }
            }

            const items = rawLines.slice(startIndex).map(line => {
                const cols = parseCsvLine(line);
                const pick = (k) => {
                    const i = indexMap[k];
                    return (i !== -1 && i < cols.length) ? cols[i] : '';
                };
                const title = pick('title');
                const type = pick('type');
                const amount = Number(pick('amount').replace(/[,\s]/g, '')) || 0;
                let date = pick('date');
                let remark = pick('remark');
                const rawStatus = pick('status');
                const code = pick('code');
                // 日付妥当性チェック: 無効なら当日付に補正し、元の値は備考に追記
                if (!this.isValidDateString(date)) {
                    if (date) {
                        remark = remark ? `${remark} ${date}` : date;
                    }
                    date = new Date().toLocaleDateString('ja-JP');
                }
                const status = this.normalizeStatus(rawStatus);
                // コードはCSV指定があれば保持する
                return { title, type, amount, date, remark, ...(status ? { status } : {}), ...(code ? { code } : {}) };
            });
            const result = await this.services.expenseService.addMultipleExpenses(items);
            const codes = (result?.results || [])
                .filter(r => r.success && r.data && r.data.code)
                .map(r => String(r.data.code));

            // 完了コード保存（今回分に置き換え）
            if (codes.length && typeof this.services.storageService.saveCompletionCodes === 'function') {
                this.services.storageService.saveCompletionCodes(codes);
            }

            this.services.errorHandler.showToast(`${items.length}件のCSVを取り込みました`, 'success');

            // 完了ページへ遷移（バックアップ仕様）
            this.showPage('completion');
        } catch (error) {
            console.error('❌ CSV取り込みエラー:', error);
            this.services.errorHandler.handle(error, 'CSV取り込み中にエラーが発生しました');
        } finally {
            // 入力をクリアして再選択を可能にする
            try {
                if (inputEl) {
                    inputEl.value = '';
                    inputEl.disabled = false;
                }
                const settingsImport = document.getElementById('settings-import-csv');
                if (settingsImport) settingsImport.value = '';
            } catch (_) {}
        }
    }

    // CSVエクスポート
    async downloadExpensesAsCsv() {
        try {
            const expenses = await this.services.expenseService.getAllExpenses();
            // ヘッダは変更しない（元の順序・名称）
            const header = ['タイトル','種別','金額','備考','コード','ステータス','登録日'];
            const rows = expenses.map(e => [
                e.title || '',
                e.type || '',
                e.amount || 0,
                e.remark || '',
                String(e.code || ''),
                this.getStatusText(e.status || ''),
                this.formatDateForCsv(e.date)
            ]);
            // 文字化け対策: UTF-8 BOMを付与し、各フィールドを必ずダブルクォートで囲む
            const csv = [header, ...rows]
                .map(r => r
                    .map(v => `"${String(v).replace(/"/g, '""')}"`)
                    .join(',')
                )
                .join('\r\n');
            const bom = '\uFEFF';
            const blob = new Blob([bom, csv], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            // 元ファイル仕様に合わせて日付入りファイル名にする（YYYYMMDD）
            const now = new Date();
            const yyyy = now.getFullYear();
            const mm = String(now.getMonth() + 1).padStart(2, '0');
            const dd = String(now.getDate()).padStart(2, '0');
            a.download = `経費データ_${yyyy}${mm}${dd}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error('❌ CSVエクスポートエラー:', error);
            this.services.errorHandler.handle(error, 'CSVエクスポート中にエラーが発生しました');
        }
    }

    // ソート切替（列キー＋列インデックス対応）
    async toggleSort(column, columnIndex = null) {
        this.sortState = this.sortState || { column: null, asc: true };
        if (this.sortState.column === column) {
            this.sortState.asc = !this.sortState.asc;
        } else {
            this.sortState.column = column;
            this.sortState.asc = true;
        }

        const expenses = await this.services.expenseService.getAllExpenses();
        const dir = this.sortState.asc ? 1 : -1;
        const sorted = [...expenses].sort((a, b) => {
            const av = a[column];
            const bv = b[column];
            if (column === 'amount') return (av - bv) * dir;
            if (column === 'date') return (new Date(av) - new Date(bv)) * dir;
            return String(av||'').localeCompare(String(bv||'')) * dir;
        });
    this.renderExpenseTable(sorted);
        // ヘッダービジュアルを更新（インデックス優先）
        this.updateSortHeaderStylesByIndex(columnIndex, this.sortState.asc, column);
        // 列ハイライトを更新（インデックス優先）
        this.highlightSortedColumnByIndex(columnIndex, this.sortState.asc, column);
    }

    /**
     * パフォーマンス監視設定
     */
    setupPerformanceMonitoring() {
        if (typeof PerformanceObserver !== 'undefined') {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.entryType === 'measure' && entry.name.startsWith('expense-app')) {
                        console.log(`⚡ ${entry.name}: ${entry.duration.toFixed(2)}ms`);
                    }
                }
            });
            
            observer.observe({ entryTypes: ['measure'] });
        }
    }

    /**
     * ウィンドウリサイズハンドラー
     */
    handleWindowResize() {
        // チャートリサイズ
        if (this.components.chartManager && this.currentPage === 'report') {
            this.components.chartManager.resizeCharts();
        }
        
        // 仮想スクロール更新
        if (this.virtualScrollManager && this.virtualScrollManager.render) {
            this.virtualScrollManager.render();
        }
    }

    /**
     * データキャッシュクリア
     */
    clearDataCache() {
        this.dataCache.clear();
        console.log('🗑️ データキャッシュをクリアしました');
    }

    /**
     * 日付フォーマット
     */
    formatDate(dateString) {
        try {
            return new Intl.DateTimeFormat('ja-JP', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
            }).format(new Date(dateString));
        } catch (error) {
            return dateString;
        }
    }

    // CSV用: 元仕様に合わせて 2025/8/29 の形式（ゼロ詰めなし）で出力
    formatDateForCsv(dateString) {
        try {
            const d = new Date(dateString);
            const y = d.getFullYear();
            const m = d.getMonth() + 1; // 1-12
            const day = d.getDate();
            if (!y || !m || !day) return dateString || '';
            return `${y}/${m}/${day}`;
        } catch (_) {
            return dateString || '';
        }
    }

    /**
     * HTML エスケープ
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // 日付形式妥当性チェック（YYYY/M/D, YYYY-MM-DD 等を許容）
    isValidDateString(s) {
        if (!s || typeof s !== 'string') return false;
        const trimmed = s.trim();
        const m = trimmed.match(/^(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})$/);
        if (!m) return false;
        const y = Number(m[1]);
        const mo = Number(m[2]);
        const d = Number(m[3]);
        const dt = new Date(y, mo - 1, d);
        return dt.getFullYear() === y && (dt.getMonth() + 1) === mo && dt.getDate() === d;
    }

    // ステータス値の正規化（日本語/英語/大小文字差異に対応）
    normalizeStatus(s) {
        if (!s || typeof s !== 'string') return '';
        const v = s.trim().toLowerCase();
        if (v === '処理済み' || v === 'processed') return (CONSTANTS.STATUS_TYPES?.PROCESSED || '処理済み');
        if (v === '未処理' || v === 'pending' || v === '未') return (CONSTANTS.STATUS_TYPES?.PENDING || '未処理');
        if (v === '却下' || v === 'rejected') return '却下';
        return '';
    }

    /**
     * ステータステキスト取得
     */
    getStatusText(status) {
        // 日英混在に対応
        const P = (CONSTANTS.STATUS_TYPES) || { PENDING: '未処理', PROCESSED: '処理済み' };
        if (status === P.PROCESSED || status === 'processed') return P.PROCESSED;
        if (status === P.PENDING || status === 'pending') return P.PENDING;
        if (status === 'rejected' || status === '却下') return '却下';
        return status;
    }

    /**
     * 経費削除
     */
    async deleteExpense(expenseId) {
        if (!confirm('この経費を削除してもよろしいですか？')) {
            return;
        }

        try {
            await this.services.expenseService.deleteExpense(expenseId);
            this.services.errorHandler.showToast('経費が削除されました', 'success');
            
            // 現在のページを再読み込み
            await this.initializePage();
            
        } catch (error) {
            console.error('❌ 経費削除エラー:', error);
            this.services.errorHandler.handle(error, '経費の削除中にエラーが発生しました');
        }
    }

    /**
     * カテゴリ選択肢設定
     */
    setupCategoryOptions() {
    const categorySelect = document.getElementById('type');
        if (categorySelect) {
            const categories = Array.isArray(CONSTANTS.EXPENSE_CATEGORIES)
                ? CONSTANTS.EXPENSE_CATEGORIES
                : Object.values(CONSTANTS.EXPENSE_CATEGORIES);
            categorySelect.innerHTML = categories.map(category => 
                `<option value="${category}">${category}</option>`
            ).join('');
        }
    }

    /**
     * テーブルソート設定
     */
    setupTableSorting() {
    let headers = document.querySelectorAll('.expense-table th');
    headers.forEach(h => h.classList.add('sortable'));
    headers.forEach((header, idx) => {
            // inline onclickがあるヘッダは既存ハンドラに任せて二重バインド回避
            if (header.getAttribute('onclick')) return;
            if (header.dataset.bound === 'true') return;
            header.addEventListener('click', () => {
                const column = header.dataset.column || this.getColumnKeyByIndex(idx);
                this.sortTable(column, idx);
            });
            header.dataset.bound = 'true';
        });
    }

    /**
     * テーブルソート実行
     */
    sortTable(column, columnIndex = null) {
        this.toggleSort(column, columnIndex);
    }

    // ソートヘッダーの見た目更新（列インデックス優先、なければキーで）
    updateSortHeaderStylesByIndex(index, asc, fallbackColumnKey = null) {
        const table = this.getActiveExpenseTableElement();
        if (!table) return;
        let headers = table.querySelectorAll('thead th');
        if (!headers || headers.length === 0) {
            headers = table.querySelectorAll('tr:first-child th');
        }
        // まず全て解除
        headers.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
        // 対象インデックス決定
        let targetIndex = index;
        if ((targetIndex === null || targetIndex === undefined) && fallbackColumnKey) {
            // data-columnが無い場合でもキー→固定順序で解決
            targetIndex = this.getColumnIndexByKey(fallbackColumnKey);
        }
        if (targetIndex !== null && targetIndex !== undefined && targetIndex >= 0 && targetIndex < headers.length) {
            headers[targetIndex].classList.add(asc ? 'sort-asc' : 'sort-desc');
        }
    }

    // ソート列のセルをハイライト（列インデックス優先、なければキーで）
    highlightSortedColumnByIndex(index, asc, fallbackColumnKey = null) {
        const table = this.getActiveExpenseTableElement();
        if (!table) return;
        // 既存のハイライトをクリア
        table.querySelectorAll('td.sorted-column-asc, td.sorted-column-desc')
            .forEach(td => td.classList.remove('sorted-column-asc', 'sorted-column-desc'));

        let targetIndex = index;
        if (targetIndex === null || targetIndex === undefined) {
            targetIndex = this.getColumnIndexByKey(fallbackColumnKey);
        }
        if (targetIndex === null || targetIndex === undefined || targetIndex < 0) return;

        const cls = asc ? 'sorted-column-asc' : 'sorted-column-desc';
        table.querySelectorAll('tbody tr').forEach(tr => {
            const tds = tr.querySelectorAll('td');
            if (tds[targetIndex]) tds[targetIndex].classList.add(cls);
        });
    }

    // 現在表示中ページのexpense-table要素を取得
    getActiveExpenseTableElement() {
        return (
            document.querySelector('#expense-list-page:not(.hidden) .expense-table') ||
            document.querySelector('.page:not(.hidden) .expense-table') ||
            document.querySelector('.expense-table')
        );
    }

    // ヘッダー列インデックスからデータキーへ変換（行レンダリング順に一致）
    getColumnKeyByIndex(index) {
        // 表示順に対応: タイトル, 種別, 金額, 備考, コード, ステータス, 登録日
        const keys = ['title', 'type', 'amount', 'remark', 'code', 'status', 'date'];
        return keys[index] || null;
    }

    // 列キーから固定表示順のインデックスを取得
    getColumnIndexByKey(key) {
        const keys = ['title', 'type', 'amount', 'remark', 'code', 'status', 'date'];
        return keys.indexOf(key);
    }

    /**
     * 設定値読み込み
     */
    loadUserSettings() {
        try {
            if (typeof this.services.storageService.getSettings !== 'function') return;
            const settings = this.services.storageService.getSettings();
            // 設定フォームに値を設定
            Object.entries(settings).forEach(([key, value]) => {
                const field = document.getElementById(key);
                if (field) {
                    field.value = value;
                }
            });
        } catch (e) {
            console.warn('設定読み込みをスキップ:', e);
        }
    }

    /**
     * 設定変更ハンドラー設定
     */
    setupSettingsHandlers() {
        const settingsForm = document.getElementById('settings-form');
        if (settingsForm) {
            settingsForm.addEventListener('submit', (event) => {
                event.preventDefault();
                this.saveSettings(new FormData(event.target));
            });
        }
    }

    /**
     * 設定保存
     */
    async saveSettings(formData) {
        try {
            if (typeof this.services.storageService.saveSettings !== 'function') {
                this.services.errorHandler.showToast('設定ストレージが未対応です', 'warning');
                return;
            }
            const settings = Object.fromEntries(formData.entries());
            await this.services.storageService.saveSettings(settings);
            this.services.errorHandler.showToast('設定が保存されました', 'success');
        } catch (error) {
            console.error('❌ 設定保存エラー:', error);
            this.services.errorHandler.handle(error, '設定の保存中にエラーが発生しました');
        }
    }

    /**
     * 完了コード表示
     */
    displayCompletionCodes() {
        if (typeof this.services.storageService.getCompletionCodes !== 'function') return;
        const completionCodes = this.services.storageService.getCompletionCodes();
        const container = document.getElementById('completion-codes-list');
        
        if (container) {
            if (completionCodes.length > 0) {
                container.innerHTML = completionCodes.map(code => `<span>${code}</span>`).join('');
            } else {
                container.textContent = 'コードは生成されませんでした。';
            }
        }
    }

    // 設定ページブリッジ: 全データエクスポート
    async exportAllData() {
        try {
            const data = await this.services.storageService.exportData();
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'expenses_export.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            this.services.errorHandler.showToast('エクスポートしました', 'success');
        } catch (error) {
            console.error('❌ エクスポートエラー:', error);
            this.services.errorHandler.handle(error, 'エクスポート中にエラーが発生しました');
        }
    }

    // 設定ページブリッジ: インポート
    async importData(event) {
        try {
            const file = event?.target?.files?.[0];
            if (!file) return;
            const text = await file.text();
            const json = JSON.parse(text);
            await this.services.storageService.importData(json);
            this.services.errorHandler.showToast('インポートしました', 'success');
            // 画面を更新
            await this.initializePage();
        } catch (error) {
            console.error('❌ インポートエラー:', error);
            this.services.errorHandler.handle(error, 'インポート中にエラーが発生しました');
        }
    }

    // 設定ページブリッジ: 全削除
    async confirmDeleteAllData() {
        if (!confirm('全データを削除します。よろしいですか？')) return;
        try {
            await this.services.expenseService.clearAllExpenses();
            this.services.errorHandler.showToast('全データを削除しました', 'success');
            await this.initializePage();
        } catch (error) {
            console.error('❌ 全削除エラー:', error);
            this.services.errorHandler.handle(error, '全削除中にエラーが発生しました');
        }
    }

    /**
     * 経費レポート読み込み
     */
    async loadExpenseReport() {
        try {
            const expenses = await this.services.expenseService.getAllExpenses();
            
            // 仮想スクロール用にデータ設定
            if (this.virtualScrollManager) {
                this.virtualScrollManager.setData(expenses);
            } else {
                // 通常のテーブル表示
                this.renderExpenseTable(expenses);
            }
            
        } catch (error) {
            console.error('❌ 経費レポート読み込みエラー:', error);
            this.services.errorHandler.handle(error, '経費レポートの読み込み中にエラーが発生しました');
        }
    }

    /**
     * 経費テーブル描画
     */
    renderExpenseTable(expenses) {
        const tbody = document.getElementById('expense-list-body')
            || document.querySelector('#expense-list-page .expense-table tbody')
            || document.querySelector('.page:not(.hidden) .expense-table tbody')
            || document.querySelector('.expense-table tbody');
        if (!tbody) return;

        if (!expenses || expenses.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;">登録された経費はありません</td></tr>';
            return;
        }

        tbody.innerHTML = expenses.map((expense, index) => this.renderExpenseTableRow(expense, index)).join('');
    }

    /**
     * パフォーマンス測定開始
     */
    startPerformanceMeasure(name) {
        performance.mark(`${name}-start`);
    }

    /**
     * パフォーマンス測定終了
     */
    endPerformanceMeasure(name) {
        performance.mark(`${name}-end`);
        performance.measure(name, `${name}-start`, `${name}-end`);
    }

    /**
     * アプリケーション破棄
     */
    destroy() {
        // イベントリスナー削除
        window.removeEventListener('resize', this.handleWindowResize);
        
        // 仮想スクロール破棄
        if (this.virtualScrollManager) {
            this.virtualScrollManager.destroy();
        }
        
        // キャッシュクリア
        this.clearDataCache();
        
        console.log('🗑️ ExpenseApp破棄完了');
    }
}


// グローバルアプリケーションインスタンス
window.appController = new ExpenseApp();

// DOMContentLoaded時に初期化
document.addEventListener('DOMContentLoaded', async () => {
    await window.appController.initialize();
});

// アンロード時にクリーンアップ
window.addEventListener('beforeunload', () => {
    window.appController.destroy();
});


