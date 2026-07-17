from fastapi import APIRouter, Depends, Query
from typing import List
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from app.services.order_service import OrderService
from app.core.deps import get_current_user, require_role
from app.models.user import UserRole

router = APIRouter(prefix="/orders", tags=["orders"])


def serialize_order(order: dict) -> OrderResponse:
    return OrderResponse(
        id=str(order["_id"]),
        customer_name=order["customer_name"],
        customer_email=order["customer_email"],
        items=order["items"],
        warehouse_id=order["warehouse_id"],
        status=order["status"],
        priority=order["priority"],
        is_bulk=order["is_bulk"],
        total_amount=order["total_amount"],
        created_at=order["created_at"],
        updated_at=order["updated_at"],
    )


@router.post("/", response_model=OrderResponse, status_code=201)
async def place_order(
    data: OrderCreate,
    current_user: dict = Depends(get_current_user),
):
    order = await OrderService.place_order(data)
    return serialize_order(order)


@router.get("/", response_model=List[OrderResponse])
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    current_user: dict = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER)),
):
    orders = await OrderService.list_orders(skip, limit)
    return [serialize_order(o) for o in orders]


@router.get("/history/{customer_email}", response_model=List[OrderResponse])
async def customer_order_history(
    customer_email: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    current_user: dict = Depends(get_current_user),
):
    orders = await OrderService.get_customer_history(customer_email, skip, limit)
    return [serialize_order(o) for o in orders]


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: dict = Depends(get_current_user),
):
    order = await OrderService.get_order(order_id)
    return serialize_order(order)


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    data: OrderStatusUpdate,
    current_user: dict = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER)),
):
    order = await OrderService.update_status(order_id, data.status.value)
    return serialize_order(order)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    current_user: dict = Depends(get_current_user),
):
    order = await OrderService.cancel_order(order_id)
    return serialize_order(order)