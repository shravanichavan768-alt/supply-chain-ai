from fastapi import APIRouter, Depends, Query
from typing import List
from bson import ObjectId
from app.schemas.warehouse import (
    WarehouseCreate,
    WarehouseUpdate,
    WarehouseResponse,
    InventoryTransferRequest,
    AddStockRequest
)
from app.services.warehouse_service import WarehouseService
from app.core.deps import get_current_user, require_role
from app.models.user import UserRole

router = APIRouter(prefix="/warehouses", tags=["warehouses"])


def serialize_warehouse(warehouse: dict) -> WarehouseResponse:
    return WarehouseResponse(
        id=str(warehouse["_id"]),
        name=warehouse["name"],
        location=warehouse["location"],
        latitude=warehouse["latitude"],
        longitude=warehouse["longitude"],
        capacity=warehouse["capacity"],
        inventory=warehouse.get("inventory", []),
        manager_id=warehouse.get("manager_id"),
        created_at=warehouse["created_at"],
        updated_at=warehouse["updated_at"],
    )


@router.post("/", response_model=WarehouseResponse, status_code=201)
async def create_warehouse(
    data: WarehouseCreate,
    current_user: dict = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER)),
):
    warehouse = await WarehouseService.create_warehouse(data)
    return serialize_warehouse(warehouse)


@router.get("/", response_model=List[WarehouseResponse])
async def list_warehouses(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    current_user: dict = Depends(get_current_user),
):
    warehouses = await WarehouseService.list_warehouses(skip, limit)
    return [serialize_warehouse(w) for w in warehouses]


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(
    warehouse_id: str,
    current_user: dict = Depends(get_current_user),
):
    warehouse = await WarehouseService.get_warehouse(warehouse_id)
    return serialize_warehouse(warehouse)


@router.patch("/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(
    warehouse_id: str,
    data: WarehouseUpdate,
    current_user: dict = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER)),
):
    warehouse = await WarehouseService.update_warehouse(warehouse_id, data)
    return serialize_warehouse(warehouse)


@router.delete("/{warehouse_id}", status_code=204)
async def delete_warehouse(
    warehouse_id: str,
    current_user: dict = Depends(require_role(UserRole.ADMIN)),
):
    await WarehouseService.delete_warehouse(warehouse_id)


@router.post("/transfer")
async def transfer_inventory(
    data: InventoryTransferRequest,
    current_user: dict = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER)),
):
    return await WarehouseService.transfer_inventory(data)

@router.post("/{warehouse_id}/add-stock", response_model=WarehouseResponse)
async def add_stock(
    warehouse_id: str,
    data: AddStockRequest,
    current_user: dict = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER)),
):
    warehouse = await WarehouseService.add_stock(warehouse_id, data.product_id, data.product_name, data.quantity)
    return serialize_warehouse(warehouse)