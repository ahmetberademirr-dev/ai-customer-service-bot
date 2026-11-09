import { createBot } from "./bot.js";

// ------------------------------------------------------------------ texts
const T = {
  tr: {
    nav_demo: "Canlı deneme", nav_dashboard: "Yönetici paneli", nav_how: "Nasıl çalışır",
    eyebrow: "Operasyon + yapay zeka projesi",
    hero_title: "Destek ekibinin yükünü azaltan, ne zaman insana devredeceğini bilen müşteri hizmetleri botu",
    hero_lead: "Bir online mağazanın müşteri mesajlarını Türkçe ve İngilizce anlıyor, siparişe bakıp mağaza kurallarına göre cevap veriyor. Emin olmadığında tahmin yürütmüyor. Ödeme ve şikayet gibi hassas konuları önceliklendirip bir insana devrediyor.",
    stat_accuracy: "doğru konu tespiti (çapraz doğrulama)",
    stat_precision: "cevap verdiğinde doğruluk",
    stat_wrong: "yanlış konuda cevap",
    stat_cost: "çalışma maliyeti, tarayıcıda çalışır",
    cta_try: "Hemen dene", cta_dashboard: "Paneli gör",
    demo_title: "Canlı deneme",
    demo_lead: "Bir soru yazın ya da örneklerden birine tıklayın. Deneme siparişlerinin numaralarını kullanabilirsiniz. Her cevabın altında botun neden öyle davrandığı görünür.",
    chat_status: "Müşteri hizmetleri asistanı · TR / EN",
    reset: "Sıfırla", send: "Gönder",
    placeholder: "Mesajınızı yazın (örnek: Siparişim nerede?)",
    loading: "Model yükleniyor...",
    load_error: "Model yüklenemedi. Sayfayı yenilemeyi deneyin.",
    welcome: "Merhaba! Ben ShopNova'nın deneme asistanıyım. Sipariş takibi, iptal, iade, adres değişikliği, ödeme ve hesap konularında yardımcı olabilirim.",
    privacy: "Bot tamamen tarayıcınızda çalışır. Yazdıklarınız hiçbir sunucuya gönderilmez.",
    orders_title: "Deneme siparişleri",
    orders_lead: "Tıklayınca sipariş numarası mesaja eklenir.",
    legend_title: "Etiketler ne anlama geliyor?",
    legend: {
      answered: "Bot çözdü, insana gerek kalmadı",
      asked_info: "Eksik bilgiyi istedi, örneğin sipariş numarası",
      clarify: "Emin olmadığı için tahmin etmedi, tekrar sordu",
      escalated: "Kural gereği ya da hassas konu olduğu için insana devretti",
    },
    status: {
      preparing: "Hazırlanıyor",
      shipped: "Yolda, {eta} gün içinde",
      late: "Gecikmede ({days} gün)",
      delivered: "{days} gün önce teslim edildi",
      cancelled: "İptal edildi",
    },
    chips: ["Siparişim nerede?", "Siparişimi iptal etmek istiyorum", "Ürünü iade etmek istiyorum", "Kartımdan iki kez para çekildi", "Şifremi unuttum", "Temsilciyle görüşmek istiyorum", "Hava nasıl?"],
    dash_title: "Ekip lideri paneli",
    dash_lead: "Sayfa açıldığında botun hiç görmediği 120 örnek müşteri mesajı botun içinden geçirildi. Sohbetteki sizin mesajlarınız da anında buraya eklenir. Bu örnekte her konudan eşit sayıda mesaj var. Bu yüzden ödeme gibi her zaman insana giden konular gerçek hayattakinden fazla.",
    kpi_total: "Toplam mesaj", kpi_handled: "İnsansız çözülen", kpi_escalated: "İnsana devredilen",
    kpi_high: "Yüksek öncelikli", kpi_clarify: "Tekrar sorulan",
    topics_title: "En çok sorulan konular",
    queue_title: "İnsan kuyruğu",
    queue_lead: "Devredilen talepler, öncelik sırasıyla.",
    queue_empty: "Kuyruk boş.",
    calc_title: "Ekibe kazandırdığı zaman",
    calc_daily: "Günlük mesaj sayısı",
    calc_minutes: "Temsilcinin mesaj başına dakikası",
    calc_result: "Ayda yaklaşık <b>{hours}</b> saat, yani <b>{fte}</b> tam zamanlı temsilci kadar iş.",
    calc_formula: "{daily} mesaj × 30 gün × {rate} insansız çözüm × {min} dk",
    calc_note: "Varsayım: insansız çözülen oran paneldeki rakamdır. Ayda 160 çalışma saati 1 tam zamanlı kişi sayılır. Gerçek rakam mağazanın mesaj karışımına göre değişir.",
    how_title: "Nasıl çalışır?",
    how_lead: "Her müşteri mesajı aynı 4 adımdan geçer.",
    steps: [
      ["Anlar", "Mesajın dilini ve konusunu bulur, ne kadar emin olduğunu hesaplar. {examples} örnek cümleden öğrendi."],
      ["Kontrol eder", "Sipariş numarasını bulur, siparişin durumuna bakar ve mağaza kurallarını uygular. Kargodaki sipariş iptal edilmez, iade süresi 14 gün."],
      ["Karar verir", "Ya kendisi cevaplar, ya eksik bilgiyi sorar ya da insana devreder. Ödeme, gecikme ve öfkeli mesajlar öne alınır."],
      ["Kaydeder", "Her mesaj konu, karar ve öncelikle kaydedilir. Ekip lideri paneli bu kayıttan beslenir."],
    ],
    measure_title: "Nasıl ölçüldü?",
    measure_lead: "İki ayrı ölçüm yapıldı: botun hiç görmediği 120 soru ve eğitim verisi üzerinde 5 katlı çapraz doğrulama. Sayfanın üstünde daha temkinli olan ikinci rakam kullanılır.",
    measure_cols: ["", "Görülmemiş 120 soru", "Çapraz doğrulama"],
    measure_rows: {
      accuracy: "Doğru konu", answered: "Kendisi cevapladı", correct_when_answered: "Cevapladığında doğru",
      wrong: "Yanlış konuda cevap", rephrase: "Tekrar sordu",
    },
    measure_lang: "Dil tespiti (120 soru): {acc}",
    measure_link: "Ayrıntılı ölçüm raporu",
    decisions_title: "Tasarım kararları",
    decisions: [
      ["Para konuları asla otomatik çözülmez.", "Çift çekim, fatura, kupon gibi her ödeme konusu muhasebe ekibine yüksek öncelikle gider."],
      ["Emin değilse tahmin etmez.", "Emin olma oranı {threshold} altındaysa müşteriden açmasını ister. Yanlış cevap, tekrar sormaktan daha pahalıdır."],
      ["Müşteriyi döngüye sokmaz.", "Üst üste iki kez anlayamazsa konuşmayı bir insana devreder."],
      ["Sıfır maliyet, sıfır veri paylaşımı.", "Ücretli bir yapay zeka servisi kullanmaz. Tamamen tarayıcıda çalışır."],
      ["Her karar ölçülebilir.", "Her mesaj kaydedilir. Otomasyon oranı ve insan kuyruğu anlık izlenir."],
    ],
    footer_school: "İTÜ İşletme Mühendisliği",
    footer_credit: "Tasarım, iş kuralları ve ölçüm: Ahmet Bera Demir. Kod, yapay zeka desteğiyle (Claude Code) yazıldı.",
    intents: {
      greeting: "Selamlaşma", goodbye: "Vedalaşma", order_status: "Sipariş durumu", cancel_order: "İptal",
      return_refund: "İade", change_address: "Adres değişikliği", payment_issue: "Ödeme",
      account_help: "Hesap", human_agent: "Temsilci isteği", out_of_scope: "Konu dışı",
    },
    outcomes: { answered: "Bot çözdü", asked_info: "Bilgi istedi", clarify: "Tekrar sordu", escalated: "İnsana devretti" },
    priorities: { high: "Öncelik: yüksek", medium: "Öncelik: orta" },
    confidence: "Emin olma {p}",
    mine: "Sizin",
  },
  en: {
    nav_demo: "Live demo", nav_dashboard: "Dashboard", nav_how: "How it works",
    eyebrow: "Operations + AI project",
    hero_title: "A customer service bot that cuts the support team's workload and knows when to hand over",
    hero_lead: "It understands an online store's customer messages in Turkish and English, checks the order and answers by the store's rules. When it isn't sure, it doesn't guess. Sensitive cases like payments and complaints are prioritised and handed to a human.",
    stat_accuracy: "correct topic (cross-validation)",
    stat_precision: "correct when it answers",
    stat_wrong: "answers on the wrong topic",
    stat_cost: "running cost, runs in the browser",
    cta_try: "Try it now", cta_dashboard: "See the dashboard",
    demo_title: "Live demo",
    demo_lead: "Type a question or click an example. You can use the demo order numbers. Under every answer you can see why the bot acted the way it did.",
    chat_status: "Customer service assistant · TR / EN",
    reset: "Reset", send: "Send",
    placeholder: "Type a message (e.g. Where is my order?)",
    loading: "Loading model...",
    load_error: "The model couldn't be loaded. Try refreshing the page.",
    welcome: "Hi! I'm ShopNova's demo assistant. I can help with order tracking, cancellations, returns, address changes, payments and account issues.",
    privacy: "The bot runs entirely in your browser. Nothing you type is sent to a server.",
    orders_title: "Demo orders",
    orders_lead: "Click to add the order number to your message.",
    legend_title: "What do the tags mean?",
    legend: {
      answered: "Solved by the bot, no human needed",
      asked_info: "Asked for missing info, e.g. the order number",
      clarify: "Wasn't sure, so it asked instead of guessing",
      escalated: "Handed to a human by rule or because the case is sensitive",
    },
    status: {
      preparing: "Being prepared",
      shipped: "On the way, within {eta} days",
      late: "Late ({days} days)",
      delivered: "Delivered {days} days ago",
      cancelled: "Cancelled",
    },
    chips: ["Where is my order?", "I want to cancel my order", "I want to return an item", "I was charged twice", "I forgot my password", "I want to talk to a human", "What's the weather?"],
    dash_title: "Team lead dashboard",
    dash_lead: "When the page loaded, 120 sample customer messages the bot had never seen were run through it. Your own chat messages are added here instantly. The sample has the same number of messages for every topic, so topics that always go to a human, like payments, are over-represented compared with real traffic.",
    kpi_total: "Total messages", kpi_handled: "Handled without a human", kpi_escalated: "Handed to a human",
    kpi_high: "High priority", kpi_clarify: "Asked to rephrase",
    topics_title: "Most common topics",
    queue_title: "Human queue",
    queue_lead: "Handed-over requests, by priority.",
    queue_empty: "The queue is empty.",
    calc_title: "Time saved for the team",
    calc_daily: "Messages per day",
    calc_minutes: "Agent minutes per message",
    calc_result: "About <b>{hours}</b> hours a month, the work of <b>{fte}</b> full-time agents.",
    calc_formula: "{daily} messages × 30 days × {rate} handled without a human × {min} min",
    calc_note: "Assumption: the handled-without-a-human rate is the dashboard figure. 160 working hours a month count as one full-time person. Real numbers depend on the store's message mix.",
    how_title: "How it works",
    how_lead: "Every customer message goes through the same 4 steps.",
    steps: [
      ["Understand", "Detects the language and the topic, and how confident it is. Learned from {examples} example sentences."],
      ["Check", "Finds the order number, looks up the order and applies the store's rules. Shipped orders can't be cancelled, returns are open for 14 days."],
      ["Decide", "Either answers, asks for missing info, or hands over to a human. Payments, late orders and angry messages jump the queue."],
      ["Log", "Every message is stored with its topic, decision and priority. The team lead dashboard is built from this log."],
    ],
    measure_title: "How it was measured",
    measure_lead: "Two separate measurements: 120 questions the bot never saw, and 5-fold cross-validation on the training data. The more conservative second number is the one shown at the top of the page.",
    measure_cols: ["", "120 unseen questions", "Cross-validation"],
    measure_rows: {
      accuracy: "Correct topic", answered: "Answered on its own", correct_when_answered: "Correct when it answers",
      wrong: "Answered on the wrong topic", rephrase: "Asked to rephrase",
    },
    measure_lang: "Language detection (120 questions): {acc}",
    measure_link: "Full evaluation report",
    decisions_title: "Design decisions",
    decisions: [
      ["Money is never automated.", "Double charges, invoices, coupons: every payment issue goes to the billing team with high priority."],
      ["It doesn't guess.", "Below {threshold} confidence it asks the customer to rephrase. A wrong answer costs more than a second question."],
      ["No loops.", "After two misunderstandings in a row, the conversation goes to a human."],
      ["Zero cost, zero data sharing.", "No paid AI service. Everything runs in the browser."],
      ["Every decision is measurable.", "Every message is logged, so the automation rate and the human queue can be tracked live."],
    ],
    footer_school: "ITU Management Engineering",
    footer_credit: "Design, business rules and evaluation: Ahmet Bera Demir. Code written with AI assistance (Claude Code).",
    intents: {
      greeting: "Greeting", goodbye: "Goodbye", order_status: "Order status", cancel_order: "Cancellation",
      return_refund: "Return", change_address: "Address change", payment_issue: "Payment",
      account_help: "Account", human_agent: "Agent request", out_of_scope: "Off-topic",
    },
    outcomes: { answered: "Solved by bot", asked_info: "Asked for info", clarify: "Asked to rephrase", escalated: "Handed to human" },
    priorities: { high: "Priority: high", medium: "Priority: medium" },
    confidence: "Confidence {p}",
    mine: "Yours",
  },
};

