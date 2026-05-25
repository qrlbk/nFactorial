/**
 * Vercel Git Integration + Next.js 16 + Root Directory `frontend`:
 * post-build validator looks for `/vercel/path0/.next/routes-manifest-deterministic.json`
 * instead of `frontend/.next/...`. Sync artifacts to repo root after `next build`.
 * @see https://github.com/vercel/vercel/issues/15937
 */
import { cpSync, existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const frontendDir = join(dirname(fileURLToPath(import.meta.url)), "..");
const appNext = join(frontendDir, ".next");
const rootNext = join(frontendDir, "..", ".next");
const rootManifest = join(rootNext, "routes-manifest-deterministic.json");

if (!existsSync(appNext)) {
  console.error("[vercel-postbuild] missing frontend/.next — run next build first");
  process.exit(1);
}

function writeDeterministicManifest(nextDir) {
  const manifestPath = join(nextDir, "routes-manifest.json");
  if (!existsSync(manifestPath)) {
    console.error(`[vercel-postbuild] missing ${manifestPath}`);
    process.exit(1);
  }
  const data = JSON.parse(readFileSync(manifestPath, "utf8"));
  data.headers = [];
  delete data.deploymentId;
  writeFileSync(
    join(nextDir, "routes-manifest-deterministic.json"),
    JSON.stringify(data),
  );
}

writeDeterministicManifest(appNext);
mkdirSync(rootNext, { recursive: true });
cpSync(appNext, rootNext, { recursive: true, force: true });
writeDeterministicManifest(rootNext);

if (!existsSync(rootManifest)) {
  console.error(`[vercel-postbuild] failed to create ${rootManifest}`);
  process.exit(1);
}

console.log(`[vercel-postbuild] OK → ${rootManifest}`);
