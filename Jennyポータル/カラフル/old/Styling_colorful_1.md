# JennyPortal Styling

This file contains the CSS styles extracted from `JennyPortal_colorful_1.html`. It can be used as a reference for creating a unified web design prompt.

```css
/* Define Cyber theme root variables */
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

/* Reset and base styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Noto Sans JP', sans-serif; /* Prioritize Noto Sans JP */
}

body {
    background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%); /* Keep Colorful gradient background */
    color: var(--text-color); /* Use Cyber text color */
    min-height: 100vh;
    margin: 0;
    padding: 0;
    line-height: 1.6;
    display: flex;
    flex-direction: column;
    align-items: center;
    font-size: 1.05em; /* Reverted to original Cyber base font size */
}

/* Main content area - now acts as the primary container */
main {
    width: 100%;
    max-width: 1600px;
    margin: 0 auto; /* Removed top margin, center horizontally */
    padding: 20px; /* Reverted to original Cyber padding */
    background-color: rgba(26, 32, 44, 0.9); /* Background from Colorful container */
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 24px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    flex-grow: 1; /* Allow main to grow and push footer down */
    box-sizing: border-box;
}

/* Section styles - Reverted to Cyber style with consistent border */
section {
    margin-bottom: 35px; /* Revert to Cyber's specific margin */
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.6s ease-out, transform 0.6s ease-out;
    background-color: var(--card-bg-color); /* Use Cyber card background color */
    border: 1px solid var(--border-color); /* Revert to Cyber border */
    border-radius: 10px; /* Revert to Cyber border-radius */
    padding: 35px; /* Keep original padding */
    box-shadow: 0 0 20px var(--shadow-color); /* Revert to Cyber shadow */
    transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out; /* Add Cyber hover transition */
}

section:hover {
    transform: translateY(-5px); /* Revert to Cyber hover transform */
    box-shadow: 0 0 25px var(--accent-color); /* Revert to Cyber hover shadow */
}

section.fade-in {
    opacity: 1;
    transform: translateY(0);
}

/* Section title - Keep Orbitron font for Cyber feel, Colorful gradients */
.section-title {
    font-size: 1.8em; /* Adjusted to original Cyber font size */
    font-weight: 700;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    color: #667eea; /* Keep Colorful section title color */
    border-bottom: 2px solid #667eea; /* Keep Colorful section title border */
    font-family: 'Orbitron', sans-serif;
}

/* Section description */
.section-description {
    margin-bottom: 1.5rem;
    color: #a0aec0; /* Keep Colorful description color */
}

/* Grid layout */
.grid {
    display: grid;
    gap: 20px; /* Revert to Cyber's specific gap */
    /* Default for larger screens */
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); /* Base for 4 columns */
}

/* Responsive grid adjustments */
/* For screens smaller than 1200px (example breakpoint for 3 columns from 4) */
@media (max-width: 1200px) {
    #introduction .grid,
    #training .grid {
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); /* Adjust to 3 columns */
    }
}

/* For screens smaller than 768px (2 columns) */
@media (max-width: 768px) {
    .grid {
        grid-template-columns: repeat(auto-fit, minmax(calc(50% - 10px), 1fr)); /* 2 columns, accounting for gap */
        gap: 20px; /* Ensure gap is consistent */
    }
}

/* For screens smaller than 480px (1 column) */
@media (max-width: 480px) {
    .grid {
        grid-template-columns: 1fr; /* 1 column */
        gap: 20px; /* Ensure gap is consistent */
    }
}

/* Card styles - Reverted to Cyber style, keeping colorful borders/gradients */
.card {
    background-color: rgba(42, 42, 74, 0.7); /* Revert to Cyber transparent background */
    border-radius: 8px; /* Revert to Cyber border-radius */
    padding: 20px; /* Revert to Cyber padding */
    border: 1px solid; /* Keep border, color set by border-* classes */
    transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out; /* Revert to Cyber transition */
    box-shadow: 0 0 10px rgba(0, 240, 255, 0.2); /* Revert to Cyber light shadow */
    position: relative;
    overflow: hidden;
    color: inherit;
    flex: 1 1 300px; /* Revert to Cyber flex properties */
    box-sizing: border-box;
}

/* Remove Colorful specific hover effects */
.card::before, .card::after {
    content: none;
}

.card:hover {
    transform: translateY(-3px); /* Revert to Cyber hover transform */
    box-shadow: 0 0 15px var(--accent-color); /* Revert to Cyber hover shadow */
}

/* When the card itself is a link (e.g., preparation, try sections) */
a.card { /* Target <a> tags that are also .card */
    text-decoration: none; /* Explicitly remove underline */
}

/* Card border colors - Keep Colorful colors and define custom property for list items */
.border-blue { border-color: #3b82f6; --card-border-color-var: #3b82f6; }
.border-green { border-color: #10b981; --card-border-color-var: #10b981; }
.border-yellow { border-color: #f59e0b; --card-border-color-var: #f59e0b; }
.border-pink { border-color: #ec4899; --card-border-color-var: #ec4899; }
.border-red { border-color: #ef4444; --card-border-color-var: #ef4444; }
.border-teal { border-color: #14b8a6; --card-border-color-var: #14b8a6; }
.border-purple { border-color: #8b5cf6; --card-border-color-var: #8b5cf6; }
.border-orange { border-color: #f97316; --card-border-color-var: #f97316; }
.border-indigo { border-color: #6366f1; --card-border-color-var: #6366f1; }

/* Card title - Keep Orbitron font for Cyber feel, Colorful gradients */
.card-title {
    font-size: 1.3em; /* Adjusted to original Cyber font size */
    font-weight: 700;
    margin-bottom: 0.75rem;
    font-family: 'Orbitron', sans-serif;
}

/* Gradient text colors for card titles - Keep Colorful gradients */
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

/* Card text */
.card-text {
    color: var(--text-color); /* Revert to Cyber text color */
    margin-bottom: 1rem;
    line-height: 1.5;
}

/* Card list styles - Reverted to Cyber list item style, using custom property for border color */
.card-list {
    margin-bottom: 1rem;
    list-style: none;
    padding: 0;
}

.card-list-item {
    font-size: 0.95em; /* Reverted to original Cyber font size */
    color: var(--text-color);
    margin-bottom: 8px;
    background-color: rgba(0, 0, 0, 0.2); /* Revert to original Cyber list item bg */
    border-left: 3px solid var(--card-border-color-var); /* Use custom property for dynamic border color */
    padding: 10px 15px;
    border-radius: 5px;
    /* Removed transform transition */
    transition: background-color 0.3s ease; /* Only background transition */
}

.card-list-item:hover {
    background-color: rgba(0, 0, 0, 0.4); /* Slightly darker on hover */
    /* Removed transform: translateX(3px); */
}

.card-list-item a {
    color: inherit;
    text-decoration: none;
    display: block;
}

/* Download button specific styles - Reverted to Cyber style */
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

/* Mini link card styles - Adjusted for wrapping text */
.mini-link-card-container {
    display: flex;
    flex-wrap: wrap; /* Allow wrapping of mini-link-cards themselves */
    gap: 10px;
    margin-bottom: 15px;
}

.mini-link-card {
    background-color: rgba(42, 42, 74, 0.5); /* Lighter transparency of Cyber card bg */
    border: 1px solid var(--border-color); /* Revert to Cyber border */
    border-radius: 6px;
    padding: 10px 15px;
    box-shadow: 0 0 8px rgba(0, 240, 255, 0.15); /* Revert to Cyber like shadow */
    transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
    flex: 0 0 auto; /* Prevent shrinking, take content width */
    max-width: 100%; /* Ensure mini-link-card itself wraps within its container */
    box-sizing: border-box;
}

.mini-link-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 12px var(--accent-color); /* Revert to Cyber like hover shadow */
    background-color: rgba(42, 42, 74, 0.7); /* Slightly darker on hover */
}

.mini-link-card a {
    color: var(--text-color); /* Revert to Cyber text color */
    text-decoration: none;
    display: block;
    font-size: 0.9em; /* Reverted to original Cyber font size */
    font-family: 'Orbitron', sans-serif; /* Revert to Cyber font */
    text-shadow: 0 0 5px var(--accent-color); /* Revert to Cyber glow */
    /* Allow text wrapping */
    white-space: normal; /* Allow text to wrap */
    overflow: visible; /* Ensure content is not hidden */
    text-overflow: clip; /* Remove ellipsis */
}

.mini-link-card a:hover {
    color: var(--accent-color); /* Revert to Cyber accent color on hover */
}

/* Footer styles - Minimal Cyber style for download button container */
footer {
    width: 100%;
    max-width: 1600px;
    padding: 20px;
    box-sizing: border-box;
    display: flex;
    justify-content: center;
    margin-top: 20px;
    background-color: transparent; /* No background */
    border-top: none; /* No border */
}

/* Remove other Colorful footer elements if they were present */
.footer-text, .footer-links, .footer-link {
    display: none; /* Hide other footer elements */
}

/* Scrollbar styles from JennyPortal_colorful.html */
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

/* Animations from JennyPortal_colorful.html */
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

/* Original Cyber did not have these, so remove them */
/* .card::after {
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
} */

/* Responsive adjustments for main content and sections */
@media (max-width: 768px) {
    main {
        padding: 10px; /* Adjust padding for smaller screens */
        /* Removed specific top margin, relying on auto margins */
    }

    section {
        padding: 20px;
    }

    .section-title {
        font-size: 1.5em; /* Adjusted for responsive Cyber font size */
    }

    /* .grid is handled by global media queries above */

    .card {
        padding: 1rem;
    }
}

@media (max-width: 480px) {
    .section-title {
        font-size: 1.25em; /* Adjusted for responsive Cyber font size */
    }

    .card-title {
        font-size: 1.125em; /* Adjusted for responsive Cyber font size */
    }
}
```
