import React, {useState} from "react";
import axios from "axios";
import {Chat, ChatMessage} from "@/components/chat";
import { useQueryClient } from '@tanstack/react-query'

interface ProfileChatResponse {
    "company_id":string,
    "result": {
        "output": string,
        "previous_response_id": string,
    }
}

export const ProfileChat = ({pageId}: {pageId: string}) => {
    const [messages, setMessages] = useState<ChatMessage[]>([])
    const queryClient = useQueryClient()

    const handleSendMessage = async (inputValue: string) => {
        if (!inputValue.trim()) return;

        const userMessage: ChatMessage = {
            id: messages.length + 1,
            isUser: true,
            text: inputValue.trim()
        };

        setMessages(prev => [...prev, userMessage]);

        try {
            const response = await axios.post<ProfileChatResponse>(`/api/company-context/${pageId}`, {
                user_response: userMessage.text
            });

            const aiMessage: ChatMessage = {
                id: messages.length + 2,
                isUser: false,
                text: response.data.result.output
            };

            setMessages(prev => [...prev, aiMessage]);
            queryClient.invalidateQueries({queryKey: ['get.company-context']});
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


    return (
        <Chat messages={messages} onMessageSent={handleSendMessage} />
    )

}
