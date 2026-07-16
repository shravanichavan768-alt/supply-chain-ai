from fastapi import APIRouter, Depends, Query
from typing import List
from app.schemas.supplier import (
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse,
    ReliabilityAdjustment,
)
from app.services.supplier_service import SupplierService
from app.core.deps import get_current_user, require_role
from app.models.user import UserRole

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


def serialize_supplier(supplier: dict) -> SupplierResponse:
    return SupplierResponse(
        id=str(supplier["_id"]),
        name=supplier["name"],
        contact_email=supplier["contact_email"],
        contact_phone=supplier["contact_phone"],
        production_capacity=supplier["production_capacity"],
        lead_time_days=supplier["lead_time_days"],
        cost_per_unit=supplier["cost_per_unit"],
        reliability_score=supplier["reliability_score"],
        products_supplied=supplier.get("products_supplied", []),
        created_at=supplier["created_at"],
        updated_at=supplier["updated_at"],
    )


@router.post("/", response_model=SupplierResponse, status_code=201)
async def create_supplier(
    data: SupplierCreate,
    current_user: dict = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER)),
):
    supplier = await SupplierService.create_supplier(data)
    return serialize_supplier(supplier)


@router.get("/", response_model=List[SupplierResponse])
async def list_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    current_user: dict = Depends(get_current_user),
):
    suppliers = await SupplierService.list_suppliers(skip, limit)
    return [serialize_supplier(s) for s in suppliers]


@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: str,
    current_user: dict = Depends(get_current_user),
):
    supplier = await SupplierService.get_supplier(supplier_id)
    return serialize_supplier(supplier)


@router.patch("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: str,
    data: SupplierUpdate,
    current_user: dict = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER)),
):
    supplier = await SupplierService.update_supplier(supplier_id, data)
    return serialize_supplier(supplier)


@router.delete("/{supplier_id}", status_code=204)
async def delete_supplier(
    supplier_id: str,
    current_user: dict = Depends(require_role(UserRole.ADMIN)),
):
    await SupplierService.delete_supplier(supplier_id)


@router.post("/{supplier_id}/adjust-reliability", response_model=SupplierResponse)
async def adjust_reliability(
    supplier_id: str,
    data: ReliabilityAdjustment,
    current_user: dict = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER)),
):
    supplier = await SupplierService.adjust_reliability(supplier_id, data.delta, data.reason)
    return serialize_supplier(supplier)