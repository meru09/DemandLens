
from pydantic import BaseModel

class BusinessMembershipResponse(BaseModel):
    business_id: int
    business_name: str
    role: str

class BusinessDetailResponse(BaseModel):
    business_id: int
    business_name: str