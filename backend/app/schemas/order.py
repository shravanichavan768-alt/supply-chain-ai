from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from datetime import datetime
from app.models.order import OrderStatus, OrderPriority


class OrderItemSchema(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    unit_price: float


class OrderCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    items: List[OrderItemSchema]
    warehouse_id: str
    priority: OrderPriority = OrderPriority.NORMAL

    @field_validator("items")
    @classmethod
    def items_not_empty(cls, v):
        if not v:
            raise ValueError("Order must contain at least one item")
        return v


class OrderResponse(BaseModel):
    id: str
    customer_name: str
    customer_email: EmailStr
    items: List[OrderItemSchema]
    warehouse_id: str
    status: OrderStatus
    priority: OrderPriority
    is_bulk: bool
    total_amount: float
    created_at: datetime
    updated_at: datetime


class OrderStatusUpdate(BaseModel):
    status: OrderStatus