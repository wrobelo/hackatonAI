"use client"

import type React from "react"
import { useEffect, useState, useRef } from "react"
import { useRouter } from "next/navigation"
import { styled } from "styled-components"
import {
  Box,
  Typography,
  Button,
  Container,
  Paper,
  CircularProgress,
  TextField,
  Avatar,
  Card,
  CardContent,
  useTheme,
} from "@mui/material"
import { Send } from "lucide-react"
import Header from "@/components/header"
import {ProfileChat} from "@/app/[pageId]/profile-creation/ProfileChat";
import {Stack} from "@mui/system";

// Define a proper type for the message objects
interface ChatMessage {
  id: number
  isUser: boolean
  text: string
}

const StyledContainer = styled(Container)`
  padding: 2rem;
  max-width: 1000px;
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
`

const LoadingContainer = styled(Box)`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  flex: 1;
  
  h5 {
    margin-bottom: 1rem;
    background: linear-gradient(to right, #6366F1, #EC4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
`

const ChatContainer = styled(Box)`
  display: flex;
  flex-direction: column;
  flex: 1;
  //overflow: hidden;
`

const MessagesContainer = styled(Box)`
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
`

const MessageInputContainer = styled(Box)`
  padding: 1rem;
  display: flex;
  gap: 1rem;
  align-items: center;
`

const ProfileSummaryCard = styled(Card)`
  margin-top: 1.5rem;
  margin-bottom: 1.5rem;
  border-radius: 16px;
  //overflow: hidden;
  
  pre {
    font-family: inherit;
  }
`


// Mock loading messages
const loadingMessages = [
  "Analyzing your Facebook page content...",
  "Learning about your brand voice...",
  "Identifying key themes and patterns...",
  "Extracting brand personality traits...",
  "Almost there! Finalizing your profile...",
]

// Mock AI conversation
const mockConversation = [
  {
    id: 1,
    isUser: false,
    text: "Hi there! I'm your Brand Hero AI assistant. I've analyzed your Facebook page 'Coffee Shop Delights' and I'd like to ask a few questions to better understand your brand. What makes your coffee shop unique compared to others in your area?",
  },
  {
    id: 2,
    isUser: true,
    text: "We focus on locally sourced ingredients and have a cozy atmosphere with live music on weekends.",
  },
  {
    id: 3,
    isUser: false,
    text: "That sounds wonderful! Do you have any signature drinks or menu items that your customers particularly love?",
  },
  {
    id: 4,
    isUser: true,
    text: "Yes, our lavender honey latte and homemade cinnamon rolls are customer favorites.",
  },
  {
    id: 5,
    isUser: false,
    text: "Great! How would you describe the atmosphere or vibe you're trying to create in your coffee shop?",
  },
  {
    id: 6,
    isUser: true,
    text: "We aim for a warm, welcoming space where people can relax, work, or connect with friends. We have lots of plants and natural light.",
  },
  {
    id: 7,
    isUser: false,
    text: "Based on our conversation and your Facebook page content, here's a summary of your brand profile:",
  },
]

// Mock profile summary for new profiles
const mockProfileSummary = `
**Coffee Shop Delights - Brand Profile**

**Brand Voice:** Warm, friendly, and inviting with a touch of creativity. Communication style is conversational and approachable, focusing on community and quality.

**Core Values:** Sustainability, local sourcing, community connection, and craftsmanship in coffee and food preparation.

**Unique Selling Points:** 
- Locally sourced ingredients
- Cozy atmosphere with live music on weekends
- Signature lavender honey latte and homemade cinnamon rolls
- Warm, plant-filled space ideal for relaxation or work

**Target Audience:** Local community members, remote workers, students, and coffee enthusiasts who value quality, sustainability, and a welcoming atmosphere.

**Content Themes:** Coffee craftsmanship, local community events, sustainability practices, seasonal menu items, and creating connections.
`

const ProfileCreationPage = ({ params }: { params: { pageId: string } }) => {
  const [stage, setStage] = useState<"loading" | "chat" | "summary">("loading")
  const [loadingMessage, setLoadingMessage] = useState(loadingMessages[0])
  const [profileSummary, setProfileSummary] = useState("")
  const [showSummary, setShowSummary] = useState(false)
  const [isEditMode, setIsEditMode] = useState(false)
  const router = useRouter()

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem("fb_access_token")
    if (!token) {
      router.push("/")
      return
    }

    // Check if we're in edit mode (profile already exists)
    const existingProfile = localStorage.getItem("company_profile")
    if (existingProfile) {
      setIsEditMode(true)
      setProfileSummary(existingProfile)
      setShowSummary(true)
    }

    // Simulate loading process
    let messageIndex = 0
    const interval = setInterval(() => {
      messageIndex = (messageIndex + 1) % loadingMessages.length
      setLoadingMessage(loadingMessages[messageIndex])
    }, 3000)

    // After loading, start the chat
    const timeout = setTimeout(() => {
      clearInterval(interval)
      setStage("chat")
    }, 6000)

    return () => {
      clearInterval(interval)
      clearTimeout(timeout)
    }
  }, [router])


  const handleConfirmProfile = () => {
    // Save profile to localStorage (in a real app, this would be saved to a database)
    localStorage.setItem("company_profile", profileSummary)

    // If in edit mode, go back to dashboard, otherwise continue to brand hero creation
    if (isEditMode) {
      router.push(`/${params.pageId}/dashboard`)
    } else {
      router.push(`/${params.pageId}/brand-hero-creation`)
    }
  }

  const handleCancel = () => {
    // Only available in edit mode - go back to dashboard
    router.push(`/${params.pageId}/dashboard`)
  }

  return (
    <>
      <Header />
      <StyledContainer>
        {stage === "loading" ? (
          <LoadingContainer>
            <CircularProgress size={60} sx={{ mb: 4 }} />
            <Typography variant="h5" gutterBottom>
              {loadingMessage}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              This may take a moment as we analyze your Facebook page
            </Typography>
          </LoadingContainer>
        ) : (
          <ChatContainer sx={{height: "100%"}}>
            <Typography variant="h5" gutterBottom>
              {isEditMode ? "Editing Your Company Profile" : "Creating Your Company Profile"}
            </Typography>

            <Stack direction="row" spacing={2} sx={{ mb: 2, flexGrow: 1, height: "100%" }}>
              {showSummary && (
                  <ProfileSummaryCard sx={{ flexBasis: "50%"}}>
                    <CardContent sx={{height: "100%"}}>
                      <Stack direction="column" spacing={2} justifyContent="stretch" sx={{height: "100%"}}>
                        <Typography variant="h6" gutterBottom>
                          Your Brand Profile
                        </Typography>
                        <Typography variant="body2" component="pre" sx={{ whiteSpace: "pre-wrap", overflowY: "auto", flex: '1 1 0' }}>
                          {profileSummary}
                        </Typography>
                        <Box sx={{ mt: 2, display: "flex", justifyContent: "flex-end", gap: 2 }}>
                          {isEditMode && (
                              <Button variant="outlined" color="inherit" onClick={handleCancel}>
                                Cancel
                              </Button>
                          )}
                          <Button variant="contained" color="primary" onClick={handleConfirmProfile}>
                            {isEditMode ? "Save Changes" : "Confirm Profile & Continue"}
                          </Button>
                        </Box>
                      </Stack>
                    </CardContent>
                  </ProfileSummaryCard>
              )}

              <Box sx={{flex: 1, flexBasis: "50%"}}>
                <ProfileChat/>
              </Box>

            </Stack>


          </ChatContainer>
        )}
      </StyledContainer>
    </>
  )
}

export default ProfileCreationPage
