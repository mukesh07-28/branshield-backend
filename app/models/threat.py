from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime

from app.core.database import Base


class Threat(Base):
    __tablename__ = "threats"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False
    )

    source_type = Column(
        String(50),
        nullable=False
    )

    platform = Column(
        String(100),
        nullable=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    url = Column(
        String(500),
        nullable=True
    )

    risk_score = Column(
        Float,
        default=0
    )

    severity = Column(
        String(50),
        default="Low"
    )

    status = Column(
        String(50),
        default="New"
    )

    analysis_reasons = Column(
        String(1000),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )