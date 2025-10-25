## サイバーパンク風Webサイトのスタイリング

以下は、サイバーパンクをテーマにしたWebサイトのCSSスタイリングです。Webサイト構築プロンプトの一部として活用できます。

```css
:root {
    --bg-color: #1a1a2e;
    --card-bg-color: #2a2a4a;
    --text-color: #e0e0e0;
    --accent-color: #00f0ff; /* Cyan */
    --secondary-accent-color: #ff00ff; /* Magenta */
    --border-color: #4a4a6a;
    --shadow-color: rgba(0, 240, 255, 0.3);
    --glow-filter: drop-shadow(0 0 5px var(--accent-color)) drop_shadow(0 0 10px var(--accent-color));
}

html {
    scroll-behavior: smooth; /* Smooth scrolling */
}

body {
    font-family: 'Roboto', sans-serif;
    background-color: var(--bg-color);
    color: var(--text-color);
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: 100vh;
    box-sizing: border-box;
    font-size: 1.05em; /* Increased base font size */
}

.download-button {
    background-color: var(--accent-color);
    color: var(--bg-color);
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
    font-family: 'Orbitron', sans-serif;
    font-size: 1em;
    transition: background-color 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
    box-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
}

.download-button:hover {
    background-color: #00b3cc; /* Darker cyan on hover */
    box-shadow: 0 0 15px var(--accent-color);
}

main {
    width: 100%;
    max-width: 1600px; /* Max width for the container */
    padding: 20px;
    box-sizing: border-box;
    flex-grow: 1; /* メインコンテンツが利用可能なスペースを埋めるようにする */
}

section {
    background-color: var(--card-bg-color);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 35px;
    margin-bottom: 35px;
    box-shadow: 0 0 20px var(--shadow-color);
    transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
}

section:hover {
    transform: translateY(-5px);
    box-shadow: 0 0 25px var(--accent-color);
}

section h2 {
    font-family: 'Orbitron', sans-serif;
    color: var(--secondary-accent-color);
    margin-top: 0;
    border-bottom: 2px solid var(--border-color);
    padding-bottom: 12px;
    margin-bottom: 15px; /* Space below h2 */
    font-size: 1.8em; /* Increased font size */
    text-shadow: 0 0 10px var(--secondary-accent-color), 0 0 20px rgba(255, 0, 255, 0.2); /* Stronger glow */
}

/* Style for description text within main heading cards */
section > p {
    line-height: 1.7;
    margin-bottom: 25px; /* Space below description text */
}

/* Container for sub-cards */
.sub-card-container {
    display: flex;
    flex-wrap: wrap;
    gap: 20px; /* Space between cards */
    justify-content: flex-start; /* Align cards to the left */
}

/* Style for sub-cards */
.sub-card {
    background-color: rgba(42, 42, 74, 0.7); /* Slightly transparent version of card-bg-color */
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 0 10px rgba(0, 240, 255, 0.2); /* Light shadow */
    transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
    flex: 1 1 300px; /* Each card maintains a minimum width of 300px and wraps automatically based on available space */
    box-sizing: border-box; /* Include padding and border in the width */
}

/* Reset link styles within sub-cards to make the entire card behave like a link */
.sub-card a {
    text-decoration: none; /* Remove underline */
    color: inherit; /* Inherit color from parent element */
    display: block; /* Make the entire card a link */
}

.sub-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 0 15px var(--accent-color);
}

.sub-card h3 {
    font-family: 'Orbitron', sans-serif;
    color: var(--accent-color);
    margin-top: 0; /* Remove top margin for h3 within sub-card */
    margin-bottom: 15px; /* Bottom margin for h3 within sub-card */
    font-size: 1.3em; /* Increased font size */
    text-shadow: 0 0 8px var(--accent-color), 0 0 15px rgba(0, 240, 255, 0.2); /* Stronger glow */
}

/* Style for p tags within sub-cards */
.sub-card p {
    line-height: 1.7;
    margin-bottom: 12px;
}

section ul {
    list-style: none;
    padding: 0;
    margin-top: 0; /* Remove default top margin for ul */
}

section ul li {
    background-color: rgba(0, 0, 0, 0.2);
    border-left: 3px solid var(--accent-color);
    padding: 10px 15px;
    margin-bottom: 8px;
    border-radius: 5px;
    font-size: 0.95em;
}

section ul li a {
    color: var(--text-color); /* リンクの色をテキスト色に合わせる */
    text-decoration: none; /* 下線を削除 */
    display: block; /* li全体をリンクにする */
}

section ul li a:hover {
    color: var(--accent-color); /* ホバー時にアクセントカラーにする */
}

/* Styles for mini-link-cards */
.mini-link-card-container {
    display: flex;
    flex-wrap: wrap;
    gap: 10px; /* Smaller gap for inline cards */
    margin-bottom: 15px; /* Space between mini-cards and other content */
}

.mini-link-card {
    background-color: rgba(74, 74, 106, 0.7); /* Slightly different background for distinction */
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 10px 15px;
    box-shadow: 0 0 8px rgba(0, 240, 255, 0.15);
    transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
    flex: 0 0 auto; /* Don't grow, take content width */
}

.mini-link-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 12px var(--accent-color);
}

.mini-link-card a {
    color: var(--text-color);
    text-decoration: none;
    display: block;
    font-size: 0.9em; /* Smaller font size */
    font-family: 'Orbitron', sans-serif; /* Use Orbitron for these buttons too */
    text-shadow: 0 0 5px var(--accent-color); /* Subtle glow */
}

.mini-link-card a:hover {
    color: var(--accent-color);
}

.news-item {
    font-size: 0.9em;
    color: var(--text-color);
    margin-bottom: 10px;
    border-bottom: 1px dashed var(--border-color);
    padding-bottom: 10px;
}

.news-item:last-child {
    border-bottom: none;
}

.news-date {
    color: var(--secondary-accent-color);
    font-weight: bold;
    margin-right: 10px;
}

footer {
    width: 100%;
    max-width: 1600px;
    padding: 20px;
    box-sizing: border-box;
    display: flex;
    justify-content: center; /* ボタンを中央に配置 */
    margin-top: 20px; /* メインコンテンツとの間にスペースを追加 */
}

@media (max-width: 768px) {
    main {
        padding: 10px;
    }

    section {
        padding: 20px;
    }

    /* On small screens, make sub-cards a single column */
    .sub-card {
        flex: 1 1 100%;
    }
}
```
