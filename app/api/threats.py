from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.company import Company
from app.models.threat import Threat
from app.schemas.threat import ThreatCreate, ThreatResponse
from app.services.risk_engine import calculate_risk_score


router = APIRouter(
    prefix="/companies",
    tags=["Threats"]
)


# ============================================================
# CREATE NEW THREAT
# ============================================================

@router.post(
    "/{company_id}/threats",
    response_model=ThreatResponse
)
def create_threat(
    company_id: int,
    threat: ThreatCreate,
    db: Session = Depends(get_db)
):
    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    risk_result = calculate_risk_score(
        brand_name=company.name,
        suspicious_name=threat.name,
        suspicious_url=threat.url,
        official_url=company.website,
        source_type=threat.source_type
    )

    reasons_text = ", ".join(
        risk_result["reasons"]
    )

    new_threat = Threat(
        company_id=company_id,
        source_type=threat.source_type,
        platform=threat.platform,
        name=threat.name,
        url=threat.url,
        risk_score=risk_result["score"],
        severity=risk_result["severity"],
        status="New",
        analysis_reasons=reasons_text
    )

    db.add(new_threat)
    db.commit()
    db.refresh(new_threat)

    return new_threat


# ============================================================
# GET THREATS WITH FILTERS
# ============================================================

@router.get(
    "/{company_id}/threats",
    response_model=list[ThreatResponse]
)
def get_threats(
    company_id: int,
    severity: str | None = Query(
        default=None,
        description="Low, Medium, High, Critical"
    ),
    status: str | None = Query(
        default=None,
        description="New, Investigating, Resolved, Takedown Requested"
    ),
    db: Session = Depends(get_db)
):
    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    query = db.query(Threat).filter(
        Threat.company_id == company_id
    )

    if severity:
        query = query.filter(
            Threat.severity.ilike(
                severity.strip()
            )
        )

    if status:
        query = query.filter(
            Threat.status.ilike(
                status.strip()
            )
        )

    threats = query.order_by(
        Threat.risk_score.desc()
    ).all()

    return threats


# ============================================================
# UPDATE THREAT STATUS
# ============================================================

@router.patch(
    "/{company_id}/threats/{threat_id}/status",
    response_model=ThreatResponse
)
def update_threat_status(
    company_id: int,
    threat_id: int,
    status: str = Query(
        ...,
        description="New, Investigating, Takedown Requested, Resolved"
    ),
    db: Session = Depends(get_db)
):
    allowed_statuses = [
        "New",
        "Investigating",
        "Takedown Requested",
        "Resolved"
    ]

    status_value = status.strip()

    if status_value not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid status",
                "allowed_statuses": allowed_statuses
            }
        )

    threat = db.query(Threat).filter(
        Threat.id == threat_id,
        Threat.company_id == company_id
    ).first()

    if not threat:
        raise HTTPException(
            status_code=404,
            detail="Threat not found"
        )

    threat.status = status_value

    db.commit()
    db.refresh(threat)

    return threat


# ============================================================
# REQUEST TAKEDOWN
# ============================================================

@router.post(
    "/{company_id}/threats/{threat_id}/takedown",
    response_model=ThreatResponse
)
def request_takedown(
    company_id: int,
    threat_id: int,
    db: Session = Depends(get_db)
):
    threat = db.query(Threat).filter(
        Threat.id == threat_id,
        Threat.company_id == company_id
    ).first()

    if not threat:
        raise HTTPException(
            status_code=404,
            detail="Threat not found"
        )

    threat.status = "Takedown Requested"

    db.commit()
    db.refresh(threat)

    return threat


# ============================================================
# THREAT STATISTICS
# ============================================================

@router.get(
    "/{company_id}/threat-statistics"
)
def get_threat_statistics(
    company_id: int,
    db: Session = Depends(get_db)
):
    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    threats = db.query(Threat).filter(
        Threat.company_id == company_id
    ).all()

    critical = sum(
        1 for threat in threats
        if threat.severity == "Critical"
    )

    high = sum(
        1 for threat in threats
        if threat.severity == "High"
    )

    medium = sum(
        1 for threat in threats
        if threat.severity == "Medium"
    )

    low = sum(
        1 for threat in threats
        if threat.severity == "Low"
    )

    new = sum(
        1 for threat in threats
        if threat.status == "New"
    )

    investigating = sum(
        1 for threat in threats
        if threat.status == "Investigating"
    )

    takedown_requested = sum(
        1 for threat in threats
        if threat.status == "Takedown Requested"
    )

    resolved = sum(
        1 for threat in threats
        if threat.status == "Resolved"
    )

    return {
        "company_id": company_id,
        "total_threats": len(threats),

        "severity": {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low
        },

        "status": {
            "new": new,
            "investigating": investigating,
            "takedown_requested": takedown_requested,
            "resolved": resolved
        }
    }


