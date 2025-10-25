/**
 * 統一的なエラーハンドリングシステム
 * 開発ガイドライン準拠: エラー処理の標準化
 */

export class ApplicationError extends Error {
    constructor(message, code = null, context = {}) {
        super(message);
        this.name = 'ApplicationError';
        this.code = code;
        this.context = context;
        this.timestamp = new Date().toISOString();
    }
}

export class ErrorHandler {
    static instance = null;
    static toastContainer = null;

    constructor() {
        if (ErrorHandler.instance) {
            return ErrorHandler.instance;
        }
        
        this.errorLog = [];
        this.maxLogSize = 100;
        this.setupToastContainer();
        
        ErrorHandler.instance = this;
    }

    /**
     * エラーハンドリングのメインメソッド
     * @param {Error} error - エラーオブジェクト
     * @param {string} context - エラーが発生したコンテキスト
     * @param {boolean} showToUser - ユーザーに通知するか
     */
    static handle(error, context = '', showToUser = true) {
        const handler = new ErrorHandler();
        handler.processError(error, context, showToUser);
    }

    // インスタンス経由でも呼べるようにする（後方互換）
    handle(error, context = '', showToUser = true) {
        this.processError(error, context, showToUser);
    }

    /**
     * エラーの処理
     * @param {Error} error - エラーオブジェクト
     * @param {string} context - コンテキスト
     * @param {boolean} showToUser - ユーザー通知フラグ
     */
    processError(error, context, showToUser) {
        const errorInfo = this.createErrorInfo(error, context);
        
        // ログに記録
        this.logError(errorInfo);
        
        // コンソールに出力
        this.outputToConsole(errorInfo);
        
        // ユーザーに通知
        if (showToUser) {
            this.showUserNotification(error);
        }
        
        // 監視システムに送信（本番環境）
        if (this.isProduction()) {
            this.sendToMonitoring(errorInfo);
        }
    }

    /**
     * エラー情報オブジェクトの作成
     * @param {Error} error - エラーオブジェクト
     * @param {string} context - コンテキスト
     * @returns {Object} エラー情報
     */
    createErrorInfo(error, context) {
        return {
            message: error.message,
            name: error.name,
            stack: error.stack,
            context: context,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            url: window.location.href,
            userId: this.getCurrentUserId() // 将来的にユーザー管理機能追加時
        };
    }

    /**
     * エラーログに記録
     * @param {Object} errorInfo - エラー情報
     */
    logError(errorInfo) {
        this.errorLog.push(errorInfo);
        
        // ログサイズ制限
        if (this.errorLog.length > this.maxLogSize) {
            this.errorLog = this.errorLog.slice(-this.maxLogSize);
        }
        
        // ローカルストレージにも保存（デバッグ用）
        try {
            localStorage.setItem('errorLog', JSON.stringify(this.errorLog));
        } catch (e) {
            console.warn('Failed to save error log to localStorage');
        }
    }

    /**
     * コンソールに出力
     * @param {Object} errorInfo - エラー情報
     */
    outputToConsole(errorInfo) {
        console.group(`🚨 Error in ${errorInfo.context || 'Unknown Context'}`);
        console.error('Message:', errorInfo.message);
        console.error('Type:', errorInfo.name);
        console.error('Timestamp:', errorInfo.timestamp);
        console.error('Stack:', errorInfo.stack);
        console.groupEnd();
    }

    /**
     * ユーザーに通知
     * @param {Error} error - エラーオブジェクト
     */
    showUserNotification(error) {
        let userMessage = this.getUserFriendlyMessage(error);
        let type = this.getNotificationType(error);
        
        this.showToast(userMessage, type);
    }

    /**
     * ユーザー向けメッセージの取得
     * @param {Error} error - エラーオブジェクト
     * @returns {string} ユーザー向けメッセージ
     */
    getUserFriendlyMessage(error) {
        // カスタムエラーの場合、メッセージをそのまま使用
        if (error.name === 'ValidationError') {
            return error.message;
        }
        
        if (error.name === 'StorageError') {
            return 'データの処理中にエラーが発生しました。しばらく待ってから再試行してください。';
        }
        
        if (error.name === 'NetworkError') {
            return 'ネットワークエラーが発生しました。接続状況を確認してください。';
        }
        
        // デフォルトメッセージ
        return 'システムエラーが発生しました。管理者にお問い合わせください。';
    }

    /**
     * 通知タイプの取得
     * @param {Error} error - エラーオブジェクト
     * @returns {string} 通知タイプ
     */
    getNotificationType(error) {
        if (error.name === 'ValidationError') {
            return 'warning';
        }
        
        if (error.name === 'StorageError' || error.name === 'NetworkError') {
            return 'error';
        }
        
        return 'error';
    }

