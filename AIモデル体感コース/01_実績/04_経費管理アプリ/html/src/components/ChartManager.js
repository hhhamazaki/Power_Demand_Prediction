/**
 * グラフ管理システム
 * 開発ガイドライン準拠: Chart.jsの最適化と遅延読み込み
 */

import { PERFORMANCE_CONFIG } from '../utils/Constants.js';
import { ErrorHandler } from '../utils/ErrorHandler.js';

export class ChartManager {
    constructor() {
        this.charts = new Map();
        this.chartJsLoaded = false;
        this.loadingPromise = null;
    }

    /**
     * CSS変数を実際のカラー値に解決
     * @param {string} name --var 名（例: '--text-color'）
     * @param {string} fallback 見つからない場合のフォールバック色
     * @returns {string} 解決済みカラー値（例: '#e0e0e0'など）
     */
    getCssVar(name, fallback) {
        // name は '--foo' 期待。内部で var(--bar) 連鎖も解決
        const MAX_DEPTH = 5;
        const doc = document.documentElement;
        const style = (el) => getComputedStyle(el);

        const resolveToken = (token, fb, depth = 0) => {
            if (!token) return fb;
            if (depth > MAX_DEPTH) return fb;
            const t = token.trim();
            // var(--xxx, fallback) 形式
            if (t.startsWith('var(')) {
                const inside = t.slice(4, -1); // remove var( and )
                // 分割（最初のカンマで変数名とフォールバックを分ける）
                const commaIdx = inside.indexOf(',');
                const varName = (commaIdx === -1 ? inside : inside.slice(0, commaIdx)).trim();
                const innerFb = commaIdx === -1 ? fb : inside.slice(commaIdx + 1).trim();
                return resolveToken(resolveToken(varName, innerFb, depth + 1), fb, depth + 1);
            }
            // '--xxx' ならCSSから取得
            if (t.startsWith('--')) {
                const v = style(doc).getPropertyValue(t);
                if (!v) return fb;
                return resolveToken(v, fb, depth + 1);
            }
            return t || fb;
        };
        try {
            return resolveToken(name, fallback, 0) || fallback;
        } catch (_) {
            return fallback;
        }
    }

    /**
     * 初期化（後方互換のためのエイリアス）
     * @returns {Promise<boolean>}
     */
    async initialize() {
        return this.loadChartJs();
    }

    /**
     * Chart.jsの遅延読み込み
     * @returns {Promise<boolean>} 読み込み結果
     */
    async loadChartJs() {
        if (this.chartJsLoaded) {
            return true;
        }

        if (this.loadingPromise) {
            return this.loadingPromise;
        }

        this.loadingPromise = this.performChartJsLoad();
        return this.loadingPromise;
    }

    async performChartJsLoad() {
        try {
            // Chart.jsが既に読み込まれているかチェック
            if (window.Chart) {
                // 可能ならデータラベルプラグインも登録
                try {
                    if (window.ChartDataLabels && !window.__chartDataLabelsRegistered) {
                        window.Chart.register(window.ChartDataLabels);
                        window.__chartDataLabelsRegistered = true;
                    }
                } catch (_) { /* noop */ }
                this.chartJsLoaded = true;
                return true;
            }

            // 動的インポート（モジュール環境の場合）
            if (typeof module !== 'undefined' && module.exports) {
                const chartModule = await import('chart.js');
                const { default: ChartDataLabels } = await import('chartjs-plugin-datalabels');
                window.Chart = chartModule.Chart || chartModule.default || chartModule;
                try {
                    if (ChartDataLabels && !window.__chartDataLabelsRegistered) {
                        window.Chart.register(ChartDataLabels);
                        window.__chartDataLabelsRegistered = true;
                    }
                } catch (_) { /* noop */ }
            } else {
                // CDNから読み込み（現在の環境）
                await this.loadChartJsFromCDN();
            }

            this.chartJsLoaded = true;
            return true;
        } catch (error) {
            ErrorHandler.handle(error, 'ChartManager.loadChartJs');
            return false;
        }
    }

