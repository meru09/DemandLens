
from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    status,
)
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import User, Business, BusinessMember, Dataset
from backend.business_schemas import (
    BusinessMembershipResponse,
    BusinessDetailResponse,
    DatasetUploadResponse,
    DatasetPreviewResponse
)

from backend.dataset_validation import ( DatasetValidationError, inspect_dataset,)



router = APIRouter(prefix="/businesses", tags=["Businesses"])

PROJECT_ROOT = Path(__file__).resolve().parents[1]
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

ALLOWED_EXTENSIONS = {".csv", ".xlsx"}


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



@router.post(
    "/{business_id}/datasets/upload",
    response_model=DatasetUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_dataset(
    business_id: int,
    file: UploadFile = File(...),
    current_business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    original_filename = Path(file.filename or "").name

    if not original_filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    file_extension = Path(original_filename).suffix.lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only CSV and XLSX files are supported.",
        )

    business_directory = UPLOAD_DIR / f"business_{current_business.id}"
    business_directory.mkdir(parents=True, exist_ok=True)

    stored_filename = f"{uuid4().hex}{file_extension}"
    destination = business_directory / stored_filename

    total_size = 0

    try:
        with destination.open("wb") as destination_file:
            while chunk := file.file.read(1024 * 1024):
                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="File exceeds the 50 MB limit.",
                    )

                destination_file.write(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        dataset = Dataset(
            business_id=current_business.id,
            original_filename=original_filename,
            file_path=str(destination),
            status="uploaded",
        )

        db.add(dataset)
        db.commit()
        db.refresh(dataset)

        return DatasetUploadResponse(
            dataset_id=dataset.id,
            business_id=dataset.business_id,
            original_filename=dataset.original_filename,
            status=dataset.status,
            uploaded_at=dataset.uploaded_at,
        )

    except Exception:
        db.rollback()

        if destination.exists():
            destination.unlink()

        raise


@router.get(
    "/{business_id}/datasets/{dataset_id}/preview",
    response_model=DatasetPreviewResponse,
)
def preview_dataset(
    business_id: int,
    dataset_id: int,
    current_business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    dataset = (
        db.query(Dataset)
        .filter(
            Dataset.id == dataset_id,
            Dataset.business_id == current_business.id,
        )
        .first()
    )

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    if not Path(dataset.file_path).is_file():
        raise HTTPException(
            status_code=404,
            detail="Dataset file not found.",
        )

    try:
        inspection = inspect_dataset(dataset.file_path)
    except DatasetValidationError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return DatasetPreviewResponse(
        dataset_id=dataset.id,
        business_id=current_business.id,
        original_filename=dataset.original_filename,
        columns=inspection["columns"],
        preview=inspection["preview"],
        sample_row_count=inspection["sample_row_count"],
    )
