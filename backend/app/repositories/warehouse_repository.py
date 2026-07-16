from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import database

warehouses_collection = database.get_collection("warehouses")


class WarehouseRepository:

    @staticmethod
    async def create(warehouse_data: dict) -> dict:
        result = await warehouses_collection.insert_one(warehouse_data)
        created = await warehouses_collection.find_one({"_id": result.inserted_id})
        return created

    @staticmethod
    async def get_by_id(warehouse_id: str) -> Optional[dict]:
        return await warehouses_collection.find_one({"_id": ObjectId(warehouse_id)})

    @staticmethod
    async def get_all(skip: int = 0, limit: int = 50) -> List[dict]:
        cursor = warehouses_collection.find().skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    @staticmethod
    async def update(warehouse_id: str, update_data: dict) -> Optional[dict]:
        update_data["updated_at"] = datetime.utcnow()
        await warehouses_collection.update_one(
            {"_id": ObjectId(warehouse_id)},
            {"$set": update_data},
        )
        return await warehouses_collection.find_one({"_id": ObjectId(warehouse_id)})

    @staticmethod
    async def delete(warehouse_id: str) -> bool:
        result = await warehouses_collection.delete_one({"_id": ObjectId(warehouse_id)})
        return result.deleted_count > 0

    @staticmethod
    async def update_inventory_quantity(warehouse_id: str, product_id: str, quantity_delta: int) -> Optional[dict]:
        """
        Increment/decrement quantity of a specific product in a warehouse's inventory array.
        Positive quantity_delta = add stock, negative = remove stock.
        """
        result = await warehouses_collection.update_one(
            {"_id": ObjectId(warehouse_id), "inventory.product_id": product_id},
            {"$inc": {"inventory.$.quantity": quantity_delta}, "$set": {"updated_at": datetime.utcnow()}},
        )
        if result.matched_count == 0:
            # product not yet in inventory array, push new entry (only valid for positive delta)
            return None
        return await warehouses_collection.find_one({"_id": ObjectId(warehouse_id)})
    
    @staticmethod
    async def add_new_product_to_inventory(warehouse_id: str, product_id: str, product_name: str, quantity: int) -> Optional[dict]:
        await warehouses_collection.update_one(
            {"_id": ObjectId(warehouse_id)},
            {
                "$push": {"inventory": {"product_id": product_id, "product_name": product_name, "quantity": quantity}},
                "$set": {"updated_at": datetime.utcnow()},
            },
        )
        return await warehouses_collection.find_one({"_id": ObjectId(warehouse_id)})