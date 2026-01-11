import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "portadesbd.diba.cat",
      },
    ],
  },
};

export default nextConfig;
