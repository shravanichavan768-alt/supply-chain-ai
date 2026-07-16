from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class InventoryItemSchema(BaseModel):
    product_id: str
    product_name: str
    quantity: int = 0


class WarehouseCreate(BaseModel):
    name: str
    location: str
    latitude: float
    longitude: float
    capacity: int
    manager_id: Optional[str] = None


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    capacity: Optional[int] = None
    manager_id: Optional[str] = None


class WarehouseResponse(BaseModel):
    id: str
    name: str
    location: str
    latitude: float
    longitude: float
    capacity: int
    inventory: List[InventoryItemSchema]
    manager_id: Optional[str]
    created_at: datetime
    updated_at: datetime


class InventoryTransferRequest(BaseModel):
    from_warehouse_id: str
    to_warehouse_id: str
    product_id: str
    quantity: int

class AddStockRequest(BaseModel):
    product_id: str
    product_name: str
    quantity: int