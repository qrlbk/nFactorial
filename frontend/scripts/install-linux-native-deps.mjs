/**
 * Vercel/Linux CI: npm often skips optional platform packages (npm/cli#4828).
 * Install Tailwind Oxide + Lightning CSS GNU binaries when missing.
 */
import { execSync } from "node:child_process";
import { existsSync } from "node:fs";
import { join } from "node:path";

const isLinux = process.platform === "linux";
if (!isLinux) {
  process.exit(0);
}

const arch = process.arch === "arm64" ? "arm64" : "x64";
const libc = "gnu";

const packages = [
  `@tailwindcss/oxide-linux-${arch}-${libc}@4.3.0`,
  `lightningcss-linux-${arch}-${libc}@1.32.0`,
];

const oxideDir = join(
  process.cwd(),
  "node_modules",
  "@tailwindcss",
  "oxide",
);

for (const pkg of packages) {
  try {
    execSync(`npm install --no-save --no-package-lock ${pkg}`, {
      stdio: "inherit",
    });
  } catch (error) {
    console.warn(`[postinstall] optional install failed for ${pkg}:`, error);
  }
}

if (!existsSync(join(oxideDir, "node_modules"))) {
  console.warn(
    "[postinstall] @tailwindcss/oxide native binding may still be missing",
  );
}
