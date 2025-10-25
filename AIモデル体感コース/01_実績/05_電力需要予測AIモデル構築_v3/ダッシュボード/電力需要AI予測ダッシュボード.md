---
marp: true
theme: gaia
_class: lead
paginate: true
backgroundColor: #000

style: |
    /* スライド余白を取り除き、フルスライド用の画像クラスを定義 */
    section {
        padding: 0 !important;
        position: relative; /* 子要素の絶対配置基準 */
        overflow: hidden;
    }
    /* 余白なしでスライド幅いっぱいに広げる画像 */
    .full-bleed-image {
        width: 100% !important;
        height: auto;
        display: block;
        margin: 0; /* 余白をなくす */
        box-shadow: none;
        align-self: stretch;
        z-index: 1;
    }
    /* top-center スライドの h2 スタイルを統合: シアン色 + 中央揃え + 影 */
    .top-center h2 {
        color: #00FFFF; /* シアン */
        text-shadow: 0 2px 6px rgba(0,0,0,0.7);
        margin: 0 0 6px 0;
        padding: 8px 0 0 0;
        font-size: 48px;
        font-weight: 600;
        text-align: center;
        width: 100%;
    }
---
<section class="top-center">
    <h2>学習年「2016-2024」9年で変動大 ⇒ 分割で精度向上？</h2>
    <!-- 余白なしでスライド幅いっぱいに表示 -->
    <img src="LightGBM_Ypred.png" class="full-bleed-image">
</section>

---
<section class="top-center">
    <h2>学習年「2024」モデルKeras（単年で精度悪化）</h2>
    <!-- 余白なしでスライド幅いっぱいに表示 -->
    <img src="24_Keras予測_改善前.png" class="full-bleed-image">
</section>

---
<section class="top-center">
    <h2>学習年「2024」モデルKeras（チューニングで精度向上）</h2>
    <!-- 余白なしでスライド幅いっぱいに表示 -->
    <img src="24_Keras予測_改善後.png" class="full-bleed-image">
</section>

---
<section class="top-center">
    <h2>学習年「2022-2024」モデルKeras（3年で劇的向上）</h2>
    <!-- 余白なしでスライド幅いっぱいに表示 -->
    <img src="22-24_Keras.png" class="full-bleed-image">
</section>
