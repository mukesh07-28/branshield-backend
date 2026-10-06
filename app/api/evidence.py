from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.company import Company
from app.models.threat import Threat
from app.models.evidence import ThreatEvidence
from app.schemas.evidence import (
    EvidenceCreate,
    EvidenceResponse
)


router = APIRouter(
    prefix="/companies",
    tags=["Evidence"]
)


# ============================================================
# ADD EVIDENCE
# ============================================================

@router.post(
    "/{company_id}/threats/{threat_id}/evidence",
    response_model=EvidenceResponse
)
def add_evidence(
    company_id: int,
    threat_id: int,
    evidence: EvidenceCreate,
    db: Session = Depends(get_db)
):

    # Check company
    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    # Check threat
    threat = db.query(Threat).filter(
        Threat.id == threat_id,
        Threat.company_id == company_id
    ).first()

    if not threat:
        raise HTTPException(
            status_code=404,
            detail="Threat not found"
        )

    # Create evidence
    new_evidence = ThreatEvidence(
        threat_id=threat_id,
        evidence_type=evidence.evidence_type,
        evidence_url=evidence.evidence_url,
        description=evidence.description
    )

    db.add(new_evidence)
    db.commit()
    db.refresh(new_evidence)

    return new_evidence


# ============================================================
# GET THREAT EVIDENCE
# ============================================================

@router.get(
    "/{company_id}/threats/{threat_id}/evidence",
    response_model=list[EvidenceResponse]
)
def get_evidence(
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

    evidence = db.query(ThreatEvidence).filter(
        ThreatEvidence.threat_id == threat_id
    ).order_by(
        ThreatEvidence.collected_at.desc()
    ).all()

    return evidence
@router.get(
    "/{company_id}/threats/{threat_id}/takedown-report"
)
def generate_takedown_report(
    company_id: int,
    threat_id: int,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Find company
    # --------------------------------------------------------

    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    # --------------------------------------------------------
    # Find threat
    # --------------------------------------------------------

    threat = db.query(Threat).filter(
        Threat.id == threat_id,
        Threat.company_id == company_id
    ).first()

    if not threat:
        raise HTTPException(
            status_code=404,
            detail="Threat not found"
        )

    # --------------------------------------------------------
    # Get evidence
    # --------------------------------------------------------

    evidence = db.query(ThreatEvidence).filter(
        ThreatEvidence.threat_id == threat_id
    ).order_by(
        ThreatEvidence.collected_at.desc()
    ).all()

    # --------------------------------------------------------
    # Convert evidence to JSON
    # --------------------------------------------------------

    evidence_list = []

    for item in evidence:

        evidence_list.append({
            "id": item.id,
            "type": item.evidence_type,
            "url": item.evidence_url,
            "description": item.description,
            "collected_at": item.collected_at
        })

    # --------------------------------------------------------
    # Detection reasons
    # --------------------------------------------------------

    reasons = []

    if threat.analysis_reasons:

        reasons = [
            reason.strip()
            for reason in threat.analysis_reasons.split(",")
            if reason.strip()
        ]

    # --------------------------------------------------------
    # Generate report
    # --------------------------------------------------------

    return {
        "report_type": "Digital Risk Protection Takedown Report",

        "company": {
            "id": company.id,
            "name": company.name,
            "website": company.website
        },

        "threat": {
            "id": threat.id,
            "source_type": threat.source_type,
            "platform": threat.platform,
            "name": threat.name,
            "url": threat.url,
            "risk_score": threat.risk_score,
            "severity": threat.severity,
            "status": threat.status
        },

        "detection_reasons": reasons,

        "evidence": evidence_list,

        "request": {
            "action": "Request platform review and takedown",
            "reason": "Potential brand impersonation or fraudulent activity"
        }
    }