    /**
     * Toast通知の表示
     * @param {string} message - メッセージ
     * @param {string} type - 通知タイプ (success, info, warning, error)
     * @param {number} duration - 表示時間（ミリ秒）
     */
    showToast(message, type = 'info', duration = 2000) {
        const toast = this.createToastElement(message, type);
        
        ErrorHandler.toastContainer.appendChild(toast);
        
        // アニメーション用のクラスを追加
        setTimeout(() => toast.classList.add('toast--show'), 100);
        
        // 自動削除
        setTimeout(() => {
            toast.classList.remove('toast--show');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, duration);
        
        // クリックで即座に削除
        toast.addEventListener('click', () => {
            toast.classList.remove('toast--show');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        });
    }

    /**
     * Toast要素の作成
     * @param {string} message - メッセージ
     * @param {string} type - タイプ
     * @returns {HTMLElement} Toast要素
     */
    createToastElement(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast toast--${type}`;
        
        const icon = this.getToastIcon(type);
        toast.innerHTML = `
            <div class="toast__icon">${icon}</div>
            <div class="toast__message">${message}</div>
            <div class="toast__close">×</div>
        `;
        
        return toast;
    }

    /**
     * Toastアイコンの取得
     * @param {string} type - タイプ
     * @returns {string} アイコン
     */
    getToastIcon(type) {
        const icons = {
            success: '✓',
            info: 'ℹ',
            warning: '⚠',
            error: '✗'
        };
        
        return icons[type] || icons.info;
    }

    /**
     * Toastコンテナの設定
     */
    setupToastContainer() {
        if (!ErrorHandler.toastContainer) {
            ErrorHandler.toastContainer = document.createElement('div');
            ErrorHandler.toastContainer.className = 'toast-container';
            document.body.appendChild(ErrorHandler.toastContainer);
            
            // CSSスタイルの追加
            this.addToastStyles();
        }
    }

    /**
     * Toastスタイルの追加
     */
    addToastStyles() {
        if (document.getElementById('toast-styles')) {
            return; // 既に追加済み
        }

        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.textContent = `
            .toast-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                pointer-events: none;
            }
            
            .toast {
                display: flex;
                align-items: center;
                margin-bottom: 10px;
                padding: 12px 16px;
                background: var(--card-bg, #2a2a4a);
                border: 2px solid var(--card-border, #4a4a6a);
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                color: var(--text-color, #e0e0e0);
                min-width: 300px;
                max-width: 500px;
                opacity: 0;
                transform: translateX(100%);
                transition: all 0.3s ease-in-out;
                pointer-events: all;
                cursor: pointer;
            }
            
            .toast--show {
                opacity: 1;
                transform: translateX(0);
            }
            
            .toast--success {
                border-color: var(--success-color, #28a745);
            }
            
            .toast--warning {
                border-color: #ffc107;
            }
            
            .toast--error {
                border-color: var(--danger-color, #dc3545);
            }
            
            .toast--info {
                border-color: var(--highlight-color, #00f0ff);
            }
            
            .toast__icon {
                margin-right: 12px;
                font-size: 1.2rem;
                font-weight: bold;
            }
            
            .toast--success .toast__icon {
                color: var(--success-color, #28a745);
            }
            
            .toast--warning .toast__icon {
                color: #ffc107;
            }
            
            .toast--error .toast__icon {
                color: var(--danger-color, #dc3545);
            }
            
            .toast--info .toast__icon {
                color: var(--highlight-color, #00f0ff);
            }
            
            .toast__message {
                flex: 1;
                font-size: 0.9rem;
                line-height: 1.4;
            }
            
            .toast__close {
                margin-left: 12px;
                font-size: 1.2rem;
                opacity: 0.7;
                transition: opacity 0.2s;
            }
            
            .toast__close:hover {
                opacity: 1;
            }
        `;
        
        document.head.appendChild(style);
    }

    /**
     * 成功メッセージの表示
     * @param {string} message - メッセージ
     */
    static showSuccess(message) {
        const handler = new ErrorHandler();
        handler.showToast(message, 'success');
    }

    /**
     * 情報メッセージの表示
     * @param {string} message - メッセージ
     */
    static showInfo(message) {
        const handler = new ErrorHandler();
        handler.showToast(message, 'info');
    }

    /**
     * 警告メッセージの表示
     * @param {string} message - メッセージ
     */
    static showWarning(message) {
        const handler = new ErrorHandler();
        handler.showToast(message, 'warning');
    }

    /**
     * エラーメッセージの表示
     * @param {string} message - メッセージ
     */
    static showError(message) {
        const handler = new ErrorHandler();
        handler.showToast(message, 'error');
    }

    /**
     * 監視システムへの送信
     * @param {Object} errorInfo - エラー情報
     */
    sendToMonitoring(errorInfo) {
        // 実際の監視システム（Sentry、Datadog等）への送信処理
        // 現在はコンソールログのみ
        console.log('Sending to monitoring system:', errorInfo);
    }

    /**
     * 本番環境かどうかの判定
     * @returns {boolean} 本番環境かどうか
     */
    isProduction() {
        return window.location.hostname !== 'localhost' && 
               window.location.hostname !== '127.0.0.1';
    }

    /**
     * 現在のユーザーIDを取得（将来的な機能）
     * @returns {string|null} ユーザーID
     */
    getCurrentUserId() {
        // 将来的にユーザー管理機能を追加する際に実装
        return null;
    }

    /**
     * エラーログの取得
     * @returns {Array} エラーログ
     */
    getErrorLog() {
        return [...this.errorLog];
    }

    /**
     * エラーログのクリア
     */
    clearErrorLog() {
        this.errorLog = [];
        try {
            localStorage.removeItem('errorLog');
        } catch (e) {
            console.warn('Failed to clear error log from localStorage');
        }
    }
}
