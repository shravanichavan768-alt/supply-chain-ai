from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import database

simulation_days_collection = database.get_collection("simulation_days")
simulation_state_collection = database.get_collection("simulation_state")

STATE_DOC_ID = "singleton_state"  # fixed ID so there's always exactly one state document


class SimulationRepository:

    @staticmethod
    async def get_state() -> Optional[dict]:
        return await simulation_state_collection.find_one({"_id": STATE_DOC_ID})

    @staticmethod
    async def initialize_state_if_missing() -> dict:
        existing = await simulation_state_collection.find_one({"_id": STATE_DOC_ID})
        if existing:
            return existing

        initial_state = {
            "_id": STATE_DOC_ID,
            "current_day": 0,
            "is_running": False,
            "total_days_target": None,
            "started_at": None,
            "updated_at": datetime.utcnow(),
        }
        await simulation_state_collection.insert_one(initial_state)
        return initial_state

    @staticmethod
    async def update_state(update_data: dict) -> dict:
        update_data["updated_at"] = datetime.utcnow()
        await simulation_state_collection.update_one(
            {"_id": STATE_DOC_ID},
            {"$set": update_data},
            upsert=True,
        )
        return await simulation_state_collection.find_one({"_id": STATE_DOC_ID})

    @staticmethod
    async def reset_state() -> dict:
        reset_data = {
            "current_day": 0,
            "is_running": False,
            "total_days_target": None,
            "started_at": None,
            "updated_at": datetime.utcnow(),
        }
        await simulation_state_collection.update_one(
            {"_id": STATE_DOC_ID},
            {"$set": reset_data},
            upsert=True,
        )
        return reset_data

    @staticmethod
    async def create_day(day_data: dict) -> dict:
        result = await simulation_days_collection.insert_one(day_data)
        return await simulation_days_collection.find_one({"_id": result.inserted_id})

    @staticmethod
    async def get_day(day_number: int) -> Optional[dict]:
        return await simulation_days_collection.find_one({"day_number": day_number})

    @staticmethod
    async def get_days_range(start: int, end: int) -> List[dict]:
        cursor = simulation_days_collection.find(
            {"day_number": {"$gte": start, "$lte": end}}
        ).sort("day_number", 1)
        return await cursor.to_list(length=end - start + 1)

    @staticmethod
    async def get_recent_days(limit: int = 30) -> List[dict]:
        cursor = simulation_days_collection.find().sort("day_number", -1).limit(limit)
        days = await cursor.to_list(length=limit)
        return list(reversed(days))  # chronological order for charts

    @staticmethod
    async def delete_all_days() -> None:
        await simulation_days_collection.delete_many({})