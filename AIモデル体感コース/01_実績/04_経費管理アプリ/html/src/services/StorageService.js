/**
 * データストレージサービス
 * 開発ガイドライン準拠: データアクセスの抽象化
 */

import { LOCAL_STORAGE_KEYS, ERROR_MESSAGES } from '../utils/Constants.js';

export class StorageError extends Error {
    constructor(message, operation = null) {
        super(message);
        this.name = 'StorageError';
        this.operation = operation;
    }
}

export class StorageService {
    constructor() {
        this.isAvailable = this.checkAvailability();
    }

    /**
     * ローカルストレージの利用可能性をチェック
     * @returns {boolean} 利用可能かどうか
     */
    checkAvailability() {
        try {
            const testKey = '__test_storage__';
            localStorage.setItem(testKey, 'test');
            localStorage.removeItem(testKey);
            return true;
        } catch (error) {
            console.warn('LocalStorage is not available:', error);
            return false;
        }
    }

    /**
     * 経費データを保存
     * @param {Array} expenseData - 経費データ配列
     * @returns {Promise<boolean>} 保存結果
     */
    async saveExpenseData(expenseData) {
        if (!this.isAvailable) {
            throw new StorageError(ERROR_MESSAGES.STORAGE.SAVE_FAILED, 'save');
        }

        try {
            const dataToSave = {
                data: expenseData,
                timestamp: new Date().toISOString(),
                version: '1.0'
            };

            localStorage.setItem(LOCAL_STORAGE_KEYS.EXPENSE_DATA, JSON.stringify(dataToSave));
            
            // バックアップも作成
            this.createBackup(dataToSave);
            
            return true;
        } catch (error) {
            console.error('Failed to save expense data:', error);
            throw new StorageError(ERROR_MESSAGES.STORAGE.SAVE_FAILED, 'save');
        }
    }

    /**
     * 経費データを読み込み
     * @returns {Promise<Array>} 経費データ配列
     */
    async loadExpenseData() {
        if (!this.isAvailable) {
            console.warn('LocalStorage not available, returning empty array');
            return [];
        }

        try {
            const savedData = localStorage.getItem(LOCAL_STORAGE_KEYS.EXPENSE_DATA);
            
            if (!savedData) {
                return [];
            }

            const parsedData = JSON.parse(savedData);
            
            // データ構造の検証
            if (this.validateDataStructure(parsedData)) {
                return parsedData.data || [];
            } else {
                console.warn('Invalid data structure, attempting backup recovery');
                return this.attemptBackupRecovery();
            }
        } catch (error) {
            console.error('Failed to load expense data:', error);
            return this.attemptBackupRecovery();
        }
    }

    /**
     * 単一経費データを追加
     * @param {Object} expense - 経費データ
     * @returns {Promise<Object>} 保存された経費データ
     */
    async addExpense(expense) {
        try {
            const currentData = await this.loadExpenseData();
            const newExpense = {
                ...expense,
                id: this.generateId(),
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            };

            currentData.push(newExpense);
            await this.saveExpenseData(currentData);
            
            return newExpense;
        } catch (error) {
            throw new StorageError(`経費の追加に失敗しました: ${error.message}`, 'add');
        }
    }

    /**
     * 経費データを更新
     * @param {string} id - 経費ID
     * @param {Object} updates - 更新データ
     * @returns {Promise<Object>} 更新された経費データ
     */
    async updateExpense(id, updates) {
        try {
            const currentData = await this.loadExpenseData();
            const expenseIndex = currentData.findIndex(expense => expense.id === id);
            
            if (expenseIndex === -1) {
                throw new Error('指定された経費が見つかりません');
            }

            currentData[expenseIndex] = {
                ...currentData[expenseIndex],
                ...updates,
                updatedAt: new Date().toISOString()
            };

            await this.saveExpenseData(currentData);
            return currentData[expenseIndex];
        } catch (error) {
            throw new StorageError(`経費の更新に失敗しました: ${error.message}`, 'update');
        }
    }

    /**
     * 経費データを削除
     * @param {string} id - 経費ID
     * @returns {Promise<boolean>} 削除結果
     */
    async deleteExpense(id) {
        try {
            const currentData = await this.loadExpenseData();
            const filteredData = currentData.filter(expense => expense.id !== id);
            
            if (filteredData.length === currentData.length) {
                throw new Error('指定された経費が見つかりません');
            }

            await this.saveExpenseData(filteredData);
            return true;
        } catch (error) {
            throw new StorageError(`経費の削除に失敗しました: ${error.message}`, 'delete');
        }
    }

    /**
     * コード番号を保存
     * @param {number} codeNumber - コード番号
     * @returns {Promise<boolean>} 保存結果
     */
    async saveCodeNumber(codeNumber) {
        if (!this.isAvailable) {
            return false;
        }

        try {
            localStorage.setItem(LOCAL_STORAGE_KEYS.LAST_CODE_NUMBER, codeNumber.toString());
            return true;
        } catch (error) {
            console.error('Failed to save code number:', error);
            return false;
        }
    }

