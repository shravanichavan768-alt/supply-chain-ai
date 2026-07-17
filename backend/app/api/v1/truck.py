from fastapi import APIRouter, Depends, Query
from typing import List
from app.schemas.truck import TruckCreate, TruckUpdate, TruckResponse
from app.services.truck_service import TruckService
from app.core.deps import get_current_user, require_role
from app.models.user import UserRole

router = APIRouter(prefix="/trucks", tags=["trucks"])


def serialize_truck(truck: dict) -> TruckResponse:
    return TruckResponse(
        id=str(truck["_id"]),
        truck_number=truck["truck_number"],
        capacity=truck["capacity"],
        current_latitude=truck["current_latitude"],
        current_longitude=truck["current_longitude"],
        status=truck["status"],
        fuel_cost_per_km=truck["fuel_cost_per_km"],
        route_history=truck.get("route_history", []),
        created_at=truck["created_at"],
        updated_at=truck["updated_at"],
    )


@router.post("/", response_model=TruckResponse, status_code=201)
async def create_truck(
    data: TruckCreate,
    current_user: dict = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER)),
):
    truck = await TruckService.create_truck(data)
    return serialize_truck(truck)


@router.get("/", response_model=List[TruckResponse])
async def list_trucks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    current_user: dict = Depends(get_current_user),
):
    trucks = await TruckService.list_trucks(skip, limit)
    return [serialize_truck(t) for t in trucks]


@router.get("/{truck_id}", response_model=TruckResponse)
async def get_truck(
    truck_id: str,
    current_user: dict = Depends(get_current_user),
):
    truck = await TruckService.get_truck(truck_id)
    return serialize_truck(truck)


@router.patch("/{truck_id}", response_model=TruckResponse)
async def update_truck(
    truck_id: str,
    data: TruckUpdate,
    current_user: dict = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER)),
):
    truck = await TruckService.update_truck(truck_id, data)
    return serialize_truck(truck)