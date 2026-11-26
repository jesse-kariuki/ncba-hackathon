import type { NextConfig } from "next";

// All /api/* calls are proxied to FastAPI, so the browser never needs CORS and the API URL lives in one place.
const API = process.env.LEAKLENS_API_URL || "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  eslint: { ignoreDuringBuilds: true },
  devIndicators: false,
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${API}/api/:path*` }];
  },
};

export default nextConfig;
