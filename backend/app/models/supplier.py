from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import List


class SupplierInDB(BaseModel):
    name: str
    contact_email: EmailStr
    contact_phone: str
    production_capacity: int
    lead_time_days: int
    cost_per_unit: float
    reliability_score: float = Field(default=100.0, ge=0, le=100)
    products_supplied: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)