from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.truck import TruckStatus


class TruckCreate(BaseModel):
    truck_number: str
    capacity: int
    current_latitude: float
    current_longitude: float
    fuel_cost_per_km: float


class TruckUpdate(BaseModel):
    capacity: Optional[int] = None
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None
    status: Optional[TruckStatus] = None
    fuel_cost_per_km: Optional[float] = None


class RouteHistoryEntrySchema(BaseModel):
    order_id: str
    from_location: str
    to_location: str
    distance_km: float
    fuel_cost: float
    delivered_at: datetime


class TruckResponse(BaseModel):
    id: str
    truck_number: str
    capacity: int
    current_latitude: float
    current_longitude: float
    status: TruckStatus
    fuel_cost_per_km: float
    route_history: List[RouteHistoryEntrySchema]
    created_at: datetime
    updated_at: datetime