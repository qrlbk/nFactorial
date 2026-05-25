import type { NextConfig } from "next";
import path from "path";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

/** Backend origin for /api rewrites — set API_URL on Vercel (e.g. https://your-api.onrender.com). */
const apiOrigin = (process.env.API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

// App directory is always frontend/ (Vercel Root Directory should be `frontend` or build runs from frontend).
const appDir = path.resolve(__dirname);

const nextConfig: NextConfig = {
  outputFileTracingRoot: appDir,
  turbopack: {
    root: appDir,
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
