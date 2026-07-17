from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import database

trucks_collection = database.get_collection("trucks")


class TruckRepository:

    @staticmethod
    async def create(truck_data: dict) -> dict:
        result = await trucks_collection.insert_one(truck_data)
        return await trucks_collection.find_one({"_id": result.inserted_id})

    @staticmethod
    async def get_by_id(truck_id: str) -> Optional[dict]:
        return await trucks_collection.find_one({"_id": ObjectId(truck_id)})

    @staticmethod
    async def get_all(skip: int = 0, limit: int = 50) -> List[dict]:
        cursor = trucks_collection.find().skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    @staticmethod
    async def get_idle_trucks() -> List[dict]:
        cursor = trucks_collection.find({"status": "idle"})
        return await cursor.to_list(length=100)

    @staticmethod
    async def update(truck_id: str, update_data: dict) -> Optional[dict]:
        update_data["updated_at"] = datetime.utcnow()
        await trucks_collection.update_one(
            {"_id": ObjectId(truck_id)},
            {"$set": update_data},
        )
        return await trucks_collection.find_one({"_id": ObjectId(truck_id)})

    @staticmethod
    async def set_status(truck_id: str, status: str) -> Optional[dict]:
        await trucks_collection.update_one(
            {"_id": ObjectId(truck_id)},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}},
        )
        return await trucks_collection.find_one({"_id": ObjectId(truck_id)})

    @staticmethod
    async def add_route_history(truck_id: str, entry: dict) -> Optional[dict]:
        await trucks_collection.update_one(
            {"_id": ObjectId(truck_id)},
            {"$push": {"route_history": entry}, "$set": {"updated_at": datetime.utcnow()}},
        )
        return await trucks_collection.find_one({"_id": ObjectId(truck_id)})

    @staticmethod
    async def update_current_location(truck_id: str, latitude: float, longitude: float) -> Optional[dict]:
        await trucks_collection.update_one(
            {"_id": ObjectId(truck_id)},
            {
                "$set": {
                    "current_latitude": latitude,
                    "current_longitude": longitude,
                    "updated_at": datetime.utcnow(),
                }
            },
        )
        return await trucks_collection.find_one({"_id": ObjectId(truck_id)})