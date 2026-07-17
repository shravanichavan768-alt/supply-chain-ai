from typing import List
from fastapi import HTTPException, status
from datetime import datetime
from app.repositories.order_repository import OrderRepository
from app.repositories.warehouse_repository import WarehouseRepository
from app.schemas.order import OrderCreate

BULK_ORDER_THRESHOLD = 100  # total quantity across items to be considered "bulk"


class OrderService:

    @staticmethod
    async def place_order(data: OrderCreate) -> dict:
        warehouse = await WarehouseRepository.get_by_id(data.warehouse_id)
        if not warehouse:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found")

        # Validate stock availability for every item BEFORE deducting anything
        for item in data.items:
            stock_item = next(
                (inv for inv in warehouse["inventory"] if inv["product_id"] == item.product_id), None
            )
            available = stock_item["quantity"] if stock_item else 0
            if available < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for {item.product_name} "
                    f"(requested {item.quantity}, available {available})",
                )

        # All items validated — now deduct stock for each
        for item in data.items:
            await WarehouseRepository.update_inventory_quantity(
                data.warehouse_id, item.product_id, -item.quantity
            )

        total_amount = sum(item.quantity * item.unit_price for item in data.items)
        total_quantity = sum(item.quantity for item in data.items)

        order_dict = data.model_dump()
        order_dict["total_amount"] = total_amount
        order_dict["is_bulk"] = total_quantity >= BULK_ORDER_THRESHOLD
        order_dict["status"] = "pending"
        order_dict["created_at"] = datetime.utcnow()
        order_dict["updated_at"] = datetime.utcnow()

        return await OrderRepository.create(order_dict)

    @staticmethod
    async def get_order(order_id: str) -> dict:
        order = await OrderRepository.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return order

    @staticmethod
    async def list_orders(skip: int = 0, limit: int = 50) -> List[dict]:
        return await OrderRepository.get_all(skip, limit)

    @staticmethod
    async def get_customer_history(email: str, skip: int = 0, limit: int = 50) -> List[dict]:
        return await OrderRepository.get_by_customer_email(email, skip, limit)

    @staticmethod
    async def cancel_order(order_id: str) -> dict:
        order = await OrderService.get_order(order_id)

        if order["status"] in ["shipped", "delivered", "cancelled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel an order with status '{order['status']}'",
            )

        # Restock items back to warehouse since order is being cancelled
        for item in order["items"]:
            existing = await WarehouseRepository.get_by_id(order["warehouse_id"])
            has_product = any(inv["product_id"] == item["product_id"] for inv in existing["inventory"])
            if has_product:
                await WarehouseRepository.update_inventory_quantity(
                    order["warehouse_id"], item["product_id"], item["quantity"]
                )
            else:
                await WarehouseRepository.add_new_product_to_inventory(
                    order["warehouse_id"], item["product_id"], item["product_name"], item["quantity"]
                )

        return await OrderRepository.update_status(order_id, "cancelled")

    @staticmethod
    async def update_status(order_id: str, new_status: str) -> dict:
        await OrderService.get_order(order_id)  # raises 404 if missing
        return await OrderRepository.update_status(order_id, new_status)