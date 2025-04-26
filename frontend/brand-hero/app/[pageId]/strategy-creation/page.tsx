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

const StrategyCreationPage = ({ params }: { params: { pageId: string } }) => {
  const router = useRouter()
  const queryClient = useQueryClient();

  const { isPending, error, data } = useQuery({
    queryKey: ['get.strategy'],
    queryFn: () =>
        fetch(`/api/strategy/${params.pageId}`).then((res): Promise<{
              company_id: string;
              strategy: string;
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
              {"Shaping Your Company's Strategy"}
            </Typography>

            <Stack direction="row" spacing={2} sx={{ mb: 2, flexGrow: 1, height: "100%" }}>
              {data?.strategy && (
                  <ProfileSummaryCard sx={{ flexBasis: "50%"}}>
                    <CardContent sx={{height: "100%"}}>
                      <Stack direction="column" spacing={2} justifyContent="stretch" sx={{height: "100%"}}>
                        <Typography variant="h6" gutterBottom>
                          Your Brand Profile
                        </Typography>
                        <Typography variant="body2" component="p" sx={{ whiteSpace: "pre-wrap", overflowY: "auto", flex: '1 1 0' }}>
                          <pre>{data.strategy}</pre>
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
                    endpoint={`/api/strategy/${params.pageId}`}
                    onResponse={() => queryClient.invalidateQueries({
                      queryKey: ['get.strategy']
                    })}
                />
              </Box>

            </Stack>


          </ChatContainer>
        </StyledContainer>
      </>
  )
}

export default StrategyCreationPage
