from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import database

orders_collection = database.get_collection("orders")


class OrderRepository:

    @staticmethod
    async def create(order_data: dict) -> dict:
        result = await orders_collection.insert_one(order_data)
        return await orders_collection.find_one({"_id": result.inserted_id})

    @staticmethod
    async def get_by_id(order_id: str) -> Optional[dict]:
        return await orders_collection.find_one({"_id": ObjectId(order_id)})

    @staticmethod
    async def get_all(skip: int = 0, limit: int = 50) -> List[dict]:
        cursor = orders_collection.find().sort("created_at", -1).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    @staticmethod
    async def get_by_customer_email(email: str, skip: int = 0, limit: int = 50) -> List[dict]:
        cursor = orders_collection.find({"customer_email": email}).sort("created_at", -1).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    @staticmethod
    async def update_status(order_id: str, status: str) -> Optional[dict]:
        await orders_collection.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}},
        )
        return await orders_collection.find_one({"_id": ObjectId(order_id)})