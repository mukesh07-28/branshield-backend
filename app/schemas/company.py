from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CompanyCreate(BaseModel):
    name: str
    website: str | None = None
    logo_url: str | None = None
    description: str | None = None


class CompanyResponse(BaseModel):
    id: int
    name: str
    website: str | None = None
    logo_url: str | None = None
    description: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)