    /**
     * CDNからChart.jsを読み込み
     * @returns {Promise<void>}
     */
    loadChartJsFromCDN() {
        return new Promise((resolve, reject) => {
            const ensurePluginRegistered = () => {
                try {
                    if (window.Chart && window.ChartDataLabels && !window.__chartDataLabelsRegistered) {
                        window.Chart.register(window.ChartDataLabels);
                        window.__chartDataLabelsRegistered = true;
                    }
                } catch (_) { /* noop */ }
            };

            const hasScriptLike = (substr) => {
                return Array.from(document.querySelectorAll('script[src]')).some(s => (s.getAttribute('src') || '').includes(substr));
            };

            const loadScript = (src) => new Promise((res, rej) => {
                if (hasScriptLike(src)) {
                    // 既存スクリプトがあり → その読み込み完了を待てない場合があるため即resolve
                    res();
                    return;
                }
                const s = document.createElement('script');
                s.async = true;
                s.src = src;
                s.onload = res;
                s.onerror = () => rej(new Error(`Failed to load: ${src}`));
                document.head.appendChild(s);
            });

            // ローカル(vendor/)優先で読み込み、失敗時にCDNへフォールバック
            const tryLoadOne = async (sources) => {
                let lastErr;
                for (const src of sources) {
                    try {
                        await loadScript(src);
                        return;
                    } catch (e) {
                        lastErr = e;
                    }
                }
                throw lastErr || new Error('No source to load');
            };

            const loadAll = async () => {
                try {
                    // UMD版を明示的にロード（v4）
                    if (!window.Chart) {
                        await tryLoadOne([
                            './vendor/chart.umd.min.js',
                            'https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js'
                        ]);
                    }
                    if (!window.Chart) {
                        throw new Error('Chart.js UMD failed to expose window.Chart');
                    }
                    // データラベルプラグイン（UMD）
                    if (!window.ChartDataLabels) {
                        await tryLoadOne([
                            './vendor/chartjs-plugin-datalabels.min.js',
                            'https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js'
                        ]);
                    }
                    ensurePluginRegistered();
                    resolve();
                } catch (e) {
                    reject(e);
                }
            };

            // 既にChartがいればプラグインだけ確認
            if (window.Chart) {
                if (!window.ChartDataLabels) {
                    tryLoadOne([
                        './vendor/chartjs-plugin-datalabels.min.js',
                        'https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js'
                    ]).then(() => {
                        ensurePluginRegistered();
                        resolve();
                    }).catch(reject);
                } else {
                    ensurePluginRegistered();
                    resolve();
                }
            } else {
                loadAll();
            }
        });
    }

    /**
     * 月別サマリーグラフの作成
     * @param {Array} expenseData - 経費データ
     * @param {string} canvasId - キャンバスのID
     * @returns {Promise<Chart>} Chart.jsインスタンス
     */
    async createMonthlyChart(expenseData, canvasId = 'monthlyChart') {
        try {
            await this.loadChartJs();
            
            const canvas = document.getElementById(canvasId);
            if (!canvas) {
                throw new Error(`Canvas element with ID "${canvasId}" not found`);
            }

            // 既存のチャートを破棄
            this.destroyChart(canvasId);

            const monthlyData = this.aggregateMonthlyData(expenseData);
            const chartConfig = this.createMonthlyChartConfig(monthlyData);

            const chart = new (window.Chart || Chart)(canvas, chartConfig);
            this.charts.set(canvasId, chart);

            return chart;
        } catch (error) {
            ErrorHandler.handle(error, 'ChartManager.createMonthlyChart');
            throw error;
        }
    }

    /**
     * カテゴリ別グラフの作成
     * @param {Array} expenseData - 経費データ
     * @param {string} canvasId - キャンバスのID
     * @returns {Promise<Chart>} Chart.jsインスタンス
     */
    async createCategoryChart(expenseData, canvasId = 'categoryChart') {
        try {
            await this.loadChartJs();
            
            const canvas = document.getElementById(canvasId);
            if (!canvas) {
                throw new Error(`Canvas element with ID "${canvasId}" not found`);
            }

            // 既存のチャートを破棄
            this.destroyChart(canvasId);

            const categoryData = this.aggregateCategoryData(expenseData);
            const chartConfig = this.createCategoryChartConfig(categoryData);

            const chart = new (window.Chart || Chart)(canvas, chartConfig);
            this.charts.set(canvasId, chart);

            return chart;
        } catch (error) {
            ErrorHandler.handle(error, 'ChartManager.createCategoryChart');
            throw error;
        }
    }