    /**
     * コード番号を読み込み
     * @returns {Promise<number>} コード番号
     */
    async loadCodeNumber() {
        if (!this.isAvailable) {
            return 0;
        }

        try {
            const savedCode = localStorage.getItem(LOCAL_STORAGE_KEYS.LAST_CODE_NUMBER);
            return savedCode ? parseInt(savedCode, 10) : 0;
        } catch (error) {
            console.error('Failed to load code number:', error);
            return 0;
        }
    }

    /**
     * 全データを削除
     * @returns {Promise<boolean>} 削除結果
     */
    async clearAllData() {
        if (!this.isAvailable) {
            return false;
        }

        try {
            localStorage.removeItem(LOCAL_STORAGE_KEYS.EXPENSE_DATA);
            localStorage.removeItem(LOCAL_STORAGE_KEYS.LAST_CODE_NUMBER);
            localStorage.removeItem(LOCAL_STORAGE_KEYS.COMPLETION_CODES);
            return true;
        } catch (error) {
            console.error('Failed to clear data:', error);
            return false;
        }
    }

    /**
     * 完了コードを保存（配列）
     * @param {string[]} codes
     */
    saveCompletionCodes(codes = []) {
        if (!this.isAvailable) return false;
        try {
            localStorage.setItem(LOCAL_STORAGE_KEYS.COMPLETION_CODES, JSON.stringify(codes));
            return true;
        } catch (e) {
            console.error('Failed to save completion codes:', e);
            return false;
        }
    }

    /**
     * 完了コードを1件追加
     * @param {string} code
     */
    addCompletionCode(code) {
        if (!this.isAvailable || !code) return false;
        try {
            const current = this.getCompletionCodes();
            if (!current.includes(code)) current.push(code);
            return this.saveCompletionCodes(current);
        } catch (e) {
            console.error('Failed to add completion code:', e);
            return false;
        }
    }

    /**
     * 完了コード一覧を取得
     * @returns {string[]}
     */
    getCompletionCodes() {
        if (!this.isAvailable) return [];
        try {
            const raw = localStorage.getItem(LOCAL_STORAGE_KEYS.COMPLETION_CODES);
            return raw ? JSON.parse(raw) : [];
        } catch (e) {
            console.error('Failed to get completion codes:', e);
            return [];
        }
    }

    /**
     * データのエクスポート
     * @returns {Promise<Object>} エクスポートデータ
     */
    async exportData() {
        try {
            const expenseData = await this.loadExpenseData();
            const codeNumber = await this.loadCodeNumber();
            
            return {
                expenses: expenseData,
                lastCodeNumber: codeNumber,
                exportDate: new Date().toISOString(),
                version: '1.0'
            };
        } catch (error) {
            throw new StorageError(`データのエクスポートに失敗しました: ${error.message}`, 'export');
        }
    }

    /**
     * データのインポート
     * @param {Object} importData - インポートデータ
     * @returns {Promise<boolean>} インポート結果
     */
    async importData(importData) {
        try {
            if (!this.validateImportData(importData)) {
                throw new Error('無効なデータ形式です');
            }

            await this.saveExpenseData(importData.expenses || []);
            if (importData.lastCodeNumber) {
                await this.saveCodeNumber(importData.lastCodeNumber);
            }

            return true;
        } catch (error) {
            throw new StorageError(`データのインポートに失敗しました: ${error.message}`, 'import');
        }
    }

    /**
     * データ構造の検証
     * @param {Object} data - 検証するデータ
     * @returns {boolean} 検証結果
     */
    validateDataStructure(data) {
        return data && 
               typeof data === 'object' && 
               Array.isArray(data.data) &&
               data.timestamp &&
               data.version;
    }

    /**
     * インポートデータの検証
     * @param {Object} data - 検証するデータ
     * @returns {boolean} 検証結果
     */
    validateImportData(data) {
        return data && 
               typeof data === 'object' && 
               Array.isArray(data.expenses);
    }

    /**
     * バックアップを作成
     * @param {Object} data - バックアップするデータ
     */
    createBackup(data) {
        try {
            const backupKey = `${LOCAL_STORAGE_KEYS.EXPENSE_DATA}_backup`;
            localStorage.setItem(backupKey, JSON.stringify(data));
        } catch (error) {
            console.warn('Failed to create backup:', error);
        }
    }

    /**
     * バックアップからの復旧を試行
     * @returns {Array} 復旧されたデータ
     */
    attemptBackupRecovery() {
        try {
            const backupKey = `${LOCAL_STORAGE_KEYS.EXPENSE_DATA}_backup`;
            const backupData = localStorage.getItem(backupKey);
            
            if (backupData) {
                const parsedBackup = JSON.parse(backupData);
                if (this.validateDataStructure(parsedBackup)) {
                    console.log('Data recovered from backup');
                    return parsedBackup.data || [];
                }
            }
        } catch (error) {
            console.error('Backup recovery failed:', error);
        }
        
        return [];
    }

    /**
     * ユニークIDを生成
     * @returns {string} ユニークID
     */
    generateId() {
        return `exp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
}
