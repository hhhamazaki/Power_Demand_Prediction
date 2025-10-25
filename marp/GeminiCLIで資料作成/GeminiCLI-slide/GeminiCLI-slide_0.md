---
marp: true
theme: uncover
style: |-
  section {
    background-image: url('../kokuban.png');
    background-size: cover;
    font-family: 'Noto Sans JP', sans-serif;
    color: #fff;
    padding: 60px;
  }

  h2 {
    color: #fff;
    text-align: center;
    margin: 0;
    padding: 0 20px;
    font-size: 2.2em;
  }

  .flex-container {
    display: flex;
    justify-content: space-around;
    align-items: flex-start;
    gap: 20px;
    margin-top: 40px; /* Adjust spacing from title */
  }
  .flex-item {
    flex: 1;
    text-align: center;
    background-color: rgba(255, 255, 255, 0.1); /* Semi-transparent background */
    padding: 20px;
    border-radius: 8px;
  }
  .flex-item img {
    width: 100%;
    height: auto;
    max-width: 350px; /* Limit image size */
    margin-bottom: 15px;
  }
  .flex-item h3 {
    font-size: 1.5em; /* Larger heading for items */
    color: #fff;
    margin-top: 0;
    margin-bottom: 10px;
  }
  .flex-item p {
    font-size: 1.1em;
    color: #ccc;
    line-height: 1.6;
  }
---

## なぜMarpを使うのか?

<div class="flex-container">
<div class="flex-item">
<h3>Genspark AIスライド</h3>
<img src="https://placehold.co/400x300" alt="Genspark AIスライドのイメージ">
<p>手軽だが、<br>細かいカスタマイズは難しい</p>
</div>
<div class="flex-item">
<h3>Marp</h3>
<img src="https://placehold.co/400x300" alt="Marpのイメージ">
<p>CSSでデザインを<br>自由に調整可能</p>
</div>
</div>