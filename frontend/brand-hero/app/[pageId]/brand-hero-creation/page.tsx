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
  TextField,
  Avatar,
  Card,
  CardContent,
  Grid,
  useTheme,
} from "@mui/material"
import { Send, Save } from "lucide-react"
import Header from "@/components/header"

// Define a proper type for the message objects
interface ChatMessage {
  id: number
  isUser: boolean
  text: string
}

const StyledContainer = styled(Container)`
  padding: 2rem;
  max-width: 1200px;
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
`

const ContentContainer = styled(Box)`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`

const ChatImageContainer = styled(Grid)`
  flex: 1;
  overflow: hidden;
`

const ChatContainer = styled(Box)`
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
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

const ImagePreviewContainer = styled(Box)`
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 1rem;
`

const ImageCard = styled(Card)`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: 16px;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
`

const ImageContent = styled(CardContent)`
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background-color: ${(props) =>
    props.theme.palette.mode === "dark" ? "rgba(17, 24, 39, 0.4)" : "rgba(249, 250, 251, 0.4)"};
`

const Message = styled(Box)<{ isUser: boolean }>`
  max-width: 80%;
  align-self: ${(props) => (props.isUser ? "flex-end" : "flex-start")};
  display: flex;
  gap: 0.5rem;
`

// Use inline styles for MessageContent instead of accessing theme directly in styled-components
const MessageContent = styled(Paper)<{ isUser: boolean; bgcolor: string; textcolor: string }>`
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  background-color: ${(props) => props.bgcolor};
  color: ${(props) => props.textcolor};
  box-shadow: ${(props) =>
    props.isUser
      ? "0 2px 8px rgba(99, 102, 241, 0.2)"
      : props.theme.palette.mode === "dark"
        ? "0 2px 8px rgba(0, 0, 0, 0.2)"
        : "0 2px 8px rgba(0, 0, 0, 0.05)"};
