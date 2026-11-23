
from datetime import datetime
from pydantic import BaseModel, model_validator



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


class DatasetMappingRequest(BaseModel):
    date_column: str
    product_column: str
    quantity_column: str

    @model_validator(mode="after")
    def validate_distinct_columns(self):
        columns = [
            self.date_column.strip(),
            self.product_column.strip(),
            self.quantity_column.strip(),
        ]

        if any(not column for column in columns):
            raise ValueError("Column names cannot be empty.")

        if len(columns) != len(set(columns)):
            raise ValueError("Date, product, and quantity must use different columns.")

        self.date_column, self.product_column, self.quantity_column = columns

        return self


class DatasetMappingResponse(BaseModel):
      dataset_id: int
      business_id: int
      date_column: str
      product_column: str
      quantity_column: str
      status: str



class DatasetProcessingResponse(BaseModel):
    dataset_id: int
    business_id: int
    status: str
    total_rows: int
    retained_rows: int
    removed_rows: int
    cleaning_report: dict
