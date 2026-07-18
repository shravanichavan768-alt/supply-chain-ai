from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class Weather(str, Enum):
    CLEAR = "clear"
    RAIN = "rain"
    STORM = "storm"


class TrafficLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SupplierDelayEvent(BaseModel):
    supplier_id: str
    delay_days: int


class SimulationDayInDB(BaseModel):
    day_number: int
    weather: Weather
    traffic_level: TrafficLevel
    is_festival: bool = False
    demand_multiplier: float = 1.0
    orders_generated: int = 0
    total_revenue: float = 0.0
    supplier_delays: List[SupplierDelayEvent] = Field(default_factory=list)
    warehouse_failures: List[str] = Field(default_factory=list)
    random_events: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SimulationStateInDB(BaseModel):
    """Singleton document tracking overall simulation state."""
    current_day: int = 0
    is_running: bool = False
    total_days_target: Optional[int] = None
    started_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)