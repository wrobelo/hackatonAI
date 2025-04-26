"use client"

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
  CardActions,
  List,
  ListItem,
  Divider,
  Paper,
} from "@mui/material"
import { Edit, Plus, Check, Clock } from "lucide-react"
import Header from "@/components/header"
import {useQuery} from "@tanstack/react-query";

const StyledContainer = styled(Container)`
  padding: 2rem;
  max-width: 1200px;
`

const TileCard = styled(Card)`
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  
  &:hover {
    transform: translateY(-4px);
  }
`

const TileContent = styled(CardContent)`
  flex: 1;
`

const EmptyPostsContainer = styled(Box)`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
`

const PostItem = styled(ListItem)`
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 1.5rem;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: ${(props) =>
      props.theme.palette.mode === "dark" ? "rgba(255, 255, 255, 0.03)" : "rgba(0, 0, 0, 0.01)"};
  }
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

// Mock posts
const mockPosts = [
  {
    id: 1,
    text: "Start your week with our signature Lavender Honey Latte! The perfect blend of floral notes and sweetness to brighten your Monday. ☕💜 #MondayMotivation #CoffeeDelights",
    scheduledDate: "2023-06-15",
    image: "/placeholder.svg?height=200&width=400",
    approved: true,
  },
  {
    id: 2,
    text: "Did you know? All our coffee beans are locally sourced and roasted in small batches to ensure the freshest flavor in every cup! Come experience the difference quality makes. #SustainableCoffee #LocallySourced",
    scheduledDate: "2023-06-18",
    image: null,
    approved: false,
  },
]

const Dashboard = ({params: {pageId}}: {params: {pageId: string}}) => {
  const [posts, setPosts] = useState<any[]>([])
  const router = useRouter()

  const {data: companyContextData } = useQuery({
    queryKey: ['get.company-context'],
    queryFn: () =>
        fetch(`/api/company-context/${pageId}`).then((res): Promise<{
              company_id: string;
              context_description: string;
            }> =>
                res.json(),
        ),
  })

  const { data: brandHeroContextData } = useQuery({
    queryKey: ['get.brand-hero-context'],
    queryFn: () =>
        fetch(`/api/brand-hero-context/${pageId}`).then((res): Promise<{
              company_id: string;
              brandhero_context: string;
              brandhero_description?: string;
              image_url?: string;
            }> =>
                res.json(),
        ),
  })

  const { data: strategyData } = useQuery({
    queryKey: ['get.strategy'],
    queryFn: () =>
        fetch(`/api/strategy/${pageId}`).then((res): Promise<{
          company_id: string;
          strategy: string;
        }> =>
            res.json(),
        ),
  })

  useEffect(() => {

    // if ((!isPending && !companyContextData?.context_description) || !heroImage) {
    //   // Redirect to appropriate setup page
    //   if (!companyContextData?.context_description) {
    //     router.push(`/${pageId}/profile-creation`)
    //   } else if (!heroImage) {
    //     router.push(`/${pageId}/brand-hero-creation`)
    //   }
    //   return
    // }

    // Set mock posts
    setPosts(mockPosts)
  }, [router])

  const handleEditProfile = () => {
    router.push(`/${pageId}/profile-creation`)
  }

  const handleEditBrandHero = () => {
    router.push(`/${pageId}/brand-hero-creation`)
  }

  const handleCreatePosts = () => {
    router.push(`/${pageId}/create-posts`)
  }

  const handleCreateStrategy = () => {
    router.push(`/${pageId}/strategy-creation`)
  }

  const handleApprovePost = (postId: number) => {
    setPosts(posts.map((post) => (post.id === postId ? { ...post, approved: true } : post)))
  }

  const handlePostNow = (postId: number) => {
    // In a real app, this would send the post to Facebook
    alert(`Post ${postId} has been published to Facebook!`)

    // Remove from list
    setPosts(posts.filter((post) => post.id !== postId))
  }

  return (
    <>
      <Header />
      <StyledContainer>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>

        <Box sx={{ display: "flex", flexDirection: { xs: "column", sm: "row" }, gap: 3, mb: 4 }}>
          <TileCard sx={{ flex: 1, width: { xs: "100%", sm: "50%" } }}>
            <TileContent>
              <Typography variant="h6" gutterBottom>
                Company Profile
              </Typography>
              {companyContextData?.context_description && (
                <Typography variant="body2" component="pre" sx={{ whiteSpace: "pre-wrap" }}>
                  {companyContextData.context_description}
                </Typography>
              )}
            </TileContent>
            <CardActions>
              <Button startIcon={<Edit size={18} />} onClick={handleEditProfile}>
                Edit Profile
              </Button>
            </CardActions>
          </TileCard>

          <TileCard sx={{ flex: 1, width: { xs: "100%", sm: "50%" } }}>
            <TileContent>
              <Typography variant="h6" gutterBottom>
                Brand Hero
              </Typography>
              {brandHeroContextData?.image_url && (<Box sx={{ display: "flex", justifyContent: "center", p: 2 }}>
                  <Box
                    component="img"
                    src={brandHeroContextData?.image_url}
                    alt="Brand Hero Character"
                    sx={{
                      maxWidth: "100%",
                      maxHeight: 250,
                      objectFit: "contain",
                    }}
                  />
              </Box>)}
            </TileContent>
            <CardActions>
              <Button startIcon={<Edit size={18} />} onClick={handleEditBrandHero}>
                Edit Brand Hero
              </Button>
            </CardActions>
          </TileCard>
        </Box>

          <Button sx={{width: '100%', my: 4}} variant="contained" color="primary" startIcon={!strategyData?.strategy && <Plus size={18} />} onClick={handleCreateStrategy}>
            {strategyData?.strategy ? 'Edit Strategy' : 'Create Strategy'}
          </Button>

        <Box sx={{ mb: 2, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <Typography variant="h5">Scheduled Posts</Typography>
        </Box>

        <Paper>
          {posts.length > 0 ? (
            <List>
              {posts.map((post, index) => (
                <Box key={post.id}>
                  {index > 0 && <Divider />}
                  <PostItem>
                    <PostContent>
                      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                          <Clock size={16} />
                          <Typography variant="body2" color="textSecondary">
                            Scheduled for: {post.scheduledDate}
                          </Typography>
                        </Box>
                        {post.approved && (
                          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                            <Check size={16} color="green" />
                            <Typography variant="body2" color="green">
                              Approved
                            </Typography>
                          </Box>
                        )}
                      </Box>

                      <Typography variant="body1" paragraph>
                        {post.text}
                      </Typography>

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
                      {!post.approved && (
                        <Button variant="outlined" color="primary" onClick={() => handleApprovePost(post.id)}>
                          Approve
                        </Button>
                      )}
                      <Button variant="contained" color="primary" onClick={() => handlePostNow(post.id)}>
                        Post Now
                      </Button>
                    </PostActions>
                  </PostItem>
                </Box>
              ))}
            </List>
          ) : (
            <EmptyPostsContainer>
              <Typography variant="h6" gutterBottom>
                No Posts Scheduled
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                Create a strategy to start engaging with your audience
              </Typography>
              <Button variant="contained" color="primary" startIcon={<Plus size={18} />} onClick={handleCreateStrategy}>
                Create Strategy
              </Button>
            </EmptyPostsContainer>
          )}
        </Paper>
      </StyledContainer>
    </>
  )
}

export default Dashboard
