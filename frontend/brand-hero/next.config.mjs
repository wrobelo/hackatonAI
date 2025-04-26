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
  rewrites: async () => [
    {
      source: "/api/company-context/:path*",
      destination: "http://localhost:8070/api/company-context/:path*",
    }
  ]
}

export default nextConfig
