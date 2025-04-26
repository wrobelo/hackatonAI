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
  Card,
  CardContent,
} from "@mui/material"
import Header from "@/components/header"
import {Stack} from "@mui/system";
import {
  useQuery, useQueryClient,
} from '@tanstack/react-query'
import {ContextChat} from "@/components/ContextChat";


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
  
  pre {
    font-family: inherit;
  }
`




const ProfileCreationPage = ({ params }: { params: { pageId: string } }) => {
  const [isEditMode, setIsEditMode] = useState(false)
  const [initialLoadDone, setInitialLoadDone] = useState(false)
  const router = useRouter()
  const queryClient = useQueryClient();

  const { isPending, error, data } = useQuery({
    queryKey: ['get.company-context'],
    queryFn: () =>
        fetch(`/api/company-context/${params.pageId}`).then((res): Promise<{
          company_id: string;
          context_description: string;
        }> =>
            res.json(),
        ),
  })



  useEffect(() => {
    if (!initialLoadDone && (data || error)) {
      const editing = !!data?.context_description
      if (editing) {
        setIsEditMode(true);
      }
      setInitialLoadDone(true);
    }
  }, [data, error, initialLoadDone]);


  const handleConfirmProfile = () => {
    // If in edit mode, go back to dashboard, otherwise continue to brand hero creation
    if (isEditMode) {
      router.push(`/${params.pageId}/dashboard`)
    } else {
      router.push(`/${params.pageId}/brand-hero-creation`)
    }
  }


  return (
    <>
      <Header />
      <StyledContainer>
          <ChatContainer sx={{height: "100%"}}>
            <Typography variant="h5" gutterBottom>
              {isEditMode ? "Editing Your Company Profile" : "Creating Your Company Profile"}
            </Typography>

            <Stack direction="row" spacing={2} sx={{ mb: 2, flexGrow: 1, height: "100%" }}>
              {data?.context_description && (
                  <ProfileSummaryCard sx={{ flexBasis: "50%"}}>
                    <CardContent sx={{height: "100%"}}>
                      <Stack direction="column" spacing={2} justifyContent="stretch" sx={{height: "100%"}}>
                        <Typography variant="h6" gutterBottom>
                          Your Brand Profile
                        </Typography>
                        <Typography variant="body2" component="pre" sx={{ whiteSpace: "pre-wrap", overflowY: "auto", flex: '1 1 0' }}>
                          {data?.context_description}
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
                <ContextChat
                    endpoint={`/api/company-context/${params.pageId}`}
                    onResponse={() => queryClient.invalidateQueries({
                      queryKey: ['get.company-context']
                    })}
                />
              </Box>

            </Stack>


          </ChatContainer>
      </StyledContainer>
    </>
  )
}

export default ProfileCreationPage
