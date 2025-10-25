// FAQ Chatbot
// - faq.json を読み込み、ユーザー入力とFAQを簡易スコアリングでマッチング
// - 最上位回答を返し、必要に応じて関連質問も提案

const FAQ_URL = "faq.json";
let FAQ_DATA = [];

// 文字正規化（NFKC, lower, 記号除去）
function normalize(text = "") {
  return String(text)
    .normalize("NFKC")
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\s]/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
}

// トークン化：スペースがなければバイグラムで近似
function tokenize(text) {
  const t = normalize(text);
  if (!t) return [];
  if (t.includes(" ")) {
    return t.split(" ");
  }
  // 日本語等の連続文字対策：バイグラム
  const grams = [];
  for (let i = 0; i < t.length - 1; i++) {
    grams.push(t.slice(i, i + 2));
  }
  return grams.length ? grams : [t];
}

// Jaccard類似度（集合）
function jaccard(aTokens, bTokens) {
  const A = new Set(aTokens);
  const B = new Set(bTokens);
  if (A.size === 0 && B.size === 0) return 0;
  let inter = 0;
  for (const x of A) if (B.has(x)) inter++;
  const union = A.size + B.size - inter;
  return union ? inter / union : 0;
}

// 包含ブースト（部分一致）
function includesBoost(query, target) {
  if (!query || !target) return 0;
  const q = normalize(query);
  const t = normalize(target);
  if (!q || !t) return 0;
  if (t.includes(q)) return 1;        // ターゲットにクエリが含まれる
  if (q.includes(t)) return 0.6;      // クエリにターゲットが含まれる
  return 0;
}

// FAQスコアリング：質問＋回答を対象に評価
function scoreFAQ(query, item) {
  const corpus = `${item.question} ${item.answer}`;
  const qTokens = tokenize(query);
  const cTokens = tokenize(corpus);
  const j = jaccard(qTokens, cTokens);             // 0..1
  const incQ = includesBoost(query, item.question);
  const incA = includesBoost(query, item.answer);
  // 重み付け：質問に寄せる
  const score = 0.65 * j + 0.25 * incQ + 0.10 * incA;
  return Math.min(1, score);
}

// ベストマッチ上位N件を返す（しきい値あり）
function getBestMatches(query, topN = 3, threshold = 0.18) {
  const ranked = FAQ_DATA
    .map((it) => ({ ...it, _score: scoreFAQ(query, it) }))
    .sort((a, b) => b._score - a._score)
    .filter((x) => x._score >= threshold)
    .slice(0, topN);
  return ranked;
}

// UI: メッセージ追加
function addMessage(text, role = "bot") {
  const messages = document.getElementById("messages");
  const bubble = document.createElement("div");
  bubble.className = `msg ${role === "user" ? "msg--user" : "msg--bot"}`;
  bubble.textContent = text;
  messages.appendChild(bubble);
  messages.scrollTop = messages.scrollHeight;
  return bubble;
}

// UI: ローディングバブル
function addLoading() {
  const messages = document.getElementById("messages");
  const wrap = document.createElement("div");
  wrap.className = "msg msg--bot";
  wrap.innerHTML = `
    <span class="loading">
      <span class="loading__dot"></span>
      <span class="loading__dot"></span>
      <span class="loading__dot"></span>
    </span>
  `;
  messages.appendChild(wrap);
  messages.scrollTop = messages.scrollHeight;
  return wrap;
}

// 応答生成
function generateResponse(query) {
  const matches = getBestMatches(query, 3);
  if (matches.length === 0) {
    const suggestions = FAQ_DATA.slice(0, 5).map((x) => `・${x.question}`).join("\n");
    return `該当する回答が見つかりませんでした。キーワードを変えてお試しください。\n\n参考:\n${suggestions}`;
  }
  const best = matches[0];
  let reply = best.answer;
  if (matches.length > 1) {
    const related = matches.slice(1).map((m) => `・${m.question}`).join("\n");
    reply += `\n\n関連する質問:\n${related}`;
  }
  return reply;
}

// 送信処理
function handleSend(e) {
  e.preventDefault();
  const input = document.getElementById("user-input");
  const text = input.value.trim();
  if (!text) return;
  addMessage(text, "user");
  input.value = "";

  const loading = addLoading();
  // 疑似ディレイでローディング感
  setTimeout(() => {
    loading.remove();
    const reply = generateResponse(text);
    addMessage(reply, "bot");
  }, 220);
}

// 初期化
async function init() {
  // FAQ読み込み
  const res = await fetch(FAQ_URL, { cache: "no-store" });
  if (!res.ok) {
    addMessage("FAQデータの読み込みに失敗しました。管理者に連絡してください。", "bot");
    return;
  }
  FAQ_DATA = await res.json();

  // ウェルカムメッセージ
  addMessage("こんにちは。社員ポータルのFAQチャットボットです。ご質問を入力してください。", "bot");

  // イベント
  const form = document.getElementById("chat-form");
  form.addEventListener("submit", handleSend);
}

window.addEventListener("DOMContentLoaded", init);
