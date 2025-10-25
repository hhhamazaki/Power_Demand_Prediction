/**
 * パフォーマンス最適化ユーティリティ
 * 開発ガイドライン準拠: パフォーマンス改善の実装
 */

import { PERFORMANCE_CONFIG } from './Constants.js';

export class PerformanceUtils {
    static cache = new Map();
    static observers = new Map();

    /**
     * デバウンス関数
     * @param {Function} func - 実行する関数
     * @param {number} delay - 遅延時間（ミリ秒）
     * @returns {Function} デバウンスされた関数
     */
    static debounce(func, delay = PERFORMANCE_CONFIG.DEBOUNCE_DELAY) {
        let timeoutId;
        return function (...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    }

    /**
     * スロットル関数
     * @param {Function} func - 実行する関数
     * @param {number} limit - 制限時間（ミリ秒）
     * @returns {Function} スロットルされた関数
     */
    static throttle(func, limit = PERFORMANCE_CONFIG.THROTTLE_LIMIT) {
        let inThrottle;
        return function (...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    /**
     * メモ化関数
     * @param {Function} func - メモ化する関数
     * @param {Function} keyGenerator - キー生成関数
     * @returns {Function} メモ化された関数
     */
    static memoize(func, keyGenerator = JSON.stringify) {
        const cache = new Map();
        
        return function (...args) {
            const key = keyGenerator(args);
            
            if (cache.has(key)) {
                return cache.get(key);
            }
            
            const result = func.apply(this, args);
            cache.set(key, result);
            
            return result;
        };
    }

    /**
     * 遅延実行関数
     * @param {Function} func - 実行する関数
     * @param {number} delay - 遅延時間（ミリ秒）
     * @returns {Promise} Promise
     */
    static delay(func, delay = 0) {
        return new Promise(resolve => {
            setTimeout(() => {
                const result = func();
                resolve(result);
            }, delay);
        });
    }

    /**
     * バッチ処理関数
     * @param {Array} items - 処理するアイテム
     * @param {Function} processor - 処理関数
     * @param {number} batchSize - バッチサイズ
     * @param {number} delay - バッチ間の遅延
     * @returns {Promise<Array>} 処理結果
     */
    static async processBatch(items, processor, batchSize = 10, delay = 10) {
        const results = [];
        
        for (let i = 0; i < items.length; i += batchSize) {
            const batch = items.slice(i, i + batchSize);
            const batchResults = await Promise.all(batch.map(processor));
            results.push(...batchResults);
            
            // 次のバッチまで少し待機（UIをブロックしないため）
            if (i + batchSize < items.length) {
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
        
        return results;
    }

    /**
     * Virtual Scrolling実装
     */
    static createVirtualScrollManager(container, itemHeight = PERFORMANCE_CONFIG.VIRTUAL_SCROLL_ITEM_HEIGHT) {
        return new VirtualScrollManager(container, itemHeight);
    }

    /**
     * IntersectionObserverによる遅延読み込み
     * @param {HTMLElement} target - 監視対象要素
     * @param {Function} callback - コールバック関数
     * @param {Object} options - オプション
     * @returns {IntersectionObserver} Observer
     */
    static createIntersectionObserver(target, callback, options = {}) {
        const defaultOptions = {
            root: null,
            rootMargin: '50px',
            threshold: 0.1
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    callback(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { ...defaultOptions, ...options });

        observer.observe(target);
        return observer;
    }

    /**
     * パフォーマンス計測
     * @param {string} name - 計測名
     * @param {Function} func - 計測する関数
     * @returns {Promise} 実行結果とパフォーマンス情報
     */
    static async measurePerformance(name, func) {
        const startTime = performance.now();
        const startMemory = performance.memory ? performance.memory.usedJSHeapSize : null;

        try {
            const result = await func();
            const endTime = performance.now();
            const endMemory = performance.memory ? performance.memory.usedJSHeapSize : null;

            const metrics = {
                name,
                duration: endTime - startTime,
                memoryDelta: startMemory && endMemory ? endMemory - startMemory : null,
                timestamp: new Date().toISOString()
            };

            console.log(`Performance [${name}]:`, metrics);
            return { result, metrics };
        } catch (error) {
            const endTime = performance.now();
            console.error(`Performance [${name}] failed:`, {
                duration: endTime - startTime,
                error: error.message
            });
            throw error;
        }
    }

    /**
     * リソースの事前読み込み
     * @param {Array} urls - 読み込むURLの配列
     * @returns {Promise<Array>} 読み込み結果
     */
    static preloadResources(urls) {
        return Promise.all(urls.map(url => {
            return new Promise((resolve, reject) => {
                const link = document.createElement('link');
                link.rel = 'preload';
                link.href = url;
                
                if (url.endsWith('.js')) {
                    link.as = 'script';
                } else if (url.endsWith('.css')) {
                    link.as = 'style';
                } else if (url.match(/\.(png|jpg|jpeg|gif|webp)$/i)) {
                    link.as = 'image';
                }

                link.onload = () => resolve(url);
                link.onerror = () => reject(new Error(`Failed to preload: ${url}`));
                
                document.head.appendChild(link);
            });
        }));
    }

    /**
     * DOM操作の最適化
     * @param {Function} domOperations - DOM操作関数
     * @returns {any} 操作結果
     */
    static optimizeDOMOperations(domOperations) {
        // DocumentFragmentを使用してDOMの再構築を最小化
        const fragment = document.createDocumentFragment();
        const result = domOperations(fragment);
        return result;
    }

    /**
     * 大量データの効率的な描画
     * @param {HTMLElement} container - コンテナ要素
     * @param {Array} items - 描画するアイテム
     * @param {Function} itemRenderer - アイテム描画関数
     * @param {number} chunkSize - チャンクサイズ
     */
    static async renderLargeDataset(container, items, itemRenderer, chunkSize = 50) {
        const fragment = document.createDocumentFragment();
        
        for (let i = 0; i < items.length; i += chunkSize) {
            const chunk = items.slice(i, i + chunkSize);
            
            chunk.forEach(item => {
                const element = itemRenderer(item);
                fragment.appendChild(element);
            });
            
            // チャンクごとにフレームを区切る
            await new Promise(resolve => requestAnimationFrame(resolve));
        }
        
        container.appendChild(fragment);
    }

    /**
     * キャッシュの管理
     */
    static setCacheItem(key, value, ttl = 300000) { // 5分のデフォルトTTL
        const expiry = Date.now() + ttl;
        this.cache.set(key, { value, expiry });
    }

    static getCacheItem(key) {
        const item = this.cache.get(key);
        if (!item) return null;
        
        if (Date.now() > item.expiry) {
            this.cache.delete(key);
            return null;
        }
        
        return item.value;
    }

    static clearCache() {
        this.cache.clear();
    }

    /**
     * Web Workersを使用した重い処理の委譲
     * @param {Function} workerFunction - Worker内で実行する関数
     * @param {any} data - Workerに渡すデータ
     * @returns {Promise} 処理結果
     */
    static runInWorker(workerFunction, data) {
        return new Promise((resolve, reject) => {
            const workerScript = `
                self.onmessage = function(e) {
                    try {
                        const result = (${workerFunction.toString()})(e.data);
                        self.postMessage({ success: true, result });
                    } catch (error) {
                        self.postMessage({ success: false, error: error.message });
                    }
                };
            `;

            const blob = new Blob([workerScript], { type: 'application/javascript' });
            const worker = new Worker(URL.createObjectURL(blob));

            worker.onmessage = function(e) {
                if (e.data.success) {
                    resolve(e.data.result);
                } else {
                    reject(new Error(e.data.error));
                }
                worker.terminate();
                URL.revokeObjectURL(worker.scriptURL);
            };

            worker.onerror = function(error) {
                reject(error);
                worker.terminate();
            };

            worker.postMessage(data);
        });
    }
}

/**
 * Virtual Scrolling Manager
 */
export class VirtualScrollManager {
    constructor(container, itemHeight = 50) {
        this.container = container;
        this.itemHeight = itemHeight;
        this.visibleItems = Math.ceil(container.clientHeight / itemHeight) + 5;
        this.startIndex = 0;
        this.data = [];
        this.renderedItems = new Map();
        
        this.setupScrollListener();
    }

    setData(data) {
        this.data = data;
        this.render();
    }

    setupScrollListener() {
        const throttledScroll = PerformanceUtils.throttle(() => {
            this.handleScroll();
        }, 16); // 60fps

        this.container.addEventListener('scroll', throttledScroll);
    }

    handleScroll() {
        const scrollTop = this.container.scrollTop;
        const newStartIndex = Math.floor(scrollTop / this.itemHeight);
        
        if (newStartIndex !== this.startIndex) {
            this.startIndex = newStartIndex;
            this.render();
        }
    }

    render() {
        const endIndex = Math.min(this.startIndex + this.visibleItems, this.data.length);
        const visibleData = this.data.slice(this.startIndex, endIndex);
        
        // コンテナの高さを設定（スクロールバーのため）
        // テーブル tbody を渡された場合は行として描画する
        if (this.container.tagName === 'TBODY') {
            // tbody の高さは親テーブルコンテナで制御するためここではクリアして行を追加
            // 現在の要素をクリア
            this.container.innerHTML = '';

            // ドキュメントフラグメントで行をバッチ追加
            const frag = document.createDocumentFragment();
            visibleData.forEach((item, index) => {
                const tr = document.createElement('tr');
                // 既定のカラムは: タイトル, 種別, 金額, 備考, コード, ステータス, 登録日
                const cols = [];
                cols.push(this._cell(this._escape(String(item.title || item.description || ''))));
                cols.push(this._cell(this._escape(String(item.type || item.category || ''))));
                cols.push(this._cell(`¥${Number(item.amount || 0).toLocaleString()}`, 'text-right'));
                cols.push(this._cell(this._escape(String(item.remark || ''))));
                cols.push(this._cell(this._escape(String(item.code || ''))));
                cols.push(this._cell(this._escape(String(item.status || ''))));
                cols.push(this._cell(this._escape(String(item.date || ''))));

                tr.innerHTML = cols.join('');
                frag.appendChild(tr);
            });

            this.container.appendChild(frag);
            return;
        }

        // 汎用コンテナの場合は既存の方式で要素を絶対配置する
        this.container.style.height = `${this.data.length * this.itemHeight}px`;
        // 現在の要素をクリア
        this.container.innerHTML = '';

        // 新しい要素を描画
        const fragment = document.createDocumentFragment();
        visibleData.forEach((item, index) => {
            const element = this.createItemElement(item, this.startIndex + index);
            fragment.appendChild(element);
        });

        this.container.appendChild(fragment);
    }

    createItemElement(data, index) {
        const element = document.createElement('div');
        element.className = 'virtual-scroll-item';
        element.style.position = 'absolute';
        element.style.top = `${index * this.itemHeight}px`;
        element.style.height = `${this.itemHeight}px`;
        element.style.width = '100%';
        
        // カスタム描画ロジックはサブクラスでオーバーライド
        this.renderItem(element, data, index);
        
        return element;
    }

    renderItem(element, data, index) {
        // デフォルト実装 - セーフにテキスト表示（オブジェクトは展開せず要点のみ）
        try {
            if (data && typeof data === 'object') {
                // 重要フィールドのみ表示して冗長なJSONダンプを避ける
                const title = data.title || data.description || '';
                const amount = data.amount || 0;
                const date = data.date || '';
                element.textContent = `${title} — ¥${Number(amount).toLocaleString()} — ${date}`;
            } else {
                element.textContent = String(data);
            }
        } catch (e) {
            element.textContent = String(data);
        }
    }

    _cell(html, cls = '') {
        return `<td${cls ? ` class="${cls}"` : ''}>${html}</td>`;
    }

    _escape(s) {
        const div = document.createElement('div');
        div.textContent = s;
        return div.innerHTML;
    }
}
