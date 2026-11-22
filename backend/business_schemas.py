
from datetime import datetime
from pydantic import BaseModel


class BusinessMembershipResponse(BaseModel):
    business_id: int
    business_name: str
    role: str


class BusinessDetailResponse(BaseModel):
    business_id: int
    business_name: str


class DatasetUploadResponse(BaseModel):
    dataset_id: int
    business_id: int
    original_filename: str
    status: str
    uploaded_at: datetime


class DatasetPreviewResponse(BaseModel):
    dataset_id: int
    business_id: int
    original_filename: str
    columns: list[str]
    preview: list[dict[str, str]]
    sample_row_count: int
