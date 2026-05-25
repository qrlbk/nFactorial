import type { NextConfig } from "next";
import path from "path";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

/** Backend origin for /api rewrites — set API_URL on Vercel (e.g. https://your-api.onrender.com). */
const apiOrigin = (process.env.API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

// Monorepo: `npm run build --workspace=frontend` runs with cwd=frontend/, next hoisted to repo root.
const nextRoot =
  process.env.VERCEL === "1" || process.env.npm_lifecycle_event === "build"
    ? path.resolve(process.cwd(), "..")
    : process.cwd();

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
