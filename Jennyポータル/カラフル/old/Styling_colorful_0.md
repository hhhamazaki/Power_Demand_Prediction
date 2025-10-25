# Webサイト構築プロンプト - スタイリングガイド

このドキュメントは、JennyPortalのWebサイトのスタイリングに関するガイドラインと、主要なCSS定義をまとめたものです。
新しいWebサイトを構築する際や、既存のサイトにJennyPortalのスタイルを適用する際のプロンプトとして活用できます。

## 1. 全体的なデザインコンセプト

JennyPortalのWebサイトは、モダンでクリーンなUI/UXを重視しています。
ダークテーマを基調とし、グラデーションやシャドウ効果を効果的に使用することで、視覚的な魅力を高めています。

## 2. フォント

日本語表示には「Noto Sans JP」を使用し、視認性と可読性を確保しています。

```html
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&display=swap" rel="stylesheet">
```

## 3. 主要なCSSスタイル

以下に、`jenny_portal_custom.html`から抽出した主要なCSSスタイルを記述します。

```css
/* リセットとベーススタイル */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Noto Sans JP', sans-serif;
}

body {
    background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
    color: #e2e8f0;
    min-height: 100vh;
    margin: 0;
    padding: 0;
    line-height: 1.6;
}

/* コンテナ */
.container {
    max-width: 1600px;
    margin: 2rem auto;
    padding: 1.5rem;
    background-color: rgba(26, 32, 44, 0.9);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 24px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

/* ヘッダー */
header {
    text-align: center;
    margin-bottom: 3rem;
}

.main-title {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 1rem;
    background: linear-gradient(45deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    color: #667eea; /* フォールバック */
}

.subtitle {
    font-size: 1.25rem;
    color: #cbd5e0;
}

/* セクション */
section {
    margin-bottom: 3rem;
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

section.fade-in {
    opacity: 1;
    transform: translateY(0);
}

.section-title {
    font-size: 1.875rem;
    font-weight: 700;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    color: #667eea;
    border-bottom: 2px solid #667eea;
}

.section-description {
    margin-bottom: 1.5rem;
    color: #a0aec0;
}

/* グリッドレイアウト */
.grid {
    display: grid;
    gap: 1.5rem;
}

.grid-cols-1 {
    grid-template-columns: 1fr;
}

.grid-cols-2 {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

.grid-cols-3 {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.grid-cols-4 {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}

/* カード */
.card {
    background-color: #2d3748;
    border-radius: 0.75rem;
    padding: 1.5rem;
    border: 2px solid;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    position: relative;
    overflow: hidden;
    display: block; /* カード全体をリンクにする */
    text-decoration: none; /* リンクの下線を削除 */
    color: inherit; /* テキスト色を親から継承 */
}

.card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
}

.card:hover::before {
    opacity: 0.1;
}

/* カードのボーダー色 */
.border-blue { border-color: #3b82f6; }
.border-green { border-color: #10b981; }
.border-yellow { border-color: #f59e0b; }
.border-pink { border-color: #ec4899; }
.border-red { border-color: #ef4444; }
.border-teal { border-color: #14b8a6; }
.border-purple { border-color: #8b5cf6; }
.border-orange { border-color: #f97316; }
.border-indigo { border-color: #6366f1; }

/* カードタイトル */
.card-title {
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 0.75rem;
}

.gradient-blue {
    background: linear-gradient(to right, #3b82f6, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.gradient-green {
    background: linear-gradient(to right, #10b981, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.gradient-yellow {
    background: linear-gradient(to right, #f59e0b, #f97316);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.gradient-pink {
    background: linear-gradient(to right, #ec4899, #ef4444);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.gradient-red {
    background: linear-gradient(to right, #ef4444, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.gradient-teal {
    background: linear-gradient(to right, #14b8a6, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.gradient-purple {
    background: linear-gradient(to right, #8b5cf6, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.gradient-orange {
    background: linear-gradient(to right, #f97316, #ef4444);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* カードテキスト */
.card-text {
    color: #cbd5e0;
    margin-bottom: 1rem;
    line-height: 1.5;
}

.card-list {
    margin-bottom: 1rem;
}

.card-list-item {
    font-size: 0.875rem;
    color: #9ca3af;
    margin-bottom: 0.25rem;
}

.card-list-item::before {
    content: '• ';
    margin-right: 0.5rem;
}

/* ボタン */


/* ニュースアイテム */
.news-date {
    font-size: 0.875rem;
    color: #9ca3af;
    margin-bottom: 0.5rem;
}

.news-title {
    font-size: 1.125rem;
    font-weight: 700;
    margin-bottom: 0.75rem;
    color: white;
}

.news-text {
    color: #cbd5e0;
    margin-bottom: 1rem;
}



/* フォーラム特殊要素 */
.forum-label {
    color: #8b5cf6;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
}

.forum-question {
    color: #9ca3af;
    font-size: 0.875rem;
    margin-bottom: 1rem;
}

.question-mark {
    color: #6366f1;
}

/* フッター */
footer {
    text-align: center;
    padding-top: 2rem;
    border-top: 1px solid #4a5568;
}

.footer-text {
    color: #9ca3af;
    margin-bottom: 1rem;
}

.footer-links {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.footer-link {
    color: #6366f1;
    text-decoration: none;
    transition: color 0.3s ease;
}

.footer-link:hover {
    color: #4f46e5;
}

/* スクロールバー */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #2d3748;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: #4a5568;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #667eea;
}

/* レスポンシブ */
@media (max-width: 768px) {
    .container {
        margin: 1rem;
        padding: 1rem;
    }
    
    .main-title {
        font-size: 2rem;
    }
    
    .section-title {
        font-size: 1.5rem;
    }
    
    .grid {
        gap: 1rem;
    }
    
    .card {
        padding: 1rem;
    }
    
    .footer-links {
        flex-direction: column;
        gap: 0.5rem;
    }
}

@media (max-width: 480px) {
    .main-title {
        font-size: 1.5rem;
    }
    
    .subtitle {
        font-size: 1rem;
    }
    
    .section-title {
        font-size: 1.25rem;
    }
    
    .card-title {
        font-size: 1.125rem;
    }
}

/* アニメーション */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.fade-in-delayed {
    animation: fadeInUp 0.8s ease-out forwards;
}

/* ホバーエフェクト強化 */
.card::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.02) 50%, transparent 70%);
    transform: translateX(-100%);
    transition: transform 0.8s ease;
}

.card:hover::after {
    transform: translateX(100%);
}
```

## 4. JavaScriptによる動的なスタイル適用

以下のJavaScriptコードは、セクションの段階的なフェードイン効果とカードのホバーエフェクトを実装しています。

```javascript
// 段階的フェードイン効果
document.addEventListener('DOMContentLoaded', function() {
    const sections = document.querySelectorAll('section');
    
    // Intersection Observer for better performance
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                // 段階的にアニメーションを適用
                setTimeout(() => {
                    entry.target.classList.add('fade-in');
                }, index * 100);
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    sections.forEach(section => {
        observer.observe(section);
    });

    // カードの微細なホバーエフェクト
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
});
```

## 5. 活用方法

このスタイリングガイドは、以下の目的で活用できます。

- **新規Webサイトの構築:** 上記のCSSとJavaScriptをベースに、JennyPortalの統一されたデザインを持つ新しいWebサイトを迅速に構築できます。
- **既存サイトへの適用:** 既存のWebサイトにJennyPortalのスタイルを部分的に、または全体的に適用する際の参考として利用できます。
- **デザインの一貫性維持:** 複数の開発者が関わるプロジェクトにおいて、デザインの一貫性を保つための共通認識として活用できます。

このプロンプトを活用し、魅力的で機能的なWebサイトを構築してください。
