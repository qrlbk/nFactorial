#!/usr/bin/env node
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const messagesDir = join(__dirname, "..", "messages");

const LOCALES = ["en", "ru", "kk"];

/** Keys or dotted paths allowed to match English in ru/kk (proper nouns, brands). */
const ALLOW_SAME_AS_EN = new Set([
  "metadata.title",
  "brand.title",
  "brand.subtitle",
  "profile.name",
  "profile.plan",
  "modes.contrarian-vc.label",
  "modes.paul-graham.label",
  "modes.research-analyst.label",
  "dashboard.traceId",
  "settings.apiBase",
  "settings.tracing",
  "settings.tracingLangfuse",
  "journey.timeline",
  "pipeline.detail.critic_slop",
  "dashboard.contextPlaceholder",
]);

function flatten(obj, prefix = "") {
  /** @type {Record<string, string>} */
  const out = {};
  for (const [key, value] of Object.entries(obj)) {
    const path = prefix ? `${prefix}.${key}` : key;
    if (value && typeof value === "object" && !Array.isArray(value)) {
      Object.assign(out, flatten(value, path));
    } else {
      out[path] = String(value);
    }
  }
  return out;
}

function loadLocale(locale) {
  const raw = readFileSync(join(messagesDir, `${locale}.json`), "utf8");
  return flatten(JSON.parse(raw));
}

const en = loadLocale("en");
const enKeys = Object.keys(en).sort();

let failed = false;

for (const locale of ["ru", "kk"]) {
  const target = loadLocale(locale);
  const targetKeys = new Set(Object.keys(target));

  const missing = enKeys.filter((key) => !targetKeys.has(key));
  if (missing.length > 0) {
    failed = true;
    console.error(`[${locale}] Missing ${missing.length} key(s):`);
    missing.forEach((key) => console.error(`  - ${key}`));
  }

  const extra = [...targetKeys].filter((key) => !enKeys.includes(key));
  if (extra.length > 0) {
    failed = true;
    console.error(`[${locale}] Extra ${extra.length} key(s) not in en.json:`);
    extra.forEach((key) => console.error(`  - ${key}`));
  }

  const untranslated = enKeys.filter(
    (key) =>
      target[key] === en[key] &&
      !ALLOW_SAME_AS_EN.has(key) &&
      /^[A-Za-z]/.test(en[key]),
  );

  if (untranslated.length > 0) {
    failed = true;
    console.error(`[${locale}] ${untranslated.length} value(s) still match English:`);
    untranslated.forEach((key) => console.error(`  - ${key}: "${en[key]}"`));
  }
}

if (failed) {
  console.error("\ni18n parity check failed.");
  process.exit(1);
}

console.log(`i18n parity OK (${enKeys.length} keys × ${LOCALES.length} locales)`);