`

// Mock AI conversation
const mockConversation = [
  {
    id: 1,
    isUser: false,
    text: "Based on your company profile, I'm going to create a brand hero character for Coffee Shop Delights. What kind of personality would you like your brand hero to have?",
  },
  {
    id: 2,
    isUser: true,
    text: "I'd like a friendly, approachable character who embodies our warm and welcoming atmosphere.",
  },
  {
    id: 3,
    isUser: false,
    text: "Great! Would you prefer a male, female, or non-binary character? Or perhaps a mascot-style character?",
  },
  {
    id: 4,
    isUser: true,
    text: "I think a female character would work well for our brand.",
  },
  {
    id: 5,
    isUser: false,
    text: "I've created an initial brand hero character. What do you think? We can make adjustments based on your feedback.",
  },
]

// Mock brand hero images
const mockBrandHeroImages = [
  "/placeholder.svg?height=400&width=400",
  "/placeholder.svg?height=400&width=400",
  "/placeholder.svg?height=400&width=400",
]

const BrandHeroCreationPage = ({ params: {pageId} }: { params: { pageId: string } }) => {
  // Update the state type
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState("")
  const [currentImageIndex, setCurrentImageIndex] = useState(0)
  const [isEditMode, setIsEditMode] = useState(false)
  const messagesEndRef = useRef<null | HTMLDivElement>(null)
  const router = useRouter()
  const theme = useTheme() // Get MUI theme

  useEffect(() => {
    // Check if user is logged in and has a company profile
    const token = localStorage.getItem("fb_access_token")
    const profile = localStorage.getItem("company_profile")
    const heroImage = localStorage.getItem("brand_hero_image")

    if (!token) {
      router.push("/")
      return
    }

    if (!profile) {
      router.push(`/${pageId}/profile-creation`)
      return
    }

    // Check if we're in edit mode (brand hero already exists)
    if (heroImage) {
      setIsEditMode(true)
      // Find the index of the existing hero image in our mock images
      const index = mockBrandHeroImages.indexOf(heroImage)
      if (index !== -1) {
        setCurrentImageIndex(index)
      }

      // Initialize chat with edit mode message
      setMessages([
        {
          id: 1,
          isUser: false,
          text: "Let's make some adjustments to your brand hero character. What would you like to change?",
        },
      ])
    } else {
      // Initialize chat with first message for new creation
      setMessages([mockConversation[0]])
    }
  }, [router, pageId])

  useEffect(() => {
    // Scroll to bottom when messages change
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSendMessage = () => {
    if (!inputValue.trim()) return

    const userMessage = {
      id: Date.now(),
      isUser: true,
      text: inputValue.trim(),
    }

    // Add the user message
    setMessages((prev) => [...prev, userMessage])
    setInputValue("")

    // Simulate AI response
    setTimeout(() => {
      // Use functional update to get the latest messages state
      setMessages((currentMessages) => {
        const currentMessageCount = currentMessages.length

        // If in edit mode, provide custom responses
        if (isEditMode) {
          // Update image after user message
          setCurrentImageIndex((prevIndex) => (prevIndex + 1) % mockBrandHeroImages.length)

          return [
            ...currentMessages,
            {
              id: Date.now(),
              isUser: false,
              text: "I've updated the character based on your feedback. What do you think of this version?",
            },
          ]
        }

        // Regular flow for new brand hero creation
        const messageIndex = Math.floor(currentMessageCount / 2)

        if (messageIndex + 1 < mockConversation.length) {
          // Add the next AI message
          const nextAiMessage = mockConversation[messageIndex + 1]

          // Update image after specific messages
          if (messageIndex + 1 >= 4) {
            setCurrentImageIndex((prevIndex) => Math.min(prevIndex + 1, mockBrandHeroImages.length - 1))
          }

          return [...currentMessages, nextAiMessage]
        }

        return currentMessages
      })
    }, 1000)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleSaveBrandHero = () => {
    // Save brand hero to localStorage (in a real app, this would be saved to a database)
    localStorage.setItem("brand_hero_image", mockBrandHeroImages[currentImageIndex])

    // Redirect to dashboard
    router.push(`/${pageId}/dashboard`)
  }

  const handleCancel = () => {
    // Only available in edit mode - go back to dashboard without saving changes
    router.push(`/${pageId}/dashboard`)
  }

  return (
    <>
      <Header />
      <StyledContainer>
        <Typography variant="h5" gutterBottom>
          {isEditMode ? "Editing Your Brand Hero" : "Creating Your Brand Hero"}
        </Typography>

        <ContentContainer>
          <ChatImageContainer container spacing={3}>
            <Grid item xs={12} md={7}>
              <ChatContainer>
                {/* Update the MessagesContainer section to add null checks */}
                <MessagesContainer>
                  {Array.isArray(messages) &&
                    messages.map((message) => {
                      // Skip rendering if message is undefined
                      if (!message) return null

                      return (
                        <Message key={message.id} isUser={Boolean(message.isUser)}>
                          {!message.isUser && <Avatar sx={{ bgcolor: "primary.main" }}>AI</Avatar>}
                          <MessageContent
                            isUser={Boolean(message.isUser)}
                            bgcolor={message.isUser ? theme.palette.primary.main : theme.palette.background.paper}
                            textcolor={message.isUser ? "#fff" : theme.palette.text.primary}
                          >
                            <Typography variant="body2">{message.text}</Typography>
                          </MessageContent>
                        </Message>
                      )
                    })}
                  <div ref={messagesEndRef} />
                </MessagesContainer>

                <MessageInputContainer>
                  <TextField
                    fullWidth
                    placeholder="Type your message..."
                    variant="outlined"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    multiline
                    maxRows={4}
                  />
                  <Button variant="contained" color="primary" onClick={handleSendMessage} disabled={!inputValue.trim()}>
                    <Send size={20} />
                  </Button>
                </MessageInputContainer>
              </ChatContainer>
            </Grid>

            <Grid item xs={12} md={5}>
              <ImagePreviewContainer>
                <ImageCard>
                  <CardContent sx={{ p: 2 }}>
                    <Typography variant="h6">Brand Hero Preview</Typography>
                  </CardContent>
                  <ImageContent>
                    <Box
                      component="img"
                      src={mockBrandHeroImages[currentImageIndex] || "/placeholder.svg"}
                      alt="Brand Hero Character"
                      sx={{
                        maxWidth: "100%",
                        maxHeight: "100%",
                        objectFit: "contain",
                      }}
                    />
                  </ImageContent>
                  <CardContent sx={{ p: 2, display: "flex", gap: 2 }}>
                    {isEditMode && (
                      <Button variant="outlined" color="inherit" fullWidth onClick={handleCancel}>
                        Cancel
                      </Button>
                    )}
                    <Button
                      variant="contained"
                      color="primary"
                      fullWidth
                      startIcon={<Save size={18} />}
                      onClick={handleSaveBrandHero}
                    >
                      {isEditMode ? "Save Changes" : "Save Brand Hero"}
                    </Button>
                  </CardContent>
                </ImageCard>
              </ImagePreviewContainer>
            </Grid>
          </ChatImageContainer>
        </ContentContainer>
      </StyledContainer>
    </>
  )
}

export default BrandHeroCreationPage
