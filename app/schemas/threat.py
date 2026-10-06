from pydantic import BaseModel, ConfigDict


class ThreatCreate(BaseModel):
    source_type: str
    platform: str | None = None
    name: str
    url: str | None = None


class ThreatResponse(BaseModel):
    id: int
    company_id: int
    source_type: str
    platform: str | None = None
    name: str
    url: str | None = None
    risk_score: float
    severity: str
    status: str
    analysis_reasons: str | None = None

    model_config = ConfigDict(from_attributes=True)