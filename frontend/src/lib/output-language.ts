export type OutputLanguage = "en" | "ru" | "kk";

export const OUTPUT_LANG_KEY = "editorial-output-lang";

export function getOutputLanguage(): OutputLanguage {
  if (typeof window === "undefined") return "en";
  const stored = localStorage.getItem(OUTPUT_LANG_KEY);
  if (stored === "ru" || stored === "kk" || stored === "en") return stored;
  return "en";
}

export function setOutputLanguage(lang: OutputLanguage) {
  localStorage.setItem(OUTPUT_LANG_KEY, lang);
}
