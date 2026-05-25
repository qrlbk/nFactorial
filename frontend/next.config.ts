import type { NextConfig } from "next";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

/** Backend origin for /api rewrites — set API_URL on Vercel (e.g. https://your-api.onrender.com). */
const apiOrigin = (process.env.API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

const frontendDir = path.dirname(fileURLToPath(import.meta.url));
const monorepoRoot = path.join(frontendDir, "..");

function resolveNextRoot(): string {
  if (fs.existsSync(path.join(frontendDir, "node_modules", "next"))) {
    return frontendDir;
  }
  if (fs.existsSync(path.join(monorepoRoot, "node_modules", "next"))) {
    return monorepoRoot;
  }
  return frontendDir;
}

const nextRoot = resolveNextRoot();

const nextConfig: NextConfig = {
  outputFileTracingRoot: nextRoot,
  turbopack: {
    root: nextRoot,
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${apiOrigin}/:path*`,
      },
    ];
  },
};

export default withNextIntl(nextConfig);
