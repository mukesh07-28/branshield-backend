from pydantic import BaseModel, ConfigDict
from datetime import datetime


class EvidenceCreate(BaseModel):
    evidence_type: str
    evidence_url: str | None = None
    description: str | None = None


class EvidenceResponse(BaseModel):
    id: int
    threat_id: int
    evidence_type: str
    evidence_url: str | None = None
    description: str | None = None
    collected_at: datetime

    model_config = ConfigDict(from_attributes=True)