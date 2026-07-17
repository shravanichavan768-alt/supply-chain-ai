from typing import List
from fastapi import HTTPException, status
from datetime import datetime
from app.repositories.truck_repository import TruckRepository
from app.schemas.truck import TruckCreate, TruckUpdate


class TruckService:

    @staticmethod
    async def create_truck(data: TruckCreate) -> dict:
        truck_dict = data.model_dump()
        truck_dict["status"] = "idle"
        truck_dict["route_history"] = []
        truck_dict["created_at"] = datetime.utcnow()
        truck_dict["updated_at"] = datetime.utcnow()
        return await TruckRepository.create(truck_dict)

    @staticmethod
    async def get_truck(truck_id: str) -> dict:
        truck = await TruckRepository.get_by_id(truck_id)
        if not truck:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Truck not found")
        return truck

    @staticmethod
    async def list_trucks(skip: int = 0, limit: int = 50) -> List[dict]:
        return await TruckRepository.get_all(skip, limit)

    @staticmethod
    async def update_truck(truck_id: str, data: TruckUpdate) -> dict:
        await TruckService.get_truck(truck_id)
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided to update")
        return await TruckRepository.update(truck_id, update_data)