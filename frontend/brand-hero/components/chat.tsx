import {Avatar, Button, TextField, Typography, useTheme} from "@mui/material";
import {Send} from "lucide-react";
import React, {useEffect} from "react";
import {useRef, useState} from "react";
import axios from "axios";
import {styled} from "styled-components";
import {Paper, Box} from "@mui/material";
import {Stack} from "@mui/system";

const ChatContainer = styled(Box)`
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
    margin: 0 auto;
    justify-content: flex-end;
    height: 100%;
`

const MessagesContainer = styled(Box)`
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  flex-direction: column;
    justify-content: flex-end;
  gap: 1rem;
`

const MessageInputContainer = styled(Box)`
  padding: 1rem;
  display: flex;
  gap: 1rem;
  align-items: center;
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
// Define a proper type for the message objects
interface ChatMessage {
    id: number
    isUser: boolean
    text: string
}

interface ApiResponse {
    message: string;
    id: number;
}

export const Chat = () => {
    const theme = useTheme();
    const messagesEndRef = useRef<null | HTMLDivElement>(null)
    const [messages, setMessages] = useState<ChatMessage[]>([])
    const [inputValue, setInputValue] = useState("")
    
    useEffect(() => {
        // Scroll to bottom when messages change
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages])

    const handleSendMessage = async () => {
        if (!inputValue.trim()) return;

        const userMessage: ChatMessage = {
            id: messages.length + 1,
            isUser: true,
            text: inputValue.trim()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue("");

        try {
            const response = await axios.post<ApiResponse>('/api/chat', {
                message: userMessage.text
            });

            const aiMessage: ChatMessage = {
                id: messages.length + 2,
                isUser: false,
                text: response.data.message
            };

            setMessages(prev => [...prev, aiMessage]);
        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage: ChatMessage = {
                id: messages.length + 2,
                isUser: false,
                text: "Sorry, there was an error processing your message."
            };
            setMessages(prev => [...prev, errorMessage]);
        }
    }

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault()
            handleSendMessage()
        }
    }
    
    return (
        <ChatContainer>
            <MessagesContainer>
                <Stack>
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
                </Stack>
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
    )
}