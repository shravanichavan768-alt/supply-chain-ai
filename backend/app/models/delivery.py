from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class DeliveryStatus(str, Enum):
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"


class DeliveryInDB(BaseModel):
    order_id: str
    truck_id: str
    warehouse_id: str
    destination_latitude: float
    destination_longitude: float
    distance_km: float
    status: DeliveryStatus = DeliveryStatus.ASSIGNED
    estimated_delivery_time_minutes: Optional[float] = None
    actual_delivery_time_minutes: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)