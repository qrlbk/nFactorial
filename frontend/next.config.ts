import type { NextConfig } from "next";
import { existsSync } from "fs";
import path from "path";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

/** Backend origin for /api rewrites — set API_URL on Vercel (e.g. https://your-api.onrender.com). */
const apiOrigin = (process.env.API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

function resolveNextRoot(): string {
  const appDir = process.cwd();
  const parent = path.resolve(appDir, "..");
  if (existsSync(path.join(parent, "node_modules", "next"))) {
    return parent;
  }
  return appDir;
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
