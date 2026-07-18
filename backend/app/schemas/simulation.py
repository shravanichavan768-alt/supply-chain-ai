from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from app.models.simulation import Weather, TrafficLevel, SupplierDelayEvent


class SimulationDayResponse(BaseModel):
    id: str
    day_number: int
    weather: Weather
    traffic_level: TrafficLevel
    is_festival: bool
    demand_multiplier: float
    orders_generated: int
    total_revenue: float
    supplier_delays: List[SupplierDelayEvent]
    warehouse_failures: List[str]
    random_events: List[str]
    created_at: datetime


class SimulationStateResponse(BaseModel):
    current_day: int
    is_running: bool
    total_days_target: Optional[int]
    started_at: Optional[datetime]
    updated_at: datetime


class RunSimulationRequest(BaseModel):
    num_days: int = 1  # how many virtual days to advance in this call