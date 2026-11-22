
from fastapi import APIRouter, Depends , HTTPException, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import User, Business , BusinessMember
from backend.business_schemas import BusinessMembershipResponse
from backend.business_schemas import BusinessDetailResponse

router = APIRouter(prefix="/businesses", tags=["Businesses"])


def get_current_business(
    business_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Business:

    membership = (
        db.query(BusinessMember)
        .filter(
            BusinessMember.business_id == business_id,
            BusinessMember.user_id == current_user.id,
        )
        .first()
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found.",
        )

    return membership.business



@router.get(
    "",
    response_model=list[BusinessMembershipResponse],
)
def get_my_businesses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    memberships = (
        db.query(BusinessMember)
        .filter(BusinessMember.user_id == current_user.id)
        .all()
    )

    return [
        BusinessMembershipResponse(
            business_id=membership.business.id,
            business_name=membership.business.business_name,
            role=membership.role,
        )
        for membership in memberships
    ]



@router.get(
    "/{business_id}",
    response_model=BusinessDetailResponse,
)
def get_business_details(
    business: Business = Depends(get_current_business),
):
    return BusinessDetailResponse(
        business_id=business.id,
        business_name=business.business_name,
    )