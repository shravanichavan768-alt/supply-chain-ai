from typing import List
from fastapi import HTTPException, status
from datetime import datetime
from app.repositories.supplier_repository import SupplierRepository
from app.schemas.supplier import SupplierCreate, SupplierUpdate


class SupplierService:

    @staticmethod
    async def create_supplier(data: SupplierCreate) -> dict:
        supplier_dict = data.model_dump()
        supplier_dict["reliability_score"] = 100.0
        supplier_dict["created_at"] = datetime.utcnow()
        supplier_dict["updated_at"] = datetime.utcnow()
        return await SupplierRepository.create(supplier_dict)

    @staticmethod
    async def get_supplier(supplier_id: str) -> dict:
        supplier = await SupplierRepository.get_by_id(supplier_id)
        if not supplier:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
        return supplier

    @staticmethod
    async def list_suppliers(skip: int = 0, limit: int = 50) -> List[dict]:
        return await SupplierRepository.get_all(skip, limit)

    @staticmethod
    async def update_supplier(supplier_id: str, data: SupplierUpdate) -> dict:
        await SupplierService.get_supplier(supplier_id)  # raises 404 if missing
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided to update")
        return await SupplierRepository.update(supplier_id, update_data)

    @staticmethod
    async def delete_supplier(supplier_id: str) -> None:
        deleted = await SupplierRepository.delete(supplier_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")

    @staticmethod
    async def adjust_reliability(supplier_id: str, delta: float, reason: str) -> dict:
        await SupplierService.get_supplier(supplier_id)  # raises 404 if missing
        updated = await SupplierRepository.adjust_reliability(supplier_id, delta)
        # In a later phase, we'll log this adjustment (supplier_id, delta, reason, timestamp)
        # to a separate "reliability_history" collection for audit/analytics purposes.
        return updated