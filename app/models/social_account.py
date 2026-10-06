from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.core.database import Base


class OfficialSocialAccount(Base):
    __tablename__ = "official_social_accounts"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False
    )

    platform = Column(String(100), nullable=False)

    username = Column(String(255), nullable=False)

    profile_url = Column(String(500), nullable=False)

    verified = Column(Boolean, default=False)