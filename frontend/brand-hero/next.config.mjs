/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  experimental: {
    proxyTimeout: 1000000,
  },
  rewrites: async () => [
    {
      source: "/api/company-context/:path*",
      destination: "http://localhost:8070/api/company-context/:path*",
    },
    {
      source: "/api/brand-hero-context/:path*",
      destination: "http://localhost:8070/api/brand-hero-context/:path*",
    },
    {
      source: "/api/images/:path*",
      destination: "http://localhost:8070/api/images/:path*",
    },
    {
      source: "/api/strategy/:path*",
      destination: "http://localhost:8070/api/strategy/:path*",
    }
  ]
}

export default nextConfig
