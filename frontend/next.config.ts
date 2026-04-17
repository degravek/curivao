import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "*.supabase.co",
        pathname: "/storage/v1/object/public/**",
      },
      // Allow any https image during development/POC
      {
        protocol: "https",
        hostname: "**",
      },
    ],
  },
};

export default nextConfig;