const VISITOR = "VISITOR";
const PRIORITY_RANK = { high: 0, medium: 1, low: 2 };
const $ = (sel) => document.querySelector(sel);

let lang = pickLanguage();
let bot, simBot, metrics, data;
const chat = []; // {kind: "user"|"bot"|"welcome"|"system", text, ticket}

function pickLanguage() {
  const param = new URLSearchParams(location.search).get("lang");
  if (param === "tr" || param === "en") return param;
  try {
    const saved = localStorage.getItem("lang");
    if (saved === "tr" || saved === "en") return saved;
  } catch (_) { /* storage may be blocked */ }
  const nav = (navigator.language || "tr").toLowerCase();
  return nav.startsWith("tr") ? "tr" : "en";
}

const fill = (template, values) => template.replace(/\{(\w+)\}/g, (_, k) => values[k] ?? "");
const pct = (x, digits = 0) =>
  new Intl.NumberFormat(lang === "tr" ? "tr-TR" : "en-US", { style: "percent", maximumFractionDigits: digits }).format(x);
const num = (x, digits = 0) =>
  new Intl.NumberFormat(lang === "tr" ? "tr-TR" : "en-US", { maximumFractionDigits: digits }).format(x);

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") node.className = v;
    else if (k === "text") node.textContent = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v);
  }
  for (const c of children) if (c) node.append(c);
  return node;
}

