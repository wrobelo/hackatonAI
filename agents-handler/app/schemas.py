from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field

class GeneratePostsRequest(BaseModel):
    company_name: str
    company_description: str
    company_values: str
    target_audience: str
    brand_hero: str
    num_posts: int
    include_trends: bool
    trend_region: Optional[str] = None
    include_competition: bool

class ResearchReport(BaseModel):
    company_analysis: str
    trends: Optional[List[str]] = None
    competition: Optional[dict] = None

class BriefOutput(BaseModel):
    brief: str

class PostDraft(BaseModel):
    content: str = Field(default="")
    hashtags: List[str] = Field(default_factory=list)
    call_to_action: str = Field(default="")

class PostProposal(BaseModel):
    content: str
    hashtags: List[str]
    call_to_action: Optional[str]
    scene_description: str
    image_url: str
    

class SceneToolOutput(BaseModel):
    description: str

class GenerateImageOutput(BaseModel):
    url: HttpUrl

class ImageAgentOutput(BaseModel):
    scene_description: str
    image_url: HttpUrl

class CompanyContextRequest(BaseModel):
    user_response: Optional[str] = None

class BrandHeroContextRequest(BaseModel):
    user_response: Optional[str] = None

class GenerateBrandHeroImageRequest(BaseModel):
    company: str
    prompt: str
    contextId: str

class GenerateBrandHeroImageResponse(BaseModel):
    contextId: str

class SaveImage(BaseModel):
    image_url: str
    contextId: str
    description: str

# Model zapytania od użytkownika
class UserMessage(BaseModel):
    user_id: str
    message: str

# Model odpowiedzi z obrazkiem
class ImageResponse(BaseModel):
    image_url: str
    description: str

class CompanyContextResponse(BaseModel):
    company_id: str
    context_description: str

class BrandHeroContextResponse(BaseModel):
    company_id: str
    brandhero_context: str
    brandhero_description: Optional[str] = None
    image_url: Optional[str] = None
