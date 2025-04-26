"use client"

import type React from "react"
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
  const router = useRouter()
  const queryClient = useQueryClient();

  const { isPending, error, data } = useQuery({
    queryKey: ['get.brand-hero-context'],
    queryFn: () =>
        fetch(`/api/brand-hero-context/${params.pageId}`).then((res): Promise<{
          company_id: string;
          brandhero_context: string;
          brandhero_description?: string;
          image_url?: string;
        }> =>
            res.json(),
        ),
  })


  const handleConfirmProfile = () => {
    router.push(`/${params.pageId}/dashboard`)
  }


  return (
      <>
        <Header />
        <StyledContainer>
              <ChatContainer sx={{height: "100%"}}>
                <Typography variant="h5" gutterBottom>
                  {"Shaping Your Company's Brand Hero"}
                </Typography>

                <Stack direction="row" spacing={2} sx={{ mb: 2, flexGrow: 1, height: "100%" }}>
                  {data?.image_url && (
                      <ProfileSummaryCard sx={{ flexBasis: "50%"}}>
                        <CardContent sx={{height: "100%"}}>
                          <Stack direction="column" spacing={2} justifyContent="stretch" sx={{height: "100%"}}>
                            <Typography variant="h6" gutterBottom>
                              Your Brand Profile
                            </Typography>
                            <Typography variant="body2" component="pre" sx={{ whiteSpace: "pre-wrap", overflowY: "auto", flex: '1 1 0' }}>
                              <img src={data.image_url} alt="" className="src"/>
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
                        endpoint={`/api/brand-hero-context/${params.pageId}`}
                        onResponse={() => queryClient.invalidateQueries({
                          queryKey: ['get.brand-hero-context']
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