    /**
     * 月別データの集計
     * @param {Array} expenseData - 経費データ
     * @returns {Object} 集計されたデータ
     */
    aggregateMonthlyData(expenseData) {
        const monthlyAggregation = {};

        expenseData.forEach(expense => {
            const date = new Date(expense.date);
            const monthKey = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`;
            
            if (!monthlyAggregation[monthKey]) {
                monthlyAggregation[monthKey] = {
                    amount: 0,
                    count: 0
                };
            }
            
            monthlyAggregation[monthKey].amount += expense.amount;
            monthlyAggregation[monthKey].count += 1;
        });

        // 過去12ヶ月のデータを生成
        const labels = [];
        const amounts = [];
        const counts = [];
        
        const now = new Date();
        for (let i = 11; i >= 0; i--) {
            const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
            const monthKey = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`;
            const monthLabel = `${date.getFullYear()}/${(date.getMonth() + 1).toString().padStart(2, '0')}`;
            
            labels.push(monthLabel);
            amounts.push(monthlyAggregation[monthKey]?.amount || 0);
            counts.push(monthlyAggregation[monthKey]?.count || 0);
        }

        return { labels, amounts, counts };
    }

    /**
     * カテゴリ別データの集計
     * @param {Array} expenseData - 経費データ
     * @returns {Object} 集計されたデータ
     */
    aggregateCategoryData(expenseData) {
        const categoryAggregation = {};

        expenseData.forEach(expense => {
            const category = expense.type || 'その他';
            
            if (!categoryAggregation[category]) {
                categoryAggregation[category] = {
                    amount: 0,
                    count: 0
                };
            }
            
            categoryAggregation[category].amount += expense.amount;
            categoryAggregation[category].count += 1;
        });

        const labels = Object.keys(categoryAggregation);
        const amounts = labels.map(label => categoryAggregation[label].amount);
        const counts = labels.map(label => categoryAggregation[label].count);

        return { labels, amounts, counts };
    }

    /**
     * 月別チャート設定の作成
     * @param {Object} data - 集計データ
     * @returns {Object} Chart.js設定オブジェクト
     */
    createMonthlyChartConfig(data) {
        // 最大値に少し余白を持たせた表示上限を算出
        const maxVal = Math.max(0, ...(data.amounts || [0]));
        const niceMax = (() => {
            if (maxVal <= 0) return 10;
            const exponent = Math.floor(Math.log10(maxVal));
            const base = Math.pow(10, exponent);
            const candidates = [1, 2, 5, 10].map(m => m * base);
            const picked = candidates.find(v => v >= maxVal) || 10 * base;
            return Math.ceil(picked * 1.1);
        })();

    // 色をCSS変数から解決
    const color1 = this.getCssVar('--chart-color-1', '#00E5FF');
    const legendColor = this.getCssVar('--chart-legend-color', this.getCssVar('--text-color', '#f0f0f0'));
    const axisXColor = this.getCssVar('--chart-axis-x-color', this.getCssVar('--text-color', '#eaeaea'));
    const axisYColor = this.getCssVar('--chart-axis-y-color', this.getCssVar('--text-color', '#eaeaea'));
    const dataLabelColor = this.getCssVar('--chart-datalabel-color', '#ffffff');
    const cardBorder = this.getCssVar('--card-border', '#4a4a6a');

    return {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: '月別経費金額',
                    data: data.amounts,
            borderColor: color1,
                    backgroundColor: 'rgba(0, 229, 255, 0.12)',
                    borderWidth: 3,
                    tension: 0.35,
            fill: true,
        pointStyle: 'circle',
        pointBackgroundColor: color1,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    hitRadius: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                layout: { padding: { top: 12, right: 12, bottom: 4, left: 4 } },
                animation: {
                    duration: PERFORMANCE_CONFIG.CHART_ANIMATION_DURATION
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    datalabels: {
                        display: (ctx) => (ctx.dataset.data[ctx.dataIndex] || 0) > 0,
                        color: dataLabelColor,
                        backgroundColor: 'rgba(0,0,0,0.45)',
                        borderRadius: 4,
                        padding: { top: 2, right: 6, bottom: 2, left: 6 },
                        anchor: 'end',
                        align: 'top',
                        offset: 6,
                        formatter: (v) => `¥${Number(v).toLocaleString()}`,
                        clamp: true
                    },
                    legend: {
                        labels: {
                            color: legendColor,
                            font: {
                                family: "'Rajdhani', sans-serif",
                                size: 14,
                                weight: '600'
                            },
                            usePointStyle: true,
                            pointStyle: 'circle',
                            boxWidth: 12,
                            boxHeight: 12
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.7)',
                        titleColor: this.getCssVar('--text-color', '#e0e0e0'),
                        bodyColor: this.getCssVar('--text-color', '#e0e0e0'),
                        borderColor: cardBorder,
                        borderWidth: 1,
                        callbacks: {
                            label: function(context) {
                                return `金額: ¥${context.parsed.y.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.12)'
                        },
                        ticks: {
                            color: axisXColor,
                            font: {
                                family: "'Rajdhani', sans-serif",
                                size: 13,
                                weight: '600'
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        suggestedMax: niceMax,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.12)'
                        },
                        ticks: {
                            color: axisYColor,
                            font: {
                                family: "'Rajdhani', sans-serif",
                                size: 13,
                                weight: '600'
                            },
                            callback: function(value) {
                                return '¥' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        };
    }

    /**
     * カテゴリチャート設定の作成
     * @param {Object} data - 集計データ
     * @returns {Object} Chart.js設定オブジェクト
     */
    createCategoryChartConfig(data) {
        const colorVars = [
            ['--chart-color-1', '#00E5FF'],
            ['--chart-color-2', '#FF3DFF'],
            ['--chart-color-3', '#22D3EE'],
            ['--chart-color-4', '#34D399'],
            ['--chart-color-5', '#F59E0B'],
        ];
        const dynamicColors = colorVars.map(([v, fb]) => this.getCssVar(v, fb)).concat([
            '#FB7185', '#A78BFA', '#4ADE80'
        ]);

        // ラベル別カラーのオーバーライド（例: 仮払/仮払い は視認性の高いアンバー）
        const advanceColor = this.getCssVar('--chart-color-advance', '#FFB300');
        const pickColor = (label, fallback) => {
            const l = (label || '').trim();
            if (l.includes('仮払') || l.includes('仮払い')) return advanceColor;
            return fallback;
        };
        const bgColors = data.labels.map((label, i) => pickColor(label, dynamicColors[i % dynamicColors.length]));

        return {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.amounts,
                    backgroundColor: bgColors,
                    borderColor: bgColors,
                    borderWidth: 2,
                    hoverBorderWidth: 3,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: PERFORMANCE_CONFIG.CHART_ANIMATION_DURATION
                },
                cutout: '58%',
                plugins: {
                    datalabels: {
                        color: this.getCssVar('--chart-datalabel-color', '#ffffff'),
                        backgroundColor: 'rgba(0,0,0,0.55)',
                        borderRadius: 6,
                        padding: { top: 2, right: 6, bottom: 2, left: 6 },
                        offset: 6,
                        font: { weight: '700' },
                        formatter: (value, ctx) => {
                            const total = ctx.dataset.data.reduce((a, b) => a + b, 0) || 0;
                            if (total === 0) return '';
                            const pct = (value / total) * 100;
                            // 小さすぎるセグメントはラベル非表示
                            if (pct < 6) return '';
                            return `${pct.toFixed(1)}%`;
                        }
                    },
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: this.getCssVar('--chart-legend-color', this.getCssVar('--text-color', '#f0f0f0')),
                            font: {
                                family: "'Rajdhani', sans-serif",
                                size: 12,
                                weight: '600'
                            },
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle',
                            boxWidth: 12,
                            boxHeight: 12
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.7)',
                        titleColor: this.getCssVar('--text-color', '#e0e0e0'),
                        bodyColor: this.getCssVar('--text-color', '#e0e0e0'),
                        borderColor: this.getCssVar('--card-border', '#4a4a6a'),
                        borderWidth: 1,
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ¥${value.toLocaleString()} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        };
    }

    /**
     * チャートの破棄
     * @param {string} chartId - チャートID
     */
    destroyChart(chartId) {
        const existingChart = this.charts.get(chartId);
        if (existingChart) {
            existingChart.destroy();
            this.charts.delete(chartId);
        }
    }

    /**
     * 全チャートの破棄
     */
    destroyAllCharts() {
        this.charts.forEach((chart, id) => {
            chart.destroy();
        });
        this.charts.clear();
    }

    /**
     * 全チャートのリサイズ
     */
    resizeCharts() {
        this.charts.forEach((chart) => {
            if (chart && typeof chart.resize === 'function') {
                chart.resize();
            }
        });
    }

    /**
     * チャートデータの更新
     * @param {string} chartId - チャートID
     * @param {Object} newData - 新しいデータ
     */
    updateChartData(chartId, newData) {
        const chart = this.charts.get(chartId);
        if (chart) {
            chart.data = newData;
            chart.update('active');
        }
    }

    /**
     * チャートのリサイズ
     * @param {string} chartId - チャートID
     */
    resizeChart(chartId) {
        const chart = this.charts.get(chartId);
        if (chart) {
            chart.resize();
        }
    }

    /**
     * 全チャートのリサイズ
     */
    resizeAllCharts() {
        this.charts.forEach(chart => {
            chart.resize();
        });
    }

    /**
     * チャートの取得
     * @param {string} chartId - チャートID
     * @returns {Chart|null} Chart.jsインスタンス
     */
    getChart(chartId) {
        return this.charts.get(chartId) || null;
    }

    /**
     * アクティブなチャート一覧の取得
     * @returns {Array} チャートIDの配列
     */
    getActiveCharts() {
        return Array.from(this.charts.keys());
    }
}
