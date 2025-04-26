"use client"

import type React from "react"

import { createTheme, ThemeProvider } from "@mui/material/styles"
import CssBaseline from "@mui/material/CssBaseline"
import { useTheme } from "next-themes"
import { useMemo } from "react"
import { ThemeProvider as StyledComponentsThemeProvider } from "styled-components"

export function AppThemeProvider({ children }: { children: React.ReactNode }) {
  const { resolvedTheme } = useTheme()
  const isDark = resolvedTheme === "dark"

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode: isDark ? "dark" : "light",
          primary: {
            main: "#6366F1", // Modern indigo
            light: "#818CF8",
            dark: "#4F46E5",
          },
          secondary: {
            main: "#EC4899", // Modern pink
            light: "#F472B6",
            dark: "#DB2777",
          },
          background: {
            default: isDark ? "#111827" : "#F9FAFB",
            paper: isDark ? "#1F2937" : "#FFFFFF",
          },
          text: {
            primary: isDark ? "#F9FAFB" : "#111827",
            secondary: isDark ? "#D1D5DB" : "#6B7280",
          },
          error: {
            main: "#EF4444",
          },
          warning: {
            main: "#F59E0B",
          },
          info: {
            main: "#3B82F6",
          },
          success: {
            main: "#10B981",
          },
        },
        typography: {
          fontFamily: "Inter, system-ui, sans-serif",
          h1: {
            fontWeight: 700,
            letterSpacing: "-0.025em",
          },
          h2: {
            fontWeight: 700,
            letterSpacing: "-0.025em",
          },
          h3: {
            fontWeight: 600,
            letterSpacing: "-0.025em",
          },
          h4: {
            fontWeight: 600,
            letterSpacing: "-0.025em",
          },
          h5: {
            fontWeight: 600,
          },
          h6: {
            fontWeight: 600,
          },
          button: {
            textTransform: "none",
            fontWeight: 500,
          },
          body1: {
            lineHeight: 1.6,
          },
          body2: {
            lineHeight: 1.6,
          },
        },
        shape: {
          borderRadius: 12,
        },
        components: {
          MuiButton: {
            styleOverrides: {
              root: {
                borderRadius: 8,
                padding: "10px 20px",
                boxShadow: "none",
                "&:hover": {
                  boxShadow: isDark ? "0 4px 12px rgba(0, 0, 0, 0.25)" : "0 4px 12px rgba(0, 0, 0, 0.1)",
                },
              },
              contained: {
                "&:hover": {
                  transform: "translateY(-1px)",
                },
              },
            },
          },
          MuiCard: {
            styleOverrides: {
              root: {
                borderRadius: 16,
                boxShadow: isDark ? "0 4px 20px rgba(0, 0, 0, 0.4)" : "0 4px 20px rgba(0, 0, 0, 0.08)",
                overflow: "hidden",
                transition: "transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out",
                "&:hover": {
                  boxShadow: isDark ? "0 8px 30px rgba(0, 0, 0, 0.5)" : "0 8px 30px rgba(0, 0, 0, 0.12)",
                },
              },
            },
          },
          MuiPaper: {
            styleOverrides: {
              root: {
                borderRadius: 12,
              },
            },
          },
          MuiTextField: {
            styleOverrides: {
              root: {
                "& .MuiOutlinedInput-root": {
                  borderRadius: 8,
                },
              },
            },
          },
          MuiAppBar: {
            styleOverrides: {
              root: {
                boxShadow: isDark ? "0 1px 3px rgba(0, 0, 0, 0.3)" : "0 1px 3px rgba(0, 0, 0, 0.1)",
                backdropFilter: "blur(8px)",
                backgroundColor: isDark ? "rgba(31, 41, 55, 0.8)" : "rgba(255, 255, 255, 0.8)",
              },
            },
          },
          MuiAvatar: {
            styleOverrides: {
              root: {
                boxShadow: isDark ? "0 2px 4px rgba(0, 0, 0, 0.3)" : "0 2px 4px rgba(0, 0, 0, 0.1)",
              },
            },
          },
          MuiListItem: {
            styleOverrides: {
              root: {
                borderRadius: 8,
              },
            },
          },
          MuiListItemButton: {
            styleOverrides: {
              root: {
                borderRadius: 8,
              },
            },
          },
        },
      }),
    [isDark],
  )

  return (
    <ThemeProvider theme={theme}>
      <StyledComponentsThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </StyledComponentsThemeProvider>
    </ThemeProvider>
  )
}
