from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.delivery import DeliveryStatus


class DeliveryCreate(BaseModel):
    order_id: str
    truck_id: str
    warehouse_id: str
    destination_latitude: float
    destination_longitude: float


class DeliveryResponse(BaseModel):
    id: str
    order_id: str
    truck_id: str
    warehouse_id: str
    destination_latitude: float
    destination_longitude: float
    distance_km: float
    status: DeliveryStatus
    estimated_delivery_time_minutes: Optional[float]
    actual_delivery_time_minutes: Optional[float]
    created_at: datetime
    updated_at: datetime


class DeliveryStatusUpdate(BaseModel):
    status: DeliveryStatus