"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { styled } from "styled-components"
import { AppBar, Toolbar, Typography, IconButton, Menu, MenuItem, Box, useTheme } from "@mui/material"
import { MenuIcon, LogOut, Sun, Moon } from "lucide-react"
import { useTheme as useNextTheme } from "next-themes"

const StyledAppBar = styled(AppBar)`
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(8px);
  background-color: ${(props) =>
    props.theme.palette.mode === "dark" ? "rgba(31, 41, 55, 0.8)" : "rgba(255, 255, 255, 0.8)"};
  border-bottom: 1px solid ${(props) =>
    props.theme.palette.mode === "dark" ? "rgba(255, 255, 255, 0.05)" : "rgba(0, 0, 0, 0.05)"};
`

const Header = () => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const router = useRouter()
  const theme = useTheme()
  const { setTheme, resolvedTheme } = useNextTheme()

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleMenuClose = () => {
    setAnchorEl(null)
  }

  const handleLogout = () => {
    // Clear local storage
    localStorage.removeItem("fb_access_token")

    // Redirect to login page
    router.push("/")
    handleMenuClose()
  }

  const toggleTheme = () => {
    setTheme(resolvedTheme === "dark" ? "light" : "dark")
    handleMenuClose()
  }

  return (
    <StyledAppBar position="static" color="default">
      <Toolbar>
        <Typography
          variant="h6"
          component="div"
          sx={{
            flexGrow: 1,
            fontWeight: "bold",
            background: "linear-gradient(to right, #6366F1, #EC4899)",
            backgroundClip: "text",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            display: "inline-block",
          }}
        >
          Brand Hero
        </Typography>

        <IconButton size="large" edge="end" color="inherit" aria-label="menu" onClick={handleMenuOpen}>
          <MenuIcon />
        </IconButton>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          anchorOrigin={{
            vertical: "bottom",
            horizontal: "right",
          }}
          transformOrigin={{
            vertical: "top",
            horizontal: "right",
          }}
        >
          <MenuItem onClick={toggleTheme}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              {resolvedTheme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
              {resolvedTheme === "dark" ? "Light Mode" : "Dark Mode"}
            </Box>
          </MenuItem>
          <MenuItem onClick={handleLogout}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <LogOut size={18} />
              Logout
            </Box>
          </MenuItem>
        </Menu>
      </Toolbar>
    </StyledAppBar>
  )
}

export default Header
