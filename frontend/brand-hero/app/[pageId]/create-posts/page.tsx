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
  List,
  ListItem,
  Divider,
  IconButton,
  useTheme,
} from "@mui/material"
import { Send, Edit, Check, ArrowLeft } from "lucide-react"
import Header from "@/components/header"

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

const ContentContainer = styled(Box)`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`

const SuggestedPostsContainer = styled(Box)`
  margin-top: 1.5rem;
  
  h6 {
    margin-bottom: 1rem;
    position: relative;
    display: inline-block;
    
    &:after {
      content: '';
      position: absolute;
      bottom: -4px;
      left: 0;
      width: 40px;
      height: 3px;
      background: linear-gradient(to right, #6366F1, #EC4899);
      border-radius: 3px;
    }
  }
`

const PostItem = styled(ListItem)`
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 1rem;
`

const PostContent = styled(Box)`
  width: 100%;
`

const PostActions = styled(Box)`
  display: flex;
  justify-content: flex-end;
  width: 100%;
  margin-top: 1rem;
  gap: 0.5rem;
`

// Mock AI conversation
const mockConversation = [
  {
    id: 1,
    isUser: false,
    text: "Hi there! I'm ready to help you create some engaging posts for your Coffee Shop Delights Facebook page. What kind of posts would you like to create today?",
  },
  {
    id: 2,
    isUser: true,
    text: "I'd like to create some posts about our new summer menu items.",
  },
  {
    id: 3,
    isUser: false,
    text: "Great idea! Summer menu posts can drive a lot of engagement. Could you tell me a bit more about what's on your summer menu?",
  },
  {
    id: 4,
    isUser: true,
    text: "We have iced lavender matcha, strawberry cold brew, and a new vegan coconut pastry.",
  },
  {
    id: 5,
    isUser: false,
    text: "Those sound delicious! I'll create some post suggestions for your summer menu items. Would you like me to include your brand hero character in any of these posts?",
  },
  {
    id: 6,
    isUser: true,
    text: "Yes, please include the brand hero in at least one of the posts.",
  },
  {
    id: 7,
    isUser: false,
    text: "Perfect! I've created some post suggestions for your summer menu. You can review them below, make any edits, and approve them for scheduling.",
  },
]

// Mock suggested posts
const mockSuggestedPosts = [
  {
    id: 1,
    text: "☀️ Summer is here and so is our NEW menu! Cool down with our refreshing Iced Lavender Matcha - the perfect balance of earthy matcha and soothing lavender. Available now! #SummerSips #CoffeeShopDelights",
    scheduledDate: "2023-06-20",
    image: "/placeholder.svg?height=200&width=400",
    editing: false,
  },
  {
    id: 2,
    text: "Meet Bella, our Brand Hero, enjoying our NEW Strawberry Cold Brew! She knows the secret to beating the heat is this perfect blend of rich cold brew and sweet strawberry. Come try it today! #BrandHero #SummerTreats",
    scheduledDate: "2023-06-22",
    image: "/placeholder.svg?height=200&width=400",
    editing: false,
  },
  {
    id: 3,
    text: "Calling all our plant-based friends! Our NEW Vegan Coconut Pastry is a tropical dream come true. Flaky, sweet, and 100% vegan - pair it with any coffee for the perfect summer treat! #VeganTreats #SummerMenu",
    scheduledDate: "2023-06-25",
    image: null,
    editing: false,
  },
]

const CreatePostsPage = ({params}: { params: { pageId: string } }) => {
  // Update the state type
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState("")
  const [suggestedPosts, setSuggestedPosts] = useState<any[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const router = useRouter()

  useEffect(() => {
    // Initialize chat with first message
    setMessages([mockConversation[0]])
  }, [router])

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

        // Calculate which AI message to show next
        const messageIndex = Math.floor(currentMessageCount / 2)

        if (messageIndex + 1 < mockConversation.length) {
          // Add the next AI message
          const nextAiMessage = mockConversation[messageIndex + 1]

          // If this is the last AI message, show the suggested posts
          if (messageIndex + 1 === mockConversation.length - 1) {
            setSuggestedPosts(mockSuggestedPosts)
            setShowSuggestions(true)
          }

          return [...currentMessages, nextAiMessage]
        }

        return currentMessages
      })
    }, 1000)
  }


  const handleEditPost = (postId: number) => {
    setSuggestedPosts(suggestedPosts.map((post) => (post.id === postId ? { ...post, editing: true } : post)))
  }

  const handleSaveEdit = (postId: number, newText: string) => {
    setSuggestedPosts(
      suggestedPosts.map((post) => (post.id === postId ? { ...post, text: newText, editing: false } : post)),
    )
  }

  const handleApprovePost = (postId: number) => {
    // In a real app, this would save the post to a database
    setSuggestedPosts(suggestedPosts.map((post) => (post.id === postId ? { ...post, approved: true } : post)))
  }

  const handleBackToDashboard = () => {
    router.push(`/${params.pageId}/dashboard`)
  }

  return (
    <>
      <Header />
      <StyledContainer>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
          <IconButton onClick={handleBackToDashboard}>
            <ArrowLeft />
          </IconButton>
          <Typography variant="h5">Create Posts</Typography>
        </Box>

        <ContentContainer>


          {showSuggestions && (
            <SuggestedPostsContainer>
              <Typography variant="h6" gutterBottom>
                Suggested Posts
              </Typography>
              <Paper>
                <List>
                  {suggestedPosts.map((post, index) => (
                    <Box key={post.id}>
                      {index > 0 && <Divider />}
                      <PostItem>
                        <PostContent>
                          <Box sx={{ mb: 1 }}>
                            <Typography variant="body2" color="textSecondary">
                              Suggested publish date: {post.scheduledDate}
                            </Typography>
                          </Box>

                          {post.editing ? (
                            <TextField
                              fullWidth
                              multiline
                              variant="outlined"
                              defaultValue={post.text}
                              sx={{ mb: 2 }}
                              onBlur={(e) => handleSaveEdit(post.id, e.target.value)}
                            />
                          ) : (
                            <Typography variant="body1" paragraph>
                              {post.text}
                            </Typography>
                          )}

                          {post.image && (
                            <Box
                              component="img"
                              src={post.image}
                              alt="Post image"
                              sx={{
                                maxWidth: "100%",
                                maxHeight: 200,
                                objectFit: "contain",
                                mb: 1,
                              }}
                            />
                          )}
                        </PostContent>

                        <PostActions>
                          {!post.editing && (
                            <Button
                              variant="outlined"
                              startIcon={<Edit size={18} />}
                              onClick={() => handleEditPost(post.id)}
                            >
                              Edit
                            </Button>
                          )}
                          <Button
                            variant="contained"
                            color="primary"
                            startIcon={<Check size={18} />}
                            onClick={() => handleApprovePost(post.id)}
                          >
                            Approve
                          </Button>
                        </PostActions>
                      </PostItem>
                    </Box>
                  ))}
                </List>
              </Paper>
            </SuggestedPostsContainer>
          )}
        </ContentContainer>
      </StyledContainer>
    </>
  )
}

export default CreatePostsPage
