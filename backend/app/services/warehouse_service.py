from typing import List, Optional
from fastapi import HTTPException, status
from app.repositories.warehouse_repository import WarehouseRepository
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate, InventoryTransferRequest
from datetime import datetime

class WarehouseService:

    @staticmethod
    async def create_warehouse(data: WarehouseCreate) -> dict:
       warehouse_dict = data.model_dump()
       warehouse_dict["inventory"] = []
       warehouse_dict["created_at"] = datetime.utcnow()
       warehouse_dict["updated_at"] = datetime.utcnow()
       return await WarehouseRepository.create(warehouse_dict)

    @staticmethod
    async def get_warehouse(warehouse_id: str) -> dict:
        warehouse = await WarehouseRepository.get_by_id(warehouse_id)
        if not warehouse:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found")
        return warehouse

    @staticmethod
    async def list_warehouses(skip: int = 0, limit: int = 50) -> List[dict]:
        return await WarehouseRepository.get_all(skip, limit)

    @staticmethod
    async def update_warehouse(warehouse_id: str, data: WarehouseUpdate) -> dict:
        await WarehouseService.get_warehouse(warehouse_id)  # raises 404 if missing
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided to update")
        return await WarehouseRepository.update(warehouse_id, update_data)

    @staticmethod
    async def delete_warehouse(warehouse_id: str) -> None:
        deleted = await WarehouseRepository.delete(warehouse_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found")

    @staticmethod
    async def transfer_inventory(data: InventoryTransferRequest) -> dict:
        from_warehouse = await WarehouseService.get_warehouse(data.from_warehouse_id)

        # Validate source has enough stock
        source_item = next(
            (item for item in from_warehouse["inventory"] if item["product_id"] == data.product_id), None
        )
        if not source_item or source_item["quantity"] < data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock in source warehouse for this transfer",
            )

        # Validate destination has capacity
        to_warehouse = await WarehouseService.get_warehouse(data.to_warehouse_id)
        current_total = sum(item["quantity"] for item in to_warehouse["inventory"])
        if current_total + data.quantity > to_warehouse["capacity"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Destination warehouse does not have enough capacity",
            )

        # Perform transfer
        await WarehouseRepository.update_inventory_quantity(data.from_warehouse_id, data.product_id, -data.quantity)

        destination_has_product = any(
            item["product_id"] == data.product_id for item in to_warehouse["inventory"]
        )
        if destination_has_product:
            await WarehouseRepository.update_inventory_quantity(data.to_warehouse_id, data.product_id, data.quantity)
        else:
            product_name = source_item["product_name"]
            await WarehouseRepository.add_new_product_to_inventory(
                data.to_warehouse_id, data.product_id, product_name, data.quantity
            )

        return {
            "message": f"Transferred {data.quantity} units of {data.product_id} "
            f"from {data.from_warehouse_id} to {data.to_warehouse_id}"
        }
    
    @staticmethod
    async def add_stock(warehouse_id: str, product_id: str, product_name: str, quantity: int) -> dict:
        warehouse = await WarehouseService.get_warehouse(warehouse_id)

        existing_item = next((item for item in warehouse["inventory"] if item["product_id"] == product_id), None)

        current_total = sum(item["quantity"] for item in warehouse["inventory"])
        if current_total + quantity > warehouse["capacity"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Adding this stock would exceed warehouse capacity",
            )

        if existing_item:
            return await WarehouseRepository.update_inventory_quantity(warehouse_id, product_id, quantity)
        else:
            return await WarehouseRepository.add_new_product_to_inventory(warehouse_id, product_id, product_name, quantity)