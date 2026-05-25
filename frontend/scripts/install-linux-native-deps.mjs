/**
 * Vercel/Linux CI: npm often skips optional platform packages (npm/cli#4828).
 * @see https://github.com/tailwindlabs/tailwindcss/issues/15806
 */
import { execSync } from "node:child_process";
import { createRequire } from "node:module";

if (process.platform !== "linux") {
  process.exit(0);
}

const arch = process.arch === "arm64" ? "arm64" : "x64";
const require = createRequire(import.meta.url);

function hasBinding() {
  try {
    require("@tailwindcss/oxide");
    return true;
  } catch {
    return false;
  }
}

if (hasBinding()) {
  process.exit(0);
}

const packages = [
  `@tailwindcss/oxide-linux-${arch}-gnu@4.3.0`,
  `lightningcss-linux-${arch}-gnu@1.32.0`,
].join(" ");

console.log("[postinstall] Installing Linux native bindings:", packages);
execSync(`npm install --no-save --no-package-lock ${packages}`, {
  stdio: "inherit",
});

if (!hasBinding()) {
  console.warn("[postinstall] @tailwindcss/oxide still not loadable after install");
  process.exit(0);
}
