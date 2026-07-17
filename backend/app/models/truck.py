from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class TruckStatus(str, Enum):
    IDLE = "idle"
    EN_ROUTE = "en_route"
    DELIVERING = "delivering"
    MAINTENANCE = "maintenance"


class RouteHistoryEntry(BaseModel):
    order_id: str
    from_location: str
    to_location: str
    distance_km: float
    fuel_cost: float
    delivered_at: datetime


class TruckInDB(BaseModel):
    truck_number: str
    capacity: int
    current_latitude: float
    current_longitude: float
    status: TruckStatus = TruckStatus.IDLE
    fuel_cost_per_km: float
    route_history: List[RouteHistoryEntry] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)