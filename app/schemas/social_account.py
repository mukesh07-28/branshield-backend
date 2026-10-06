from pydantic import BaseModel, ConfigDict


class SocialAccountCreate(BaseModel):
    platform: str
    username: str
    profile_url: str
    verified: bool = False


class SocialAccountResponse(BaseModel):
    id: int
    company_id: int
    platform: str
    username: str
    profile_url: str
    verified: bool

    model_config = ConfigDict(from_attributes=True)