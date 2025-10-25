/**
 * 入力値検証サービス
 * 開発ガイドライン準拠: バリデーション処理の統一化
 */

import { VALIDATION_RULES, ERROR_MESSAGES } from '../utils/Constants.js';

export class ValidationError extends Error {
    constructor(message, field = null) {
        super(message);
        this.name = 'ValidationError';
        this.field = field;
    }
}

export class ValidationService {
    /**
     * 経費データの包括的バリデーション
     * @param {Object} expenseData - 検証する経費データ
     * @returns {Object} 検証結果
     */
    validateExpense(expenseData) {
        const errors = [];

        // タイトル検証
        const titleResult = this.validateTitle(expenseData.title);
        if (!titleResult.isValid) {
            errors.push({ field: 'title', message: titleResult.message });
        }

        // カテゴリ検証
        const categoryResult = this.validateCategory(expenseData.type);
        if (!categoryResult.isValid) {
            errors.push({ field: 'type', message: categoryResult.message });
        }

        // 金額検証
        const amountResult = this.validateAmount(expenseData.amount);
        if (!amountResult.isValid) {
            errors.push({ field: 'amount', message: amountResult.message });
        }

        // 備考検証（オプション）
        if (expenseData.remark) {
            const remarkResult = this.validateRemark(expenseData.remark);
            if (!remarkResult.isValid) {
                errors.push({ field: 'remark', message: remarkResult.message });
            }
        }

        return {
            isValid: errors.length === 0,
            errors: errors,
            message: errors.map(error => error.message).join(', ')
        };
    }

    /**
     * タイトルのバリデーション
     * @param {string} title - タイトル
     * @returns {Object} 検証結果
     */
    validateTitle(title) {
        if (!title || typeof title !== 'string') {
            return {
                isValid: false,
                message: ERROR_MESSAGES.VALIDATION.TITLE_REQUIRED
            };
        }

        const trimmedTitle = title.trim();
        
        if (trimmedTitle.length < VALIDATION_RULES.TITLE.MIN_LENGTH) {
            return {
                isValid: false,
                message: ERROR_MESSAGES.VALIDATION.TITLE_REQUIRED
            };
        }

        if (trimmedTitle.length > VALIDATION_RULES.TITLE.MAX_LENGTH) {
            return {
                isValid: false,
                message: ERROR_MESSAGES.VALIDATION.TITLE_TOO_LONG
            };
        }

        // セキュリティ: XSS対策の基本チェック
        if (this.containsSuspiciousContent(trimmedTitle)) {
            return {
                isValid: false,
                message: '不正な文字が含まれています'
            };
        }

        return { isValid: true, message: '' };
    }

    /**
     * カテゴリのバリデーション
     * @param {string} category - カテゴリ
     * @returns {Object} 検証結果
     */
    validateCategory(category) {
        if (!category || typeof category !== 'string') {
            return {
                isValid: false,
                message: ERROR_MESSAGES.VALIDATION.CATEGORY_REQUIRED
            };
        }

        return { isValid: true, message: '' };
    }

    /**
     * 金額のバリデーション
     * @param {number|string} amount - 金額
     * @returns {Object} 検証結果
     */
    validateAmount(amount) {
        const numAmount = Number(amount);
        
        if (isNaN(numAmount)) {
            return {
                isValid: false,
                message: ERROR_MESSAGES.VALIDATION.AMOUNT_INVALID
            };
        }

        if (numAmount < VALIDATION_RULES.AMOUNT.MIN_VALUE || 
            numAmount > VALIDATION_RULES.AMOUNT.MAX_VALUE) {
            return {
                isValid: false,
                message: ERROR_MESSAGES.VALIDATION.AMOUNT_INVALID
            };
        }

        return { isValid: true, message: '' };
    }

    /**
     * 備考のバリデーション
     * @param {string} remark - 備考
     * @returns {Object} 検証結果
     */
    validateRemark(remark) {
        if (typeof remark !== 'string') {
            return { isValid: false, message: '備考は文字列で入力してください' };
        }

        if (remark.length > VALIDATION_RULES.REMARK.MAX_LENGTH) {
            return {
                isValid: false,
                message: `備考は${VALIDATION_RULES.REMARK.MAX_LENGTH}文字以下で入力してください`
            };
        }

        if (this.containsSuspiciousContent(remark)) {
            return {
                isValid: false,
                message: '不正な文字が含まれています'
            };
        }

        return { isValid: true, message: '' };
    }

    /**
     * ファイルのバリデーション
     * @param {File} file - ファイル
     * @returns {Object} 検証結果
     */
    validateFile(file) {
        if (!file) {
            return { isValid: false, message: 'ファイルが選択されていません' };
        }

        // ファイルサイズチェック
        const maxSizeBytes = 5 * 1024 * 1024; // 5MB
        if (file.size > maxSizeBytes) {
            return {
                isValid: false,
                message: ERROR_MESSAGES.FILE.SIZE_TOO_LARGE
            };
        }

        // ファイル形式チェック
        const allowedTypes = ['text/csv', 'application/vnd.ms-excel'];
        if (!allowedTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.csv')) {
            return {
                isValid: false,
                message: ERROR_MESSAGES.FILE.INVALID_FORMAT
            };
        }

        return { isValid: true, message: '' };
    }

    /**
     * 入力値のサニタイゼーション
     * @param {string} input - 入力値
     * @returns {string} サニタイズされた値
     */
    sanitizeInput(input) {
        if (typeof input !== 'string') {
            return input;
        }

        return input
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#x27;')
            .replace(/\//g, '&#x2F;')
            .trim();
    }

    /**
     * 不審なコンテンツの検出
     * @param {string} content - コンテンツ
     * @returns {boolean} 不審なコンテンツが含まれているか
     */
    containsSuspiciousContent(content) {
        const suspiciousPatterns = [
            /<script/i,
            /javascript:/i,
            /on\w+\s*=/i,
            /<iframe/i,
            /<object/i,
            /<embed/i
        ];

        return suspiciousPatterns.some(pattern => pattern.test(content));
    }
}