# ============================================================
# DASHBOARD OVERVIEW
# ============================================================

@router.get(
    "/{company_id}/dashboard-overview"
)
def get_dashboard_overview(
    company_id: int,
    db: Session = Depends(get_db)
):
    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    threats = db.query(Threat).filter(
        Threat.company_id == company_id
    ).all()

    critical = sum(
        1 for threat in threats
        if threat.severity == "Critical"
    )

    high = sum(
        1 for threat in threats
        if threat.severity == "High"
    )

    medium = sum(
        1 for threat in threats
        if threat.severity == "Medium"
    )

    low = sum(
        1 for threat in threats
        if threat.severity == "Low"
    )

    new = sum(
        1 for threat in threats
        if threat.status == "New"
    )

    investigating = sum(
        1 for threat in threats
        if threat.status == "Investigating"
    )

    takedown_requested = sum(
        1 for threat in threats
        if threat.status == "Takedown Requested"
    )

    resolved = sum(
        1 for threat in threats
        if threat.status == "Resolved"
    )

    social = sum(
        1 for threat in threats
        if threat.source_type == "social"
    )

    apps = sum(
        1 for threat in threats
        if threat.source_type == "app"
    )

    average_risk = (
        round(
            sum(
                threat.risk_score or 0
                for threat in threats
            ) / len(threats),
            2
        )
        if threats
        else 0
    )

    highest_risk = sorted(
        threats,
        key=lambda threat: threat.risk_score or 0,
        reverse=True
    )[:5]

    top_threats = []

    for threat in highest_risk:
        top_threats.append({
            "id": threat.id,
            "name": threat.name,
            "platform": threat.platform,
            "source_type": threat.source_type,
            "risk_score": threat.risk_score,
            "severity": threat.severity,
            "status": threat.status,
            "url": threat.url
        })

    return {
        "company": {
            "id": company.id,
            "name": company.name,
            "website": company.website,
            "logo_url": company.logo_url
        },

        "summary": {
            "total_threats": len(threats),
            "average_risk_score": average_risk,
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low
        },

        "status": {
            "new": new,
            "investigating": investigating,
            "takedown_requested": takedown_requested,
            "resolved": resolved
        },

        "sources": {
            "social": social,
            "apps": apps
        },

        "top_threats": top_threats
    }


# ============================================================
# THREAT DETAILS
# ============================================================

@router.get(
    "/{company_id}/threats/{threat_id}/details"
)
def get_threat_details(
    company_id: int,
    threat_id: int,
    db: Session = Depends(get_db)
):
    threat = db.query(Threat).filter(
        Threat.id == threat_id,
        Threat.company_id == company_id
    ).first()

    if not threat:
        raise HTTPException(
            status_code=404,
            detail="Threat not found"
        )

    reasons = []

    if threat.analysis_reasons:
        reasons = [
            reason.strip()
            for reason in threat.analysis_reasons.split(",")
            if reason.strip()
        ]

    return {
        "id": threat.id,
        "company_id": threat.company_id,
        "source_type": threat.source_type,
        "platform": threat.platform,
        "name": threat.name,
        "url": threat.url,
        "risk_score": threat.risk_score,
        "severity": threat.severity,
        "status": threat.status,
        "detection_reasons": reasons,
        "created_at": threat.created_at
    }


# ============================================================
# SOCIAL MONITORING
# ============================================================

@router.post(
    "/{company_id}/monitor/social",
    response_model=ThreatResponse
)
def monitor_social_account(
    company_id: int,
    platform: str,
    username: str,
    profile_url: str,
    db: Session = Depends(get_db)
):
    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    risk_result = calculate_risk_score(
        brand_name=company.name,
        suspicious_name=username,
        suspicious_url=profile_url,
        official_url=company.website,
        source_type="social"
    )

    reasons_text = ", ".join(
        risk_result["reasons"]
    )

    new_threat = Threat(
        company_id=company_id,
        source_type="social",
        platform=platform,
        name=username,
        url=profile_url,
        risk_score=risk_result["score"],
        severity=risk_result["severity"],
        status="New",
        analysis_reasons=reasons_text
    )

    db.add(new_threat)
    db.commit()
    db.refresh(new_threat)

    return new_threat


# ============================================================
# MOBILE APP MONITORING
# ============================================================

