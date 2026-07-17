import math
from typing import List
from fastapi import HTTPException, status
from datetime import datetime
from app.repositories.delivery_repository import DeliveryRepository
from app.repositories.truck_repository import TruckRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.delivery import DeliveryCreate

AVERAGE_SPEED_KMPH = 40  # baseline assumption for estimation, refined later by ML model in Module 7


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two lat/lng points in kilometers."""
    R = 6371  # Earth's radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class DeliveryService:

    @staticmethod
    async def assign_delivery(data: DeliveryCreate) -> dict:
        order = await OrderRepository.get_by_id(data.order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        truck = await TruckRepository.get_by_id(data.truck_id)
        if not truck:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Truck not found")

        if truck["status"] != "idle":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Truck {truck['truck_number']} is not available (status: {truck['status']})",
            )

        total_order_quantity = sum(item["quantity"] for item in order["items"])
        if total_order_quantity > truck["capacity"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order quantity exceeds truck capacity",
            )

        distance_km = haversine_distance_km(
            truck["current_latitude"],
            truck["current_longitude"],
            data.destination_latitude,
            data.destination_longitude,
        )
        estimated_minutes = (distance_km / AVERAGE_SPEED_KMPH) * 60

        delivery_dict = data.model_dump()
        delivery_dict["distance_km"] = round(distance_km, 2)
        delivery_dict["estimated_delivery_time_minutes"] = round(estimated_minutes, 2)
        delivery_dict["actual_delivery_time_minutes"] = None
        delivery_dict["status"] = "assigned"
        delivery_dict["created_at"] = datetime.utcnow()
        delivery_dict["updated_at"] = datetime.utcnow()

        delivery = await DeliveryRepository.create(delivery_dict)

        # Mark truck as en_route since it now has an active assignment
        await TruckRepository.set_status(data.truck_id, "en_route")

        return delivery

    @staticmethod
    async def get_delivery(delivery_id: str) -> dict:
        delivery = await DeliveryRepository.get_by_id(delivery_id)
        if not delivery:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
        return delivery

    @staticmethod
    async def list_deliveries(skip: int = 0, limit: int = 50) -> List[dict]:
        return await DeliveryRepository.get_all(skip, limit)

    @staticmethod
    async def mark_delivered(delivery_id: str, actual_minutes: float) -> dict:
        delivery = await DeliveryService.get_delivery(delivery_id)

        if delivery["status"] == "delivered":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Delivery already marked as delivered")

        updated = await DeliveryRepository.update_status(delivery_id, "delivered", actual_minutes)

        # Free up the truck and log this trip in its route history
        truck = await TruckRepository.get_by_id(delivery["truck_id"])
        fuel_cost = delivery["distance_km"] * truck["fuel_cost_per_km"]

        await TruckRepository.add_route_history(
            delivery["truck_id"],
            {
                "order_id": delivery["order_id"],
                "from_location": f"{truck['current_latitude']},{truck['current_longitude']}",
                "to_location": f"{delivery['destination_latitude']},{delivery['destination_longitude']}",
                "distance_km": delivery["distance_km"],
                "fuel_cost": round(fuel_cost, 2),
                "delivered_at": datetime.utcnow(),
            },
        )
        await TruckRepository.update_current_location(
            delivery["truck_id"], delivery["destination_latitude"], delivery["destination_longitude"]
        )
        await TruckRepository.set_status(delivery["truck_id"], "idle")

        return updated