// ----------------------------------------------------------------- render
function renderStatic() {
  const t = T[lang];
  document.documentElement.lang = lang;
  document.querySelectorAll("[data-i18n]").forEach((node) => { node.textContent = t[node.dataset.i18n]; });
  document.querySelectorAll(".lang-switch button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.lang === lang)));
  $("#message").placeholder = data ? t.placeholder : t.loading;

  $("#chips").replaceChildren(...t.chips.map((text) =>
    el("button", { type: "button", class: "chip", text, onclick: () => send(text) })));
  $("#legend").replaceChildren(...Object.entries(t.legend).map(([k, v]) =>
    el("li", {}, el("span", { class: `tag ${k}`, text: t.outcomes[k] }), el("span", { text: v }))));

  const stepIcons = [
    '<path d="M4 6h16v10H9l-5 4z"/>',
    '<path d="M3 7l9-4 9 4v10l-9 4-9-4z"/><path d="M3 7l9 4 9-4M12 11v10"/>',
    '<path d="M12 3v6M12 15v6M5 12H3M21 12h-2"/><circle cx="12" cy="12" r="3"/>',
    '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
  ];
  $("#steps").replaceChildren(...t.steps.map(([title, body], i) => {
    const li = el("li");
    li.innerHTML = `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${stepIcons[i]}</svg>`;
    li.append(el("h3", { text: title }), el("p", { text: fill(body, { examples: metrics ? num(metrics.train_examples) : "" }) }));
    return li;
  }));

  if (metrics) renderMetrics();
  if (data) { renderOrders(); renderChat(); renderDashboard(); }
}

function renderMetrics() {
  const t = T[lang];
  const cv = metrics.cross_validation;
  const stats = [
    [pct(cv.accuracy), t.stat_accuracy],
    [pct(cv.correct_when_answered), t.stat_precision],
    [pct(cv.wrong, 1), t.stat_wrong],
    [lang === "tr" ? "0 TL" : "$0", t.stat_cost],
  ];
  $("#hero-stats").replaceChildren(...stats.map(([b, s]) => el("li", {}, el("b", { text: b }), el("span", { text: s }))));

  const head = el("tr", {}, ...t.measure_cols.map((c) => el("th", { text: c })));
  const rows = Object.entries(t.measure_rows).map(([k, label]) => el("tr", {},
    el("td", { text: label }),
    el("td", { text: pct(metrics.test[k], 1) }),
    el("td", { text: pct(metrics.cross_validation[k], 1) })));
  const caption = el("caption", { class: "small muted", text: fill(t.measure_lang, { acc: pct(metrics.language_accuracy, 1) }) });
  caption.style.captionSide = "bottom";
  caption.style.textAlign = "left";
  caption.style.paddingTop = "8px";
  $("#measure").replaceChildren(caption, el("thead", {}, head), el("tbody", {}, ...rows));

  $("#decisions").replaceChildren(...t.decisions.map(([b, s]) =>
    el("li", {}, el("b", { text: b }), el("span", { text: fill(s, { threshold: pct(metrics.threshold) }) }))));
}

function orderStatus(o) {
  const s = T[lang].status;
  if (o.status === "shipped" && o.eta_in_days < 0) return fill(s.late, { days: -o.eta_in_days });
  return fill(s[o.status], { eta: Math.max(o.eta_in_days || 1, 1), days: o.delivered_days_ago });
}

function renderOrders() {
  $("#order-list").replaceChildren(...data.orders.map(({ order_id }) => {
    const o = bot.getOrder(order_id);
    return el("li", {}, el("button", {
      type: "button", class: "order", "aria-label": `${order_id}: ${o[`item_${lang}`]}`,
      onclick: () => {
        const input = $("#message");
        input.value = input.value.trim() ? `${input.value.trim()} ${order_id}` : order_id;
        input.focus();
      },
    }, el("code", { text: order_id }), el("span", { class: "item", text: o[`item_${lang}`] }),
      el("span", { class: "status", text: orderStatus(o) })));
  }));
}

function tagsFor(ticket, { mine = false } = {}) {
  const t = T[lang];
  const tags = [];
  if (mine) tags.push(el("span", { class: "tag mine", text: t.mine }));
  if (ticket.confidence >= data.rules.threshold) tags.push(el("span", { class: "tag", text: t.intents[ticket.intent] }));
  tags.push(el("span", { class: `tag ${ticket.outcome}`, text: t.outcomes[ticket.outcome] }));
  if (ticket.priority !== "low") tags.push(el("span", { class: `tag ${ticket.priority}`, text: t.priorities[ticket.priority] }));
  tags.push(el("span", { class: "tag", text: fill(t.confidence, { p: pct(ticket.confidence) }) }));
  return el("div", { class: "tags" }, ...tags);
}

function renderChat() {
  const log = $("#chat-log");
  log.replaceChildren(...chat.map((m) => {
    if (m.kind === "welcome") return el("div", { class: "msg bot" }, el("div", { class: "bubble", text: T[lang].welcome }));
    if (m.kind === "user") return el("div", { class: "msg user" }, el("div", { class: "bubble", text: m.text }));
    return el("div", { class: "msg bot" }, el("div", { class: "bubble", text: m.ticket.reply }), tagsFor(m.ticket));
  }));
  log.scrollTop = log.scrollHeight;
}

function renderDashboard() {
  const t = T[lang];
  const tickets = [...simBot.tickets, ...bot.tickets];
  const total = tickets.length;
  const count = (f) => tickets.filter(f).length;
  const escalated = count((x) => x.outcome === "escalated");
  const handled = total ? 1 - escalated / total : 0;

  const kpis = [
    [num(total), t.kpi_total, ""],
    [pct(handled), t.kpi_handled, "good"],
    [num(escalated), t.kpi_escalated, ""],
    [num(count((x) => x.priority === "high")), t.kpi_high, "warn"],
    [num(count((x) => x.outcome === "clarify")), t.kpi_clarify, ""],
  ];
  $("#kpis").replaceChildren(...kpis.map(([b, s, cls]) => el("div", { class: `kpi ${cls}` }, el("b", { text: b }), el("span", { text: s }))));

  const byTopic = {};
  for (const x of tickets) if (x.confidence >= data.rules.threshold) byTopic[x.intent] = (byTopic[x.intent] || 0) + 1;
  const sorted = Object.entries(byTopic).sort((a, b) => b[1] - a[1]);
  const max = sorted.length ? sorted[0][1] : 1;
  $("#topic-bars").replaceChildren(...sorted.map(([intent, n]) => {
    const fillBar = el("div", { class: "fill" });
    fillBar.style.width = `${(n / max) * 100}%`;
    return el("div", { class: "bar" }, el("span", { text: t.intents[intent] }), el("div", { class: "track" }, fillBar), el("span", { class: "n", text: num(n) }));
  }));

  const queue = tickets
    .map((x, i) => ({ ...x, order: i }))
    .filter((x) => x.outcome === "escalated")
    .sort((a, b) => PRIORITY_RANK[a.priority] - PRIORITY_RANK[b.priority] || b.order - a.order)
    .slice(0, 30);
  $("#queue").replaceChildren(...(queue.length
    ? queue.map((x) => el("li", {}, el("span", { class: "text", text: x.message }), tagsFor(x, { mine: x.customer_id === VISITOR })))
    : [el("li", { class: "muted small", text: t.queue_empty })]));

  renderCalc(handled);
}

let lastHandled = 0;
function renderCalc(handled = lastHandled) {
  lastHandled = handled;
  const t = T[lang];
  const daily = Math.max(0, Number($("#calc-daily").value) || 0);
  const minutes = Math.max(0, Number($("#calc-minutes").value) || 0);
  const hours = (daily * 30 * handled * minutes) / 60;
  const result = $("#calc-result");
  result.innerHTML = fill(t.calc_result, { hours: "{h}", fte: "{f}" })
    .replace("{h}", '<span id="h"></span>').replace("{f}", '<span id="f"></span>');
  result.querySelector("#h").textContent = num(hours);
  result.querySelector("#f").textContent = num(hours / 160, 1);
  $("#calc-formula").textContent = fill(t.calc_formula, { daily: num(daily), rate: pct(handled), min: num(minutes, 1) });
}

// ------------------------------------------------------------------- chat
function send(text) {
  const message = text.trim();
  if (!message || !bot) return;
  chat.push({ kind: "user", text: message });
  renderChat();
  $("#message").value = "";
  const ticket = bot.handleMessage(VISITOR, message, lang);
  setTimeout(() => {
    chat.push({ kind: "bot", ticket });
    renderChat();
    renderOrders();
    renderDashboard();
  }, 280);
}

function resetChat() {
  bot.reset();
  chat.length = 0;
  chat.push({ kind: "welcome" });
  renderOrders();
  renderChat();
  renderDashboard();
}

// ------------------------------------------------------------------ start
async function start() {
  renderStatic();
  document.querySelectorAll(".lang-switch button").forEach((b) => b.addEventListener("click", () => {
    lang = b.dataset.lang;
    try { localStorage.setItem("lang", lang); } catch (_) { /* ignore */ }
    renderStatic();
  }));
  $("#chat-form").addEventListener("submit", (e) => { e.preventDefault(); send($("#message").value); });
  $("#reset").addEventListener("click", resetChat);
  $("#calc-daily").addEventListener("input", () => renderCalc());
  $("#calc-minutes").addEventListener("input", () => renderCalc());

  try {
    const [model, d, m] = await Promise.all(
      ["model.json", "data.json", "metrics.json"].map((f) => fetch(f).then((r) => {
        if (!r.ok) throw new Error(`${f}: ${r.status}`);
        return r.json();
      })));
    data = d;
    metrics = m;
    bot = createBot(model, data);
    simBot = createBot(model, data);
    data.simulation.forEach((s, i) => simBot.handleMessage(`SIM-${i}`, s.text, s.lang));
    chat.push({ kind: "welcome" });
    $("#message").disabled = false;
    $("#send").disabled = false;
    renderStatic();
  } catch (err) {
    console.error(err);
    $("#chat-log").replaceChildren(el("div", { class: "msg system", text: T[lang].load_error }));
  }
}

start();
