"use client"

import type React from "react"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { styled } from "styled-components"
import {
    Box,
    Typography,
    Container,
    CircularProgress,
} from "@mui/material"
import Header from "@/components/header"


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



// Mock loading messages
const loadingMessages = [
    "Analyzing your Facebook page content...",
    "Learning about your brand voice...",
    "Identifying key themes and patterns...",
    "Extracting brand personality traits...",
    "Almost there! Finalizing your profile...",
]

const ScrapingPage = ({ params }: { params: { pageId: string } }) => {
    const [loadingMessage, setLoadingMessage] = useState(loadingMessages[0])
    const router = useRouter()

    useEffect(() => {

        // Simulate loading process
        let messageIndex = 0
        const interval = setInterval(() => {
            messageIndex = (messageIndex + 1) % loadingMessages.length
            setLoadingMessage(loadingMessages[messageIndex])
        }, 3000)

        // After loading, start the chat
        const timeout = setTimeout(() => {
            clearInterval(interval)
            router.push(`/${params.pageId}/profile-creation`)
        }, 6000)

        return () => {
            clearInterval(interval)
            clearTimeout(timeout)
        }
    }, [router])


    return (
        <>
        <Header />
        <StyledContainer>
                    <LoadingContainer>
                        <CircularProgress size={60} sx={{ mb: 4 }} />
                        <Typography variant="h5" gutterBottom>
                            {loadingMessage}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                            {'This may take a moment as we analyze your Facebook page'}
                        </Typography>
                    </LoadingContainer>

            </StyledContainer>
        </>
    )
}

export default ScrapingPage
