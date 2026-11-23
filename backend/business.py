
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
from backend.models import User, Business, BusinessMember, Dataset, DatasetProcessing
from backend.business_schemas import (
    BusinessMembershipResponse,
    BusinessDetailResponse,
    DatasetUploadResponse,
    DatasetPreviewResponse,
    DatasetMappingRequest,
    DatasetMappingResponse,
    DatasetProcessingResponse
)

from backend.dataset_validation import ( DatasetValidationError, inspect_dataset,)
from backend.dataset_processing import ( DatasetProcessingError, process_uploaded_dataset,)


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


@router.put(
    "/{business_id}/datasets/{dataset_id}/mapping",
    response_model=DatasetMappingResponse,
)
def map_dataset_columns(
    business_id: int,
    dataset_id: int,
    mapping: DatasetMappingRequest,
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

    available_columns = inspection["columns"]

    selected_columns = [
        mapping.date_column,
        mapping.product_column,
        mapping.quantity_column,
    ]

    missing_columns = [
        column
        for column in selected_columns
        if column not in available_columns
    ]

    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail=f"Columns not found in dataset: {missing_columns}",
        )

    dataset.date_column = mapping.date_column
    dataset.product_column = mapping.product_column
    dataset.quantity_column = mapping.quantity_column

    db.commit()
    db.refresh(dataset)

    return DatasetMappingResponse(
        dataset_id=dataset.id,
        business_id=dataset.business_id,
        date_column=dataset.date_column,
        product_column=dataset.product_column,
        quantity_column=dataset.quantity_column,
        status=dataset.status,
    )



@router.post(
    "/{business_id}/datasets/{dataset_id}/process",
    response_model=DatasetProcessingResponse,
)
def process_business_dataset(
    business_id: int,
    dataset_id: int,
    current_business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    # Find a dataset belonging to the authenticated user's business.
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

    # Require all three column mappings before processing.
    if not all([
        dataset.date_column,
        dataset.product_column,
        dataset.quantity_column,
    ]):
        raise HTTPException(
            status_code=400,
            detail="Map the date, product, and quantity columns first.",
        )

    try:
        result = process_uploaded_dataset(
            file_path=dataset.file_path,
            date_column=dataset.date_column,
            product_column=dataset.product_column,
            quantity_column=dataset.quantity_column,
        )
    except DatasetProcessingError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    # Store output separately for this business and dataset.
    output_directory = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / f"business_{current_business.id}"
    )
    output_directory.mkdir(parents=True, exist_ok=True)

    output_filename = f"dataset_{dataset.id}_{uuid4().hex}.csv"
    output_path = output_directory / output_filename
    temporary_path = output_path.with_suffix(".tmp")

    previous_processing = (
        db.query(DatasetProcessing)
        .filter(DatasetProcessing.dataset_id == dataset.id)
        .first()
    )

    old_output_path = (
        Path(previous_processing.processed_file_path)
        if previous_processing is not None
        else None
    )

    report = result["cleaning_report"]
    weekly_sales = result["weekly_sales"]

    try:
        # Write the new output before changing the database record.
        weekly_sales.to_csv(temporary_path, index=False)
        temporary_path.replace(output_path)

        if previous_processing is None:
            processing_record = DatasetProcessing(
                dataset_id=dataset.id,
                business_id=current_business.id,
                processed_file_path=str(output_path),
                cleaning_report=report,
                retained_rows=report["retained_rows"],
            )
            db.add(processing_record)
        else:
            previous_processing.processed_file_path = str(output_path)
            previous_processing.cleaning_report = report
            previous_processing.retained_rows = report["retained_rows"]

        dataset.status = "processed"

        db.commit()

    except Exception:
        db.rollback()

        if temporary_path.exists():
            temporary_path.unlink()

        if output_path.exists():
            output_path.unlink()

        raise

    # Remove the previous output only after the new result is committed.
    if (
        old_output_path is not None
        and old_output_path != output_path
        and old_output_path.is_file()
    ):
        old_output_path.unlink()

    return DatasetProcessingResponse(
        dataset_id=dataset.id,
        business_id=current_business.id,
        status=dataset.status,
        total_rows=report["total_rows"],
        retained_rows=report["retained_rows"],
        removed_rows=report["removed_rows"],
        cleaning_report=report,
    )
