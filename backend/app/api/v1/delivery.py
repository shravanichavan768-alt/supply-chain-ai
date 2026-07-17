from fastapi import APIRouter, Depends, Query
from typing import List
from app.schemas.delivery import DeliveryCreate, DeliveryResponse
from app.services.delivery_service import DeliveryService
from app.core.deps import get_current_user, require_role
from app.models.user import UserRole

router = APIRouter(prefix="/deliveries", tags=["deliveries"])


def serialize_delivery(delivery: dict) -> DeliveryResponse:
    return DeliveryResponse(
        id=str(delivery["_id"]),
        order_id=delivery["order_id"],
        truck_id=delivery["truck_id"],
        warehouse_id=delivery["warehouse_id"],
        destination_latitude=delivery["destination_latitude"],
        destination_longitude=delivery["destination_longitude"],
        distance_km=delivery["distance_km"],
        status=delivery["status"],
        estimated_delivery_time_minutes=delivery.get("estimated_delivery_time_minutes"),
        actual_delivery_time_minutes=delivery.get("actual_delivery_time_minutes"),
        created_at=delivery["created_at"],
        updated_at=delivery["updated_at"],
    )


@router.post("/", response_model=DeliveryResponse, status_code=201)
async def assign_delivery(
    data: DeliveryCreate,
    current_user: dict = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER)),
):
    delivery = await DeliveryService.assign_delivery(data)
    return serialize_delivery(delivery)


@router.get("/", response_model=List[DeliveryResponse])
async def list_deliveries(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    current_user: dict = Depends(get_current_user),
):
    deliveries = await DeliveryService.list_deliveries(skip, limit)
    return [serialize_delivery(d) for d in deliveries]


@router.get("/{delivery_id}", response_model=DeliveryResponse)
async def get_delivery(
    delivery_id: str,
    current_user: dict = Depends(get_current_user),
):
    delivery = await DeliveryService.get_delivery(delivery_id)
    return serialize_delivery(delivery)


@router.post("/{delivery_id}/deliver", response_model=DeliveryResponse)
async def mark_delivered(
    delivery_id: str,
    actual_minutes: float,
    current_user: dict = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER)),
):
    delivery = await DeliveryService.mark_delivered(delivery_id, actual_minutes)
    return serialize_delivery(delivery)