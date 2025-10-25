/**
 * 経費管理のビジネスロジックサービス
 * 開発ガイドライン準拠: 関心の分離とSOLID原則
 */

import { ValidationService, ValidationError } from './ValidationService.js';
import { StorageService, StorageError } from './StorageService.js';
import { ErrorHandler } from '../utils/ErrorHandler.js';
import { STATUS_TYPES, EXPENSE_CATEGORIES } from '../utils/Constants.js';

export class ExpenseServiceError extends Error {
    constructor(message, operation = null) {
        super(message);
        this.name = 'ExpenseServiceError';
        this.operation = operation;
    }
}

export class ExpenseService {
    constructor() {
        this.validationService = new ValidationService();
        this.storageService = new StorageService();
        this.codeCounter = 0;
        this.initializeCodeCounter();
    }

    /**
     * コードカウンターの初期化
     */
    async initializeCodeCounter() {
        try {
            this.codeCounter = await this.storageService.loadCodeNumber();
        } catch (error) {
            console.warn('Failed to load code counter:', error);
            this.codeCounter = 0;
        }
    }

    /**
     * 経費を追加
     * @param {Object} expenseData - 経費データ
     * @returns {Promise<Object>} 追加された経費データ
     */
    async addExpense(expenseData) {
        try {
            // 入力値のサニタイゼーション
            const sanitizedData = this.sanitizeExpenseData(expenseData);
            
            // バリデーション
            const validationResult = this.validationService.validateExpense(sanitizedData);
            if (!validationResult.isValid) {
                throw new ValidationError(validationResult.message);
            }

            // CSV等でコードが指定された場合はカウンタを追従（将来の生成重複を防止）
            if (sanitizedData.code) {
                const n = parseInt(String(sanitizedData.code), 10);
                if (!Number.isNaN(n)) {
                    this.codeCounter = Math.max(this.codeCounter, n);
                }
            }

            // 経費データの拡張
            const enrichedExpense = this.enrichExpenseData(sanitizedData);
            
            // データ保存
            const savedExpense = await this.storageService.addExpense(enrichedExpense);
            
            // コードカウンターの更新
            await this.updateCodeCounter();
            
            // 成功通知はコントローラ側で行う（UIの一元管理）
            
            return savedExpense;
        } catch (error) {
            if (error instanceof ValidationError) {
                throw error; // バリデーションエラーはそのまま再スロー
            }
            
            ErrorHandler.handle(error, 'ExpenseService.addExpense');
            throw new ExpenseServiceError(`経費の追加に失敗しました: ${error.message}`, 'add');
        }
    }

    /**
     * 複数の経費を一括追加
     * @param {Array} expenseDataList - 経費データのリスト
     * @returns {Promise<Array>} 追加された経費データのリスト
     */
    async addMultipleExpenses(expenseDataList) {
        const results = [];
        const errors = [];

        for (let i = 0; i < expenseDataList.length; i++) {
            try {
                const result = await this.addExpense(expenseDataList[i]);
                results.push({
                    index: i + 1,
                    success: true,
                    data: result
                });
            } catch (error) {
                errors.push({
                    index: i + 1,
                    success: false,
                    error: error.message,
                    data: expenseDataList[i]
                });
            }
        }

    // 結果の通知はコントローラ側で行う

        return { results, errors };
    }

    /**
     * 経費一覧を取得
     * @param {Object} filters - フィルター条件
     * @returns {Promise<Array>} 経費データリスト
     */
    async getExpenses(filters = {}) {
        try {
            const expenses = await this.storageService.loadExpenseData();
            return this.applyFilters(expenses, filters);
        } catch (error) {
            ErrorHandler.handle(error, 'ExpenseService.getExpenses');
            throw new ExpenseServiceError('経費データの取得に失敗しました', 'get');
        }
    }

    // ...recent-expenses feature removed per project request...

    /**
     * 全経費データを取得（ソートなしの生データ）
     * @returns {Promise<Array>} 経費一覧
     */
    async getAllExpenses() {
        return this.getExpenses();
    }

