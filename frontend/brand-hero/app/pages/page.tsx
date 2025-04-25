"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { styled } from "styled-components"
import {
  Box,
  Typography,
  Button,
  Container,
  Paper,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  CircularProgress,
  Divider,
} from "@mui/material"
import { RefreshCw } from "lucide-react"
import Header from "@/components/header"

const StyledContainer = styled(Container)`
  padding: 2rem;
  max-width: 800px;
`

const StyledPaper = styled(Paper)`
  padding: 2rem;
  margin-top: 2rem;
  border-radius: 16px;
  overflow: hidden;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
`

const EmptyStateContainer = styled(Box)`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 4rem 1rem;
  text-align: center;
`

// Mock data for Facebook pages
const mockPages = [
  { id: "1", name: "Coffee Shop Delights", category: "Coffee Shop" },
  { id: "2", name: "Tech Gadgets Store", category: "Retail" },
  { id: "3", name: "Yoga with Sarah", category: "Fitness" },
]

const PageSelectionPage = () => {
  const [pages, setPages] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem("fb_access_token")
    if (!token) {
      router.push("/")
      return
    }

    // Fetch pages (mock implementation)
    const fetchPages = async () => {
      try {
        // Simulate API call delay
        await new Promise((resolve) => setTimeout(resolve, 1500))

        // Set mock data
        setPages(mockPages)
      } catch (error) {
        console.error("Failed to fetch pages:", error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchPages()
  }, [router])

  const handleRefresh = async () => {
    setIsLoading(true)

    // Simulate refresh
    await new Promise((resolve) => setTimeout(resolve, 1500))

    // Set mock data again (in a real app, this would re-fetch from API)
    setPages(mockPages)
    setIsLoading(false)
  }

  const handlePageSelect = (pageId: string) => {
    // Redirect to profile creation
    router.push(`/${pageId}/profile-creation`)
  }

  return (
    <>
      <Header />
      <StyledContainer>
        <Typography variant="h4" component="h1" gutterBottom>
          Select a Facebook Page
        </Typography>
        <Typography variant="body1" color="textSecondary" paragraph>
          Choose a Facebook page you manage to get started with Brand Hero
        </Typography>

        <StyledPaper>
          {isLoading ? (
            <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
              <CircularProgress />
            </Box>
          ) : pages.length > 0 ? (
            <List>
              {pages.map((page, index) => (
                <Box key={page.id}>
                  {index > 0 && <Divider />}
                  <ListItem disablePadding>
                    <ListItemButton onClick={() => handlePageSelect(page.id)}>
                      <ListItemText primary={page.name} secondary={page.category} />
                    </ListItemButton>
                  </ListItem>
                </Box>
              ))}
            </List>
          ) : (
            <EmptyStateContainer>
              <Typography variant="h6" gutterBottom>
                No Facebook Pages Found
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                You don't seem to manage any Facebook pages yet. To use Brand Hero, you'll need to create a Facebook
                page first.
              </Typography>
              <Typography variant="body2" paragraph sx={{ mb: 3 }}>
                Visit{" "}
                <a href="https://www.facebook.com/pages/create" target="_blank" rel="noopener noreferrer">
                  Facebook Pages
                </a>{" "}
                to create a new page, then come back here.
              </Typography>
              <Button variant="outlined" startIcon={<RefreshCw size={18} />} onClick={handleRefresh}>
                Refresh Page List
              </Button>
            </EmptyStateContainer>
          )}
        </StyledPaper>
      </StyledContainer>
    </>
  )
}

export default PageSelectionPage
