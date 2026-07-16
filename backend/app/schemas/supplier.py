from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


class SupplierCreate(BaseModel):
    name: str
    contact_email: EmailStr
    contact_phone: str
    production_capacity: int
    lead_time_days: int
    cost_per_unit: float
    products_supplied: List[str] = Field(default_factory=list)


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    production_capacity: Optional[int] = None
    lead_time_days: Optional[int] = None
    cost_per_unit: Optional[float] = None
    products_supplied: Optional[List[str]] = None


class SupplierResponse(BaseModel):
    id: str
    name: str
    contact_email: EmailStr
    contact_phone: str
    production_capacity: int
    lead_time_days: int
    cost_per_unit: float
    reliability_score: float
    products_supplied: List[str]
    created_at: datetime
    updated_at: datetime


class ReliabilityAdjustment(BaseModel):
    delta: float = Field(..., description="Amount to add/subtract from reliability score, e.g. -5 for a late delivery")
    reason: str