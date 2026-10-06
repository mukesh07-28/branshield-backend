from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime

from app.core.database import Base


class ThreatEvidence(Base):
    __tablename__ = "threat_evidence"

    id = Column(Integer, primary_key=True, index=True)

    threat_id = Column(
        Integer,
        ForeignKey("threats.id"),
        nullable=False
    )

    evidence_type = Column(
        String(100),
        nullable=False
    )

    evidence_url = Column(
        String(500),
        nullable=True
    )

    description = Column(
        Text,
        nullable=True
    )

    collected_at = Column(
        DateTime,
        default=datetime.utcnow
    )