import React, {useEffect, useState} from "react";
import axios from "axios";
import {Chat, ChatMessage} from "@/components/chat";

interface ContextChatResponse {
    "company_id":string,
    "result": {
        "output": string,
        "previous_response_id": string,
    }
}

export const ContextChat = ({endpoint, onResponse}: {
    endpoint: string,
    onResponse: () => void
}) => {
    const [messages, setMessages] = useState<ChatMessage[]>([])
    const [processing, setProcessing] = useState(false);

    useEffect(() => {
        handleSendMessage('', true)
    }, [])

    const handleSendMessage = async (inputValue: string, initialMessage?: boolean) => {
        if (!inputValue.trim() && !initialMessage) return;
        setProcessing(true);

        const userMessage: ChatMessage = {
            id: messages.length + 1,
            isUser: true,
            text: initialMessage ? '' : inputValue.trim()
        };

        setMessages(prev => [...prev, userMessage]);

        try {
            const response = await axios.post<ContextChatResponse>(endpoint, {
                user_response: userMessage.text
            });

            const aiMessage: ChatMessage = {
                id: messages.length + 2,
                isUser: false,
                text: response.data.result.output
            };

            setMessages(prev => [...prev, aiMessage]);
            onResponse();
        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage: ChatMessage = {
                id: messages.length + 2,
                isUser: false,
                text: "Sorry, there was an error processing your message."
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setProcessing(false);
        }
    }


    return (
        <Chat messages={messages} onMessageSent={handleSendMessage} processing={processing} />
    )

}