    /**
     * 経費を更新
     * @param {string} id - 経費ID
     * @param {Object} updates - 更新データ
     * @returns {Promise<Object>} 更新された経費データ
     */
    async updateExpense(id, updates) {
        try {
            // 更新データのサニタイゼーション
            const sanitizedUpdates = this.sanitizeExpenseData(updates);
            
            // 部分的なバリデーション
            if (updates.title !== undefined) {
                const titleValidation = this.validationService.validateTitle(updates.title);
                if (!titleValidation.isValid) {
                    throw new ValidationError(titleValidation.message);
                }
            }

            if (updates.amount !== undefined) {
                const amountValidation = this.validationService.validateAmount(updates.amount);
                if (!amountValidation.isValid) {
                    throw new ValidationError(amountValidation.message);
                }
            }

            const updatedExpense = await this.storageService.updateExpense(id, sanitizedUpdates);
            
            // 更新成功の通知はコントローラ側で行う
            return updatedExpense;
        } catch (error) {
            if (error instanceof ValidationError) {
                throw error;
            }
            
            ErrorHandler.handle(error, 'ExpenseService.updateExpense');
            throw new ExpenseServiceError(`経費の更新に失敗しました: ${error.message}`, 'update');
        }
    }

    /**
     * 経費を削除
     * @param {string} id - 経費ID
     * @returns {Promise<boolean>} 削除結果
     */
    async deleteExpense(id) {
        try {
            const result = await this.storageService.deleteExpense(id);
            // 削除成功の通知はコントローラ側で行う
            return result;
        } catch (error) {
            ErrorHandler.handle(error, 'ExpenseService.deleteExpense');
            throw new ExpenseServiceError(`経費の削除に失敗しました: ${error.message}`, 'delete');
        }
    }

    /**
     * 経費のステータスを更新
     * @param {string} id - 経費ID
     * @param {string} status - 新しいステータス
     * @returns {Promise<Object>} 更新された経費データ
     */
    async updateExpenseStatus(id, status) {
        if (!Object.values(STATUS_TYPES).includes(status)) {
            throw new ValidationError('無効なステータスです');
        }

        return this.updateExpense(id, { status });
    }

    /**
     * 全経費データを削除
     * @returns {Promise<boolean>} 削除結果
     */
    async clearAllExpenses() {
        try {
            const result = await this.storageService.clearAllData();
            this.codeCounter = 0;
            // 全削除成功の通知はコントローラ側で行う
            return result;
        } catch (error) {
            ErrorHandler.handle(error, 'ExpenseService.clearAllExpenses');
            throw new ExpenseServiceError('データの削除に失敗しました', 'clear');
        }
    }

    /**
     * 統計情報を取得
     * @returns {Promise<Object>} 統計情報
     */
    async getStatistics() {
        try {
            const expenses = await this.getExpenses();
            
            return {
                totalCount: expenses.length,
                totalAmount: expenses.reduce((sum, expense) => sum + expense.amount, 0),
                processedCount: expenses.filter(expense => expense.status === STATUS_TYPES.PROCESSED).length,
                pendingCount: expenses.filter(expense => expense.status === STATUS_TYPES.PENDING).length,
                categoryBreakdown: this.calculateCategoryBreakdown(expenses),
                monthlyBreakdown: this.calculateMonthlyBreakdown(expenses)
            };
        } catch (error) {
            ErrorHandler.handle(error, 'ExpenseService.getStatistics');
            throw new ExpenseServiceError('統計情報の取得に失敗しました', 'statistics');
        }
    }

    /**
     * データのエクスポート
     * @returns {Promise<Object>} エクスポートデータ
     */
    async exportData() {
        try {
            return await this.storageService.exportData();
        } catch (error) {
            ErrorHandler.handle(error, 'ExpenseService.exportData');
            throw new ExpenseServiceError('データのエクスポートに失敗しました', 'export');
        }
    }

    /**
     * データのインポート
     * @param {Object} importData - インポートデータ
     * @returns {Promise<boolean>} インポート結果
     */
    async importData(importData) {
        try {
            const result = await this.storageService.importData(importData);
            await this.initializeCodeCounter(); // コードカウンターを再初期化
            // インポート成功の通知はコントローラ側で行う
            return result;
        } catch (error) {
            ErrorHandler.handle(error, 'ExpenseService.importData');
            throw new ExpenseServiceError('データのインポートに失敗しました', 'import');
        }
    }

