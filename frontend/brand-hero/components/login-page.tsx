"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { styled } from "styled-components"
import { Box, Typography, Button, Container, Paper, useTheme } from "@mui/material"
import { Facebook } from "lucide-react"

const StyledContainer = styled(Container)`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
`

const StyledPaper = styled(Paper)`
  padding: 3rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 500px;
  width: 100%;
  border-radius: 24px;
  background: ${(props) =>
    props.theme.palette.mode === "dark"
      ? "linear-gradient(145deg, rgba(31, 41, 55, 0.7), rgba(17, 24, 39, 0.9))"
      : "linear-gradient(145deg, rgba(255, 255, 255, 0.9), rgba(249, 250, 251, 0.9))"};
  backdrop-filter: blur(10px);
  border: 1px solid ${(props) =>
    props.theme.palette.mode === "dark" ? "rgba(255, 255, 255, 0.05)" : "rgba(255, 255, 255, 0.5)"};
`

const LogoContainer = styled.div`
  margin-bottom: 2.5rem;
  text-align: center;
  
  h1 {
    background: linear-gradient(to right, #6366F1, #EC4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
  }
`

const LoginPage = () => {
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const theme = useTheme()

  const handleFacebookLogin = async () => {
    setIsLoading(true)

    // In a real implementation, you would redirect to Facebook OAuth
    // For now, we'll simulate the login process
    try {
      // Simulate API call delay
      await new Promise((resolve) => setTimeout(resolve, 1500))

      // Store a mock token in localStorage
      localStorage.setItem("fb_access_token", "mock_token_123")

      // Redirect to page selection
      router.push("/pages")
    } catch (error) {
      console.error("Login failed:", error)
      setIsLoading(false)
    }
  }

  return (
    <StyledContainer>
      <StyledPaper elevation={3}>
        <LogoContainer>
          <Typography variant="h3" component="h1" gutterBottom fontWeight="bold">
            Brand Hero
          </Typography>
          <Typography variant="body1" color="textSecondary" paragraph>
            AI-powered Facebook page management for small businesses
          </Typography>
        </LogoContainer>

        <Box sx={{ width: "100%", mb: 4 }}>
          <Typography variant="h6" gutterBottom align="center">
            Welcome to Brand Hero
          </Typography>
          <Typography variant="body2" paragraph align="center" color="textSecondary">
            Connect your Facebook account to get started with AI-powered page management
          </Typography>
        </Box>

        <Button
          variant="contained"
          color="primary"
          size="large"
          startIcon={<Facebook />}
          onClick={handleFacebookLogin}
          disabled={isLoading}
          fullWidth
          sx={{
            backgroundColor: "#1877F2",
            "&:hover": {
              backgroundColor: "#166FE5",
              transform: "translateY(-2px)",
              boxShadow: "0 4px 12px rgba(24, 119, 242, 0.4)",
            },
            transition: "all 0.2s ease-in-out",
          }}
        >
          {isLoading ? "Connecting..." : "Continue with Facebook"}
        </Button>
      </StyledPaper>
    </StyledContainer>
  )
}

export default LoginPage
