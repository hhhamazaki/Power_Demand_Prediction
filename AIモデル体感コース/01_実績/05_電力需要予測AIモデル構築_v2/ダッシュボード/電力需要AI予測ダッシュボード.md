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
    <h2>学習年「2024」全モデル共通「学習データ処理」実行中</h2>
    <!-- 余白なしでスライド幅いっぱいに表示 -->
    <img src="RandomForestデータ処理.png" class="full-bleed-image">
</section>

---
<section class="top-center">
    <h2>学習年「2024」モデルPyCaret「学習」実行中</h2>
    <!-- 余白なしでスライド幅いっぱいに表示 -->
    <img src="PyCaret学習.png" class="full-bleed-image">
</section>

---
<section class="top-center">
    <h2>全モデル共通「予測データ取得」実行中</h2>
    <!-- 余白なしでスライド幅いっぱいに表示 -->
    <img src="LightGBMデータ取得.png" class="full-bleed-image">
</section>

---
<section class="top-center">
    <h2>モデルKeras「予測」実行中　⇒　精度悪化の要因分析</h2>
    <!-- 余白なしでスライド幅いっぱいに表示 -->
    <img src="Keras予測.png" class="full-bleed-image">
</section>
