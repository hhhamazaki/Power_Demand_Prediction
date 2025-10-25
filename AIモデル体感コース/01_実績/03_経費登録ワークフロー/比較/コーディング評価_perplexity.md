<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

### Claude Sonnet 4とGPT-5のコーディング性能評価の妥当性

**現状の主なベンチマーク結果**

- Claude Sonnet 4のSWE-bench Verified（GitHubの実課題修正ベンチマーク）スコアは**約72.7%**。[^1][^2][^3]
- GPT-5の同ベンチマークスコアは**74.9%**であり、Sonnet 4より若干高い数字。[^3][^4][^5]
- Aider Polyglot（多言語コード編集ベンチ）でもGPT-5は88%と最先端水準。[^4][^5]

**実務的な観点と補足**

- Claude Sonnet 4は速度・直接性・コスト効率に優れ、単純な修正や高速なイテレーションには強み。[^6]
- GPT-5は精度重視、複雑なリファクタやクロスファイル依存解決、大規模案件などでより信頼される傾向がある。[^4][^6]
- 実務ユーザーの体感評価は「好み」や「用途」により分かれ、どちらか一方が常に上回るとは言えない。[^6]

**結論**

- 現行の客観的ベンチマーク（SWE-benchなど）では、**GPT-5の方がSonnet 4よりコーディング性能が僅かに高い**のが事実です。[^5][^3][^4][^6]
- Sonnet 4の方が性能が高いという評価は現状の数値・業界比較からは**妥当ではありません**。
- ただし、速度重視・コスト重視・用途特化ではSonnet 4が選ばれる場面も多く、性能の「質」や「ターゲット」によって最適モデルを使い分けるべきです。[^3][^6]


#### 参考：主要ベンチマーク値比較表

| モデル | SWE-bench Verified | Aider Polyglot | 特記事項 |
| :-- | :-- | :-- | :-- |
| Claude Sonnet 4 | 約72.7%[^2][^1][^3] | 約77%[^7] | 高速・コスト効率 |
| GPT-5 | 74.9%[^4][^5][^3] | 88%[^4][^5] | 精度・クロスファイル・大規模対応 |

**妥当性まとめ**
Sonnet 4がGPT-5よりコーディング性能で高評価されるのは、現状の客観的ベンチマークおよび業界評価の観点から**妥当ではありません**。どちらもトップ性能だが、僅差で**GPT-5優位**です。用途別・ユーザー好みで使い分けるのが最適解です。

<div style="text-align: center">⁂</div>

[^1]: https://zenn.dev/saan/articles/265d063eb90f31

[^2]: https://blog.scuti.jp/claude-4-advanced-coding-reasoning-overview/

[^3]: https://blog.getbind.co/2025/08/04/openai-gpt-5-vs-claude-4-feature-comparison/

[^4]: https://openai.com/index/introducing-gpt-5-for-developers/

[^5]: https://www.vellum.ai/blog/gpt-5-benchmarks

[^6]: https://www.augmentcode.com/blog/gpt-5-is-here-and-we-now-have-a-model-picker

[^7]: https://www.qt.io/ja-jp/blog/improving-qml-coding-by-up-to-11-with-sonnet-4-qt-ai-assistant-0.9.3-released

[^8]: AImoteruBi-Jiao-Fen-Xi.html

[^9]: https://www.anthropic.com/news/claude-4

[^10]: https://dev.to/composiodev/claude-sonnet-4-vs-gemini-25-pro-coding-comparison-5787

[^11]: https://zenn.dev/shintaroamaike/articles/d5437c8afd54c4

[^12]: https://www.finalroundai.com/blog/openai-gpt-5-for-software-developers

[^13]: https://weel.co.jp/media/tech/claude-sonnet-4/

[^14]: https://www.reddit.com/r/ChatGPTCoding/comments/1mk93ti/gpt5_in_cline_is_making_me_think_sonnet4s/

[^15]: https://apidog.com/jp/blog/claude-4-sonnet-opus-vs-gpt-4-1-vs-gemini-2-5-pro-coding-jp/

[^16]: https://www.qodo.ai/blog/benchmarking-gpt-5-on-real-world-code-reviews-with-the-pr-benchmark/

[^17]: https://news.ycombinator.com/item?id=44827101

[^18]: https://forgecode.dev/blog/claude-sonnet-4-vs-gemini-2-5-pro-preview-coding-comparison/

[^19]: https://openai.com/index/introducing-gpt-5/

[^20]: https://news.ycombinator.com/item?id=44838303

[^21]: https://www.getpassionfruit.com/blog/chatgpt-5-vs-gpt-5-pro-vs-gpt-4o-vs-o3-performance-benchmark-comparison-recommendation-of-openai-s-2025-models

