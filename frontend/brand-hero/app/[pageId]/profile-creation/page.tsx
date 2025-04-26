"use client"

import type React from "react"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { styled } from "styled-components"
import {
  Box,
  Typography,
  Button,
  Container,
  CircularProgress,
  Card,
  CardContent,
} from "@mui/material"
import Header from "@/components/header"
import {ProfileChat} from "@/app/[pageId]/profile-creation/ProfileChat";
import {Stack} from "@mui/system";
import {
  useQuery,
} from '@tanstack/react-query'
import axios from "axios";


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

const ProfileCreationPage = ({ params }: { params: { pageId: string } }) => {
  const [stage, setStage] = useState<"loading" | "chat" | "summary">("loading")
  const [loadingMessage, setLoadingMessage] = useState(loadingMessages[0])
  const [profileSummary, setProfileSummary] = useState("")
  const [isEditMode, setIsEditMode] = useState(false)
  const router = useRouter()

  const { isPending, error, data } = useQuery({
    queryKey: ['get.company-context'],
    queryFn: async () =>
        await axios.get<{
          company_id: string;
          context_description: string;
        }>(`/api/company-context/${params.pageId}`),
  })

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
              {data?.data.context_description && (
                  <ProfileSummaryCard sx={{ flexBasis: "50%"}}>
                    <CardContent sx={{height: "100%"}}>
                      <Stack direction="column" spacing={2} justifyContent="stretch" sx={{height: "100%"}}>
                        <Typography variant="h6" gutterBottom>
                          Your Brand Profile
                        </Typography>
                        <Typography variant="body2" component="pre" sx={{ whiteSpace: "pre-wrap", overflowY: "auto", flex: '1 1 0' }}>
                          {data?.data.context_description}
                        </Typography>
                        <Box sx={{ mt: 2, display: "flex", justifyContent: "flex-end", gap: 2 }}>
                          <Button variant="contained" color="primary" onClick={handleConfirmProfile}>
                            Continue
                          </Button>
                        </Box>
                      </Stack>
                    </CardContent>
                  </ProfileSummaryCard>
              )}

              <Box sx={{flex: 1, flexBasis: "50%"}}>
                <ProfileChat pageId={params.pageId}/>
              </Box>

            </Stack>


          </ChatContainer>
        )}
      </StyledContainer>
    </>
  )
}

export default ProfileCreationPage
