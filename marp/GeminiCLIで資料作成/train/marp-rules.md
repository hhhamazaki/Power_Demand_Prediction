---
theme: default
paginate: true
backgroundColor: black
color: white
style: |
  section {
    background-image: url('../../kokuban.png'); /* marp/GeminiCLIで資料作成/kokuban.png への相対パス */
    background-size: cover;
    font-family: "Noto Sans JP", sans-serif;
    text-align: center;
  }

  /* Title Slide Layout */
  section.title-slide h1 {
    font-size: 3em;
    margin-bottom: 0.5em;
  }
  section.title-slide h2 {
    font-size: 1.5em;
  }

  /* Key Point Slide Layout */
  section.key-point-slide h3 {
    font-size: 1.2em;
    margin-bottom: 0.5em;
  }
  section.key-point-slide h1 {
    font-size: 3em;
    margin-bottom: 0.5em;
  }
  section.key-point-slide h2 {
    font-size: 1.5em;
  }
  section.key-point-slide p.note {
    font-size: 0.8em;
    text-align: center;
  }

  /* Bulleted List Slide Layout */
  section.bullet-list-slide h1 {
    font-size: 2em;
    margin-bottom: 1em;
  }
  section.bullet-list-slide ul {
    list-style-type: disc;
    text-align: left;
    margin-left: 20%;
    font-size: 1.5em;
  }
  section.bullet-list-slide ul li {
    margin-bottom: 0.5em;
  }
  section.bullet-list-slide p.note {
    font-size: 0.8em;
    text-align: left;
    margin-left: 20%;
    margin-top: 1em;
  }

  /* Concept Introduction Slide Layout */
  section.concept-slide h1 {
    font-size: 2em;
    margin-bottom: 1em;
  }
  section.concept-slide h2 {
    font-size: 3em;
    margin-bottom: 1em;
  }
  section.concept-slide p {
    font-size: 1.5em;
  }

  /* Comparison Slide Layout */
  section.comparison-slide h1 {
    font-size: 2em;
    margin-bottom: 1em;
  }
  section.comparison-slide .columns {
    display: flex;
    justify-content: space-around;
    align-items: flex-start;
    text-align: center;
  }
  section.comparison-slide .column {
    flex: 1;
    padding: 0 1em;
  }
  section.comparison-slide .column h2 {
    font-size: 1.5em;
    margin-bottom: 0.5em;
  }
  section.comparison-slide .column img {
    max-width: 100%;
    height: auto;
    margin-bottom: 0.5em;
  }
  section.comparison-slide .column p {
    font-size: 1.2em;
  }

  /* Single Point with Image Slide Layout */
  section.image-text-slide h1 {
    font-size: 2em;
    margin-bottom: 1em;
  }
  section.image-text-slide img {
    max-width: 60%;
    height: auto;
    margin-bottom: 1em;
  }
  section.image-text-slide p {
    font-size: 1.5em;
  }

/* Placeholder Image Rule */
/* Replace image paths with https://placeholder.co/WIDTHxHEIGHT */
/* Example: ![placeholder 600x400](https://placeholder.co/600x400) */
