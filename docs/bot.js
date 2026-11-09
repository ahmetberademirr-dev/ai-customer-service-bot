// Browser (and Node) port of src/classifier.py + src/bot.py.
//
// The weights come from docs/model.json and the store rules from docs/data.json,
// both produced by `python export_model.py`. tests/parity.mjs checks that this
// file makes the same predictions and decisions as the Python bot.

export function createBot(model, data) {
  const RULES = data.rules;
  const FOLD = RULES.tr_fold;
  const ORDER_INTENTS = new Set(RULES.order_intents);
  const URGENT = new Set(RULES.urgent_words);
  const FILLER = new Set(RULES.filler_words);

  // ---------------------------------------------------------------- features
  function normalize(text) {
    let t = Array.from(text, (ch) => (ch in FOLD ? FOLD[ch] : ch)).join("").toLowerCase();
    t = t.replace(/[0-9]+/g, " 0 ").replace(/[^a-z0 ]+/g, " ");
    return t.replace(/\s+/g, " ").trim();
  }

  function wordNgrams(text, [minN, maxN]) {
    const tokens = text.match(/[a-z0]+/g) || [];
    const out = [];
    for (let n = minN; n <= Math.min(maxN, tokens.length); n++) {
      for (let i = 0; i + n <= tokens.length; i++) out.push(tokens.slice(i, i + n).join(" "));
    }
    return out;
  }

  // Same as scikit-learn's _char_wb_ngrams: n-grams inside space-padded words.
  function charWbNgrams(text, [minN, maxN]) {
    const out = [];
    for (const word of text.replace(/\s\s+/g, " ").split(/\s+/).filter(Boolean)) {
      const w = Array.from(" " + word + " ");
      for (let n = minN; n <= maxN; n++) {
        let offset = 0;
        out.push(w.slice(offset, offset + n).join(""));
        while (offset + n < w.length) {
          offset += 1;
          out.push(w.slice(offset, offset + n).join(""));
        }
        if (offset === 0) break; // short word: counted once
      }
    }
    return out;
  }

  function prepare(spec, offset) {
    const index = new Map(spec.vocab.map((term, i) => [term, i]));
    return { ...spec, index, offset };
  }

  function prepareModel(m, preprocess) {
    let offset = 0;
    const vectorizers = m.vectorizers.map((spec) => {
      const v = prepare(spec, offset);
      offset += spec.vocab.length;
      return v;
    });
    return { ...m, vectorizers, preprocess };
  }

  const intentModel = prepareModel(model.intent, normalize);
  const languageModel = prepareModel(model.language, (t) => t.toLowerCase());

  // TF-IDF per vectorizer (each L2-normalised), concatenated -> sparse map.
  function featurize(m, text) {
    const pre = m.preprocess(text);
    const features = new Map();
    for (const v of m.vectorizers) {
      const grams = v.analyzer === "word" ? wordNgrams(pre, v.ngram_range) : charWbNgrams(pre, v.ngram_range);
      const counts = new Map();
      for (const g of grams) {
        const i = v.index.get(g);
        if (i !== undefined) counts.set(i, (counts.get(i) || 0) + 1);
      }
      let norm = 0;
      const values = [];
      for (const [i, c] of counts) {
        const tf = v.sublinear_tf ? 1 + Math.log(c) : c;
        const value = tf * v.idf[i];
        values.push([i, value]);
        norm += value * value;
      }
      norm = Math.sqrt(norm) || 1;
      for (const [i, value] of values) features.set(v.offset + i, value / norm);
    }
    return features;
  }

  const round3 = (x) => Math.round(x * 1000) / 1000;

  function predict(m, text) {
    const x = featurize(m, text);
    const scores = m.coef.map((row, c) => {
      let s = m.intercept[c];
      for (const [j, value] of x) s += value * row[j];
      return s;
    });
    let probs;
    if (m.classes.length === 2) {
      const p1 = 1 / (1 + Math.exp(-scores[0]));
      probs = [1 - p1, p1];
    } else {
      const max = Math.max(...scores);
      const exps = scores.map((s) => Math.exp(s - max));
      const sum = exps.reduce((a, b) => a + b, 0);
      probs = exps.map((e) => e / sum);
    }
    let best = 0;
    probs.forEach((p, i) => { if (p > probs[best]) best = i; });
    return [m.classes[best], round3(probs[best])];
  }

  const predictIntent = (text) => predict(intentModel, text);
  const predictLanguage = (text) => predict(languageModel, text);

  // ------------------------------------------------------------ conversation
  const extractOrderId = (message) => {
    const m = message.match(/(?<!\d)(\d{6})(?!\d)/);
    return m ? m[1] : null;
  };
  const isMostlyOrderNumber = (message) =>
    normalize(message).split(" ").filter((w) => w && w !== "0").every((w) => FILLER.has(w));

  let orders, sessions, tickets;
  function reset() {
    orders = new Map(data.orders.map((o) => [o.order_id, { ...o }]));
    sessions = new Map();
    tickets = [];
  }
  reset();

  const orderHandlers = {
    order_status(o, f) {
      if (o.status === "preparing") return ["status_preparing", "answered"];
      if (o.status === "shipped") {
        if (o.eta_in_days < 0) { f.days = -o.eta_in_days; return ["status_delayed", "escalated"]; }
        return ["status_shipped", "answered"];
      }
      if (o.status === "delivered") return ["status_delivered", "answered"];
      return ["status_cancelled", "answered"];
    },
    cancel_order(o) {
      if (o.status === "preparing") { o.status = "cancelled"; return ["cancel_ok", "answered"]; }
      if (o.status === "shipped") return ["cancel_shipped", "answered"];
      if (o.status === "delivered") return ["cancel_delivered", "answered"];
      return ["cancel_already", "answered"];
    },
    return_refund(o, f) {
      if (o.status === "delivered") {
        if (o.delivered_days_ago <= RULES.return_window_days) { f.code = `RET-${o.order_id}`; return ["return_ok", "answered"]; }
        return ["return_expired", "escalated"];
      }
      if (o.status === "cancelled") return ["status_cancelled", "answered"];
      return ["return_not_delivered", "answered"];
    },
    change_address(o) {
      if (o.status === "preparing") return ["address_ok", "answered"];
      if (o.status === "shipped") return ["address_too_late", "escalated"];
      if (o.status === "delivered") return ["status_delivered", "answered"];
      return ["address_cancelled", "answered"];
    },
  };

  function act(intent, session, lang) {
    if (!ORDER_INTENTS.has(intent)) {
      session.pending = null;
      const [key, outcome] = RULES.simple_intents[intent];
      return [key, outcome, {}];
    }
    const orderId = session.last_order;
    if (!orderId) { session.pending = intent; return ["ask_order_id", "asked_info", {}]; }
    const order = orders.get(orderId);
    if (!order) {
      session.pending = intent;
      session.last_order = null;
      return ["order_not_found", "asked_info", { order_id: orderId }];
    }
    session.pending = null;
    const fields = {
      order_id: orderId,
      item: order[`item_${lang}`],
      carrier: order.carrier,
      eta: Math.max(order.eta_in_days || 1, 1),
      days: order.delivered_days_ago,
    };
    const [key, outcome] = orderHandlers[intent](order, fields);
    return [key, outcome, fields];
  }

  function priorityOf(message, intent, key, outcome) {
    const words = normalize(message).split(" ");
    if (intent === "payment_issue" || key === "status_delayed" || words.some((w) => URGENT.has(w))) return "high";
    return outcome === "escalated" ? "medium" : "low";
  }

  function handleMessage(customerId, rawMessage, defaultLang = null) {
    const message = Array.from(rawMessage).slice(0, RULES.max_message_length).join("");
    if (!sessions.has(customerId)) sessions.set(customerId, { lang: null, pending: null, last_order: null, misses: 0 });
    const session = sessions.get(customerId);

    const orderId = extractOrderId(message);
    if (orderId) session.last_order = orderId;
    let [intent, confidence] = predictIntent(message);

    if (orderId && (isMostlyOrderNumber(message) || confidence < RULES.threshold)) {
      intent = session.pending || "order_status";
      confidence = 1.0;
    }

    // Short replies ("ok") and gibberish say nothing reliable about language.
    let [lang, langConfidence] = predictLanguage(message);
    const unclear = langConfidence < RULES.language_confidence || confidence < RULES.threshold;
    if (unclear && (session.lang || defaultLang)) lang = session.lang || defaultLang;
    session.lang = lang;

    let key, outcome, fields;
    if (confidence < RULES.threshold) {
      session.misses += 1;
      if (session.misses >= 2) { session.misses = 0; [key, outcome, fields] = ["clarify_escalate", "escalated", {}]; }
      else [key, outcome, fields] = ["clarify", "clarify", {}];
    } else {
      session.misses = 0;
      [key, outcome, fields] = act(intent, session, lang);
    }

    const priority = priorityOf(message, intent, key, outcome);
    const reply = data.replies[key][lang].replace(/\{(\w+)\}/g, (_, k) => String(fields[k]));
    const ticket = {
      ticket_id: tickets.length + 1, customer_id: customerId, message, language: lang, intent,
      confidence, outcome, priority, order_id: fields.order_id || null, reply,
      escalated: outcome === "escalated",
    };
    tickets.push(ticket);
    return ticket;
  }

  return {
    handleMessage, reset, normalize, predictIntent, predictLanguage,
    get tickets() { return tickets; },
    getOrder: (id) => orders.get(id),
  };
}