@router.post(
    "/{company_id}/monitor/app",
    response_model=ThreatResponse
)
def monitor_mobile_app(
    company_id: int,
    app_name: str,
    developer: str,
    store: str,
    store_url: str,
    db: Session = Depends(get_db)
):
    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    risk_result = calculate_risk_score(
        brand_name=company.name,
        suspicious_name=app_name,
        suspicious_url=store_url,
        official_url=company.website,
        source_type="app"
    )

    reasons = list(
        risk_result["reasons"]
    )

    if developer.strip().lower() != company.name.strip().lower():
        reasons.append(
            "Different or suspicious app developer"
        )

    reasons_text = ", ".join(reasons)

    new_threat = Threat(
        company_id=company_id,
        source_type="app",
        platform=store,
        name=app_name,
        url=store_url,
        risk_score=risk_result["score"],
        severity=risk_result["severity"],
        status="New",
        analysis_reasons=reasons_text
    )

    db.add(new_threat)
    db.commit()
    db.refresh(new_threat)

    return new_threat


# ============================================================
# THREAT INVESTIGATION
# ============================================================

@router.get(
    "/{company_id}/threats/{threat_id}/investigation"
)
def investigate_threat(
    company_id: int,
    threat_id: int,
    db: Session = Depends(get_db)
):
    threat = db.query(Threat).filter(
        Threat.id == threat_id,
        Threat.company_id == company_id
    ).first()

    if not threat:
        raise HTTPException(
            status_code=404,
            detail="Threat not found"
        )

    domain = None

    if threat.url:
        domain = (
            threat.url
            .replace("https://", "")
            .replace("http://", "")
            .split("/")[0]
        )

    indicators = []

    if domain:
        indicators.append({
            "type": "Domain",
            "value": domain
        })

    if threat.platform:
        indicators.append({
            "type": "Platform",
            "value": threat.platform
        })

    if threat.source_type:
        indicators.append({
            "type": "Source",
            "value": threat.source_type
        })

    reasons = []

    if threat.analysis_reasons:
        reasons = [
            reason.strip()
            for reason in threat.analysis_reasons.split(",")
            if reason.strip()
        ]

    return {
        "threat_id": threat.id,

        "threat": {
            "name": threat.name,
            "url": threat.url,
            "platform": threat.platform,
            "source_type": threat.source_type,
            "risk_score": threat.risk_score,
            "severity": threat.severity,
            "status": threat.status
        },

        "infrastructure": {
            "domain": domain
        },

        "indicators": indicators,

        "detection_reasons": reasons,

        "investigation_note": (
            "Infrastructure indicators are based on "
            "publicly observable information. "
            "They support threat investigation and "
            "do not identify a person's private identity."
        )
    }


# ============================================================
# RE-MONITORING / REAPPEARANCE DETECTION
# ============================================================

@router.post(
    "/{company_id}/threats/{threat_id}/remonitor"
)
def remonitor_threat(
    company_id: int,
    threat_id: int,
    new_name: str,
    new_url: str,
    db: Session = Depends(get_db)
):
    original_threat = db.query(Threat).filter(
        Threat.id == threat_id,
        Threat.company_id == company_id
    ).first()

    if not original_threat:
        raise HTTPException(
            status_code=404,
            detail="Original threat not found"
        )

    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    from rapidfuzz import fuzz

    name_similarity = fuzz.ratio(
        original_threat.name.lower(),
        new_name.lower()
    )

    brand_similarity = fuzz.ratio(
        company.name.lower(),
        new_name.lower()
    )

    reappearance_detected = (
        name_similarity >= 70
        or brand_similarity >= 70
    )

    risk_result = calculate_risk_score(
        brand_name=company.name,
        suspicious_name=new_name,
        suspicious_url=new_url,
        official_url=company.website,
        source_type=original_threat.source_type
    )

    reasons = list(
        risk_result["reasons"]
    )

    if name_similarity >= 70:
        reasons.append(
            "Similar to previously detected threat"
        )

    if reappearance_detected:
        reasons.append(
            "Possible threat reappearance detected"
        )

    reasons_text = ", ".join(reasons)

    new_threat = Threat(
        company_id=company_id,
        source_type=original_threat.source_type,
        platform=original_threat.platform,
        name=new_name,
        url=new_url,
        risk_score=risk_result["score"],
        severity=risk_result["severity"],
        status="New",
        analysis_reasons=reasons_text
    )

    db.add(new_threat)
    db.commit()
    db.refresh(new_threat)

    return {
        "reappearance_detected": reappearance_detected,

        "original_threat": {
            "id": original_threat.id,
            "name": original_threat.name,
            "url": original_threat.url
        },

        "new_threat": {
            "id": new_threat.id,
            "name": new_threat.name,
            "url": new_threat.url,
            "risk_score": new_threat.risk_score,
            "severity": new_threat.severity,
            "status": new_threat.status
        },

        "similarity": {
            "previous_threat_similarity": round(
                name_similarity,
                2
            ),
            "brand_similarity": round(
                brand_similarity,
                2
            )
        },

        "detection_reasons": reasons
    }