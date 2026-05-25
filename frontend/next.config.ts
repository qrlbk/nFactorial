import type { NextConfig } from "next";
import path from "path";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

/** Backend origin for /api rewrites — set API_URL on Vercel (e.g. https://your-api.onrender.com). */
const apiOrigin = (process.env.API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

const nextConfig: NextConfig = {
  outputFileTracingRoot: path.join(process.cwd(), ".."),
  turbopack: {
    root: process.cwd(),
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
