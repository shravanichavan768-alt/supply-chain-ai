from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class InventoryItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int = 0


class WarehouseInDB(BaseModel):
    name: str
    location: str
    latitude: float
    longitude: float
    capacity: int
    inventory: List[InventoryItem] = Field(default_factory=list)
    manager_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)