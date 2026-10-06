from fastapi import FastAPI

from app.api.companies import router as companies_router
from app.api.social_accounts import router as social_accounts_router
from app.api.official_apps import router as official_apps_router
from app.api.threats import router as threats_router
from app.api.evidence import router as evidence_router

from app.core.database import Base, engine

from app.models.company import Company
from app.models.social_account import OfficialSocialAccount
from app.models.official_app import OfficialApp
from app.models.threat import Threat
from app.models.evidence import ThreatEvidence


app = FastAPI(
    title="BrandShield AI",
    description="Digital Risk Protection Platform",
    version="1.0.0"
)


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# REGISTER API ROUTES
# ============================================================

app.include_router(companies_router)
app.include_router(social_accounts_router)
app.include_router(official_apps_router)
app.include_router(threats_router)
app.include_router(evidence_router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "BrandShield AI Backend is Running!"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }