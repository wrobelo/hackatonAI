import type React from "react"
import { Inter } from "next/font/google"
import { ThemeProvider } from "@/components/theme-provider"
import StyledComponentsRegistry from "@/lib/styled-components-registry"
import { AppThemeProvider } from "@/components/app-theme-provider"
import "./globals.css"
import { AuthProvider } from "@/auth";

const inter = Inter({ subsets: ["latin"] })

export const metadata = {
  title: "Brand Hero",
  description: "AI-powered Facebook page management for small businesses",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
      <AuthProvider>
        <ThemeProvider attribute="class" defaultTheme="light" enableSystem disableTransitionOnChange>
          <StyledComponentsRegistry>
            <AppThemeProvider>{children}</AppThemeProvider>
          </StyledComponentsRegistry>
        </ThemeProvider>
      </AuthProvider>
      </body>
    </html>
  )
}