    /**
     * 経費データのサニタイゼーション
     * @param {Object} expenseData - 経費データ
     * @returns {Object} サニタイズされた経費データ
     */
    sanitizeExpenseData(expenseData) {
        const sanitized = {};
        
        if (expenseData.title !== undefined) {
            sanitized.title = this.validationService.sanitizeInput(expenseData.title);
        }
        
        if (expenseData.type !== undefined) {
            sanitized.type = this.validationService.sanitizeInput(expenseData.type);
        }
        
        if (expenseData.amount !== undefined) {
            sanitized.amount = Number(expenseData.amount);
        }
        
        if (expenseData.remark !== undefined) {
            sanitized.remark = this.validationService.sanitizeInput(expenseData.remark);
        }
        
        if (expenseData.date !== undefined) {
            sanitized.date = expenseData.date;
        }
        
        if (expenseData.status !== undefined) {
            sanitized.status = expenseData.status;
        }

        if (expenseData.code !== undefined) {
            sanitized.code = String(expenseData.code).trim();
        }

        return sanitized;
    }

    /**
     * 経費データの拡張
     * @param {Object} expenseData - 経費データ
     * @returns {Object} 拡張された経費データ
     */
    enrichExpenseData(expenseData) {
        return {
            ...expenseData,
            code: expenseData.code ? String(expenseData.code) : this.generateCode(),
            status: expenseData.status || STATUS_TYPES.PENDING,
            date: expenseData.date || new Date().toLocaleDateString('ja-JP')
        };
    }

    /**
     * コードの生成
     * @returns {string} 生成されたコード
     */
    generateCode() {
        this.codeCounter++;
        return this.codeCounter.toString().padStart(6, '0');
    }

    /**
     * コードカウンターの更新
     */
    async updateCodeCounter() {
        try {
            await this.storageService.saveCodeNumber(this.codeCounter);
        } catch (error) {
            console.warn('Failed to save code counter:', error);
        }
    }

    /**
     * フィルターの適用
     * @param {Array} expenses - 経費データリスト
     * @param {Object} filters - フィルター条件
     * @returns {Array} フィルタリングされた経費データリスト
     */
    applyFilters(expenses, filters) {
        let filtered = [...expenses];

        if (filters.status) {
            filtered = filtered.filter(expense => expense.status === filters.status);
        }

        if (filters.category) {
            filtered = filtered.filter(expense => expense.type === filters.category);
        }

        if (filters.dateFrom) {
            filtered = filtered.filter(expense => new Date(expense.date) >= new Date(filters.dateFrom));
        }

        if (filters.dateTo) {
            filtered = filtered.filter(expense => new Date(expense.date) <= new Date(filters.dateTo));
        }

        if (filters.amountMin !== undefined) {
            filtered = filtered.filter(expense => expense.amount >= filters.amountMin);
        }

        if (filters.amountMax !== undefined) {
            filtered = filtered.filter(expense => expense.amount <= filters.amountMax);
        }

        if (filters.keyword) {
            const keyword = filters.keyword.toLowerCase();
            filtered = filtered.filter(expense => 
                expense.title.toLowerCase().includes(keyword) ||
                (expense.remark && expense.remark.toLowerCase().includes(keyword))
            );
        }

        return filtered;
    }

    /**
     * カテゴリ別集計の計算
     * @param {Array} expenses - 経費データリスト
     * @returns {Object} カテゴリ別集計
     */
    calculateCategoryBreakdown(expenses) {
        const breakdown = {};
        
        Object.values(EXPENSE_CATEGORIES).forEach(category => {
            breakdown[category] = {
                count: 0,
                amount: 0
            };
        });

        expenses.forEach(expense => {
            if (breakdown[expense.type]) {
                breakdown[expense.type].count++;
                breakdown[expense.type].amount += expense.amount;
            }
        });

        return breakdown;
    }

    /**
     * 月別集計の計算
     * @param {Array} expenses - 経費データリスト
     * @returns {Object} 月別集計
     */
    calculateMonthlyBreakdown(expenses) {
        const breakdown = {};

        expenses.forEach(expense => {
            const date = new Date(expense.date);
            const monthKey = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`;
            
            if (!breakdown[monthKey]) {
                breakdown[monthKey] = {
                    count: 0,
                    amount: 0
                };
            }
            
            breakdown[monthKey].count++;
            breakdown[monthKey].amount += expense.amount;
        });

        return breakdown;
    }
}
