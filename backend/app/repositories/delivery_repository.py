from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import database

deliveries_collection = database.get_collection("deliveries")


class DeliveryRepository:

    @staticmethod
    async def create(delivery_data: dict) -> dict:
        result = await deliveries_collection.insert_one(delivery_data)
        return await deliveries_collection.find_one({"_id": result.inserted_id})

    @staticmethod
    async def get_by_id(delivery_id: str) -> Optional[dict]:
        return await deliveries_collection.find_one({"_id": ObjectId(delivery_id)})

    @staticmethod
    async def get_all(skip: int = 0, limit: int = 50) -> List[dict]:
        cursor = deliveries_collection.find().sort("created_at", -1).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    @staticmethod
    async def update_status(delivery_id: str, status: str, actual_time: Optional[float] = None) -> Optional[dict]:
        update_fields = {"status": status, "updated_at": datetime.utcnow()}
        if actual_time is not None:
            update_fields["actual_delivery_time_minutes"] = actual_time

        await deliveries_collection.update_one(
            {"_id": ObjectId(delivery_id)},
            {"$set": update_fields},
        )
        return await deliveries_collection.find_one({"_id": ObjectId(delivery_id)})