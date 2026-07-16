from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import database

suppliers_collection = database.get_collection("suppliers")


class SupplierRepository:

    @staticmethod
    async def create(supplier_data: dict) -> dict:
        result = await suppliers_collection.insert_one(supplier_data)
        return await suppliers_collection.find_one({"_id": result.inserted_id})

    @staticmethod
    async def get_by_id(supplier_id: str) -> Optional[dict]:
        return await suppliers_collection.find_one({"_id": ObjectId(supplier_id)})

    @staticmethod
    async def get_all(skip: int = 0, limit: int = 50) -> List[dict]:
        cursor = suppliers_collection.find().skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    @staticmethod
    async def update(supplier_id: str, update_data: dict) -> Optional[dict]:
        update_data["updated_at"] = datetime.utcnow()
        await suppliers_collection.update_one(
            {"_id": ObjectId(supplier_id)},
            {"$set": update_data},
        )
        return await suppliers_collection.find_one({"_id": ObjectId(supplier_id)})

    @staticmethod
    async def delete(supplier_id: str) -> bool:
        result = await suppliers_collection.delete_one({"_id": ObjectId(supplier_id)})
        return result.deleted_count > 0

    @staticmethod
    async def adjust_reliability(supplier_id: str, delta: float) -> Optional[dict]:
        supplier = await suppliers_collection.find_one({"_id": ObjectId(supplier_id)})
        if not supplier:
            return None

        new_score = max(0, min(100, supplier["reliability_score"] + delta))
        await suppliers_collection.update_one(
            {"_id": ObjectId(supplier_id)},
            {"$set": {"reliability_score": new_score, "updated_at": datetime.utcnow()}},
        )
        return await suppliers_collection.find_one({"_id": ObjectId(supplier_id)})