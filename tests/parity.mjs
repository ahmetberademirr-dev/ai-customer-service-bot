// Proves the browser bot (docs/bot.js) behaves exactly like the Python bot.
//   node tests/parity.mjs
// 1. Same topic and language as Python on every training and test sentence
//    (probabilities within 0.01).
// 2. Every conversation in tests/scenarios.json passes.

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { createBot } from "../docs/bot.js";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const load = (p) => JSON.parse(readFileSync(join(root, p), "utf-8"));

const bot = createBot(load("docs/model.json"), load("docs/data.json"));
const failures = [];

// 1. Prediction parity
const expected = load("tests/expected_predictions.json");
for (const e of expected) {
  const [intent, conf] = bot.predictIntent(e.text);
  const [lang, langConf] = bot.predictLanguage(e.text);
  if (intent !== e.intent || Math.abs(conf - e.confidence) > 0.01)
    failures.push(`intent "${e.text}": python ${e.intent} ${e.confidence}, js ${intent} ${conf}`);
  if (lang !== e.language || Math.abs(langConf - e.language_confidence) > 0.01)
    failures.push(`language "${e.text}": python ${e.language} ${e.language_confidence}, js ${lang} ${langConf}`);
}

// 2. Scenario parity
const scenarios = load("tests/scenarios.json");
for (const s of scenarios) {
  bot.reset();
  for (const turn of s.turns) {
    const message = turn.say ?? turn.say_repeat[0].repeat(turn.say_repeat[1]);
    const r = bot.handleMessage("TEST", message, turn.default_lang ?? null);
    const x = turn.expect;
    for (const f of ["intent", "outcome", "priority", "language"])
      if (f in x && r[f] !== x[f]) failures.push(`[${s.name}] ${f}: expected ${x[f]}, got ${r[f]}`);
    for (const t of x.reply_contains ?? [])
      if (!r.reply.includes(t)) failures.push(`[${s.name}] reply missing "${t}": ${r.reply}`);
    if ("message_length" in x && Array.from(r.message).length !== x.message_length)
      failures.push(`[${s.name}] message length ${Array.from(r.message).length}`);
  }
}

if (failures.length) {
  console.error(`PARITY FAILED (${failures.length})\n` + failures.slice(0, 30).join("\n"));
  process.exit(1);
}
console.log(`parity ok: ${expected.length} predictions, ${scenarios.length} scenarios`);
