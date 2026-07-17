from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import List
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderPriority(str, Enum):
    NORMAL = "normal"
    HIGH = "high"


class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    unit_price: float


class OrderInDB(BaseModel):
    customer_name: str
    customer_email: EmailStr
    items: List[OrderItem]
    warehouse_id: str
    status: OrderStatus = OrderStatus.PENDING
    priority: OrderPriority = OrderPriority.NORMAL
    is_bulk: bool = False
    total_amount: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)