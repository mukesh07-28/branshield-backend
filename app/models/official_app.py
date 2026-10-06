from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

from app.core.database import Base


class OfficialApp(Base):
    __tablename__ = "official_apps"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False
    )

    app_name = Column(String(255), nullable=False)
    developer = Column(String(255), nullable=False)
    package_id = Column(String(255), nullable=True)
    store = Column(String(100), nullable=False)
    store_url = Column(String(500), nullable=True)
    verified = Column(Boolean, default=False)