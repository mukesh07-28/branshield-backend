from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.company import Company
from app.models.social_account import OfficialSocialAccount
from app.schemas.social_account import (
    SocialAccountCreate,
    SocialAccountResponse
)


router = APIRouter(
    prefix="/companies",
    tags=["Social Accounts"]
)


@router.post(
    "/{company_id}/social-accounts",
    response_model=SocialAccountResponse
)
def create_social_account(
    company_id: int,
    account: SocialAccountCreate,
    db: Session = Depends(get_db)
):
    # Check whether company exists
    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    # Create social account
    new_account = OfficialSocialAccount(
        company_id=company_id,
        platform=account.platform,
        username=account.username,
        profile_url=account.profile_url,
        verified=account.verified
    )

    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    return new_account