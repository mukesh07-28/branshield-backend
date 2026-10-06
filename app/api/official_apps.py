from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.company import Company
from app.models.official_app import OfficialApp
from app.schemas.official_app import (
    OfficialAppCreate,
    OfficialAppResponse
)


router = APIRouter(
    prefix="/companies",
    tags=["Official Apps"]
)


@router.post(
    "/{company_id}/official-apps",
    response_model=OfficialAppResponse
)
def create_official_app(
    company_id: int,
    app: OfficialAppCreate,
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

    new_app = OfficialApp(
        company_id=company_id,
        app_name=app.app_name,
        developer=app.developer,
        package_id=app.package_id,
        store=app.store,
        store_url=app.store_url,
        verified=app.verified
    )

    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    return new_app