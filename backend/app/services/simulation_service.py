import random
from typing import List
from datetime import datetime
from fastapi import HTTPException, status
from app.repositories.simulation_repository import SimulationRepository
from app.repositories.warehouse_repository import WarehouseRepository
from app.repositories.supplier_repository import SupplierRepository
from app.models.simulation import Weather, TrafficLevel

RANDOM_EVENT_POOL = [
    "Port congestion delayed inbound shipments",
    "Local holiday reduced warehouse staff availability",
    "Fuel price spike increased delivery costs",
    "New product line launched, minor demand uptick",
    "Regional strike affected trucking routes",
    "Currency fluctuation affected import costs",
]

PRODUCT_CATALOG = [
    {"product_id": "PROD-001", "product_name": "Wireless Mouse", "base_price": 15.99},
    {"product_id": "PROD-002", "product_name": "Bluetooth Keyboard", "base_price": 29.99},
    {"product_id": "PROD-003", "product_name": "USB-C Hub", "base_price": 22.50},
    {"product_id": "PROD-004", "product_name": "Laptop Stand", "base_price": 34.99},
]

FESTIVAL_DAY_INTERVAL = 30  # roughly one festival every 30 virtual days


class SimulationService:

    @staticmethod
    async def get_state() -> dict:
        return await SimulationRepository.initialize_state_if_missing()

    @staticmethod
    async def reset_simulation() -> dict:
        await SimulationRepository.delete_all_days()
        return await SimulationRepository.reset_state()

    @staticmethod
    async def run_days(num_days: int) -> List[dict]:
        state = await SimulationRepository.initialize_state_if_missing()
        current_day = state["current_day"]

        if not state.get("started_at"):
            await SimulationRepository.update_state({"started_at": datetime.utcnow(), "is_running": True})

        results = []
        for _ in range(num_days):
            current_day += 1
            day_result = await SimulationService._simulate_single_day(current_day)
            results.append(day_result)

        await SimulationRepository.update_state({"current_day": current_day, "is_running": False})
        return results

    @staticmethod
    async def _simulate_single_day(day_number: int) -> dict:
        
        weather = random.choices(
            [Weather.CLEAR, Weather.RAIN, Weather.STORM],
            weights=[0.7, 0.25, 0.05],
        )[0]
        traffic = random.choices(
            [TrafficLevel.LOW, TrafficLevel.MEDIUM, TrafficLevel.HIGH],
            weights=[0.4, 0.4, 0.2],
        )[0]
        is_festival = day_number % FESTIVAL_DAY_INTERVAL == 0

        demand_multiplier = 1.0
        if is_festival:
            demand_multiplier *= 2.5
        if weather == Weather.STORM:
            demand_multiplier *= 0.6  # people order less during storms
        if traffic == TrafficLevel.HIGH:
            demand_multiplier *= 0.9  # slight dampening, deliveries backed up

        
        base_order_count = random.randint(5, 15)
        orders_to_generate = max(1, int(base_order_count * demand_multiplier))
        orders_generated, total_revenue = await SimulationService._generate_orders(orders_to_generate)

        supplier_delays = await SimulationService._generate_supplier_delays()

        warehouse_failures = await SimulationService._generate_warehouse_failures()

     
        random_events = []
        if random.random() < 0.15:  # 15% chance per day
            random_events.append(random.choice(RANDOM_EVENT_POOL))

        day_data = {
            "day_number": day_number,
            "weather": weather.value,
            "traffic_level": traffic.value,
            "is_festival": is_festival,
            "demand_multiplier": round(demand_multiplier, 2),
            "orders_generated": orders_generated,
            "total_revenue": round(total_revenue, 2),
            "supplier_delays": supplier_delays,
            "warehouse_failures": warehouse_failures,
            "random_events": random_events,
            "created_at": datetime.utcnow(),
        }

        return await SimulationRepository.create_day(day_data)

    @staticmethod
    async def _generate_orders(count: int) -> tuple:
        
        from app.repositories.truck_repository import TruckRepository
        from app.repositories.order_repository import OrderRepository
        from app.repositories.delivery_repository import DeliveryRepository
        from app.services.delivery_service import haversine_distance_km
        import random as rnd

        warehouses = await WarehouseRepository.get_all(limit=100)
        if not warehouses:
            return 0, 0.0

        successful_orders = 0
        total_revenue = 0.0

        for _ in range(count):
            warehouse = random.choice(warehouses)
            product = random.choice(PRODUCT_CATALOG)
            quantity = random.randint(1, 10)

            stock_item = next(
                (inv for inv in warehouse["inventory"] if inv["product_id"] == product["product_id"]), None
            )
            available = stock_item["quantity"] if stock_item else 0

            if available >= quantity:
                await WarehouseRepository.update_inventory_quantity(
                    str(warehouse["_id"]), product["product_id"], -quantity
                )
                revenue = quantity * product["base_price"]
                total_revenue += revenue
                successful_orders += 1
                stock_item["quantity"] -= quantity

                order_doc = {
                    "customer_name": f"Simulated Customer {rnd.randint(1000, 9999)}",
                    "customer_email": f"sim{rnd.randint(1000, 9999)}@example.com",
                    "items": [{
                        "product_id": product["product_id"],
                        "product_name": product["product_name"],
                        "quantity": quantity,
                        "unit_price": product["base_price"],
                    }],
                    "warehouse_id": str(warehouse["_id"]),
                    "status": "delivered",
                    "priority": "high" if quantity >= 8 else "normal",
                    "is_bulk": quantity >= 8,
                    "total_amount": revenue,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
                created_order = await OrderRepository.create(order_doc)

                
                trucks = await TruckRepository.get_all(limit=100)
                warehouse_trucks = [t for t in trucks if abs(t["current_latitude"] - warehouse["latitude"]) < 1]
                if warehouse_trucks:
                    truck = random.choice(warehouse_trucks)

                    dest_lat = warehouse["latitude"] + random.uniform(-0.15, 0.15)
                    dest_lng = warehouse["longitude"] + random.uniform(-0.15, 0.15)
                    distance = haversine_distance_km(
                        warehouse["latitude"], warehouse["longitude"], dest_lat, dest_lng
                    )

                    
                    base_speed = 40
                    actual_minutes = (distance / base_speed) * 60 * random.uniform(0.9, 1.4)

                    delivery_doc = {
                        "order_id": str(created_order["_id"]),
                        "truck_id": str(truck["_id"]),
                        "warehouse_id": str(warehouse["_id"]),
                        "destination_latitude": dest_lat,
                        "destination_longitude": dest_lng,
                        "distance_km": round(distance, 2),
                        "status": "delivered",
                        "estimated_delivery_time_minutes": round((distance / base_speed) * 60, 2),
                        "actual_delivery_time_minutes": round(actual_minutes, 2),
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                    }
                    await DeliveryRepository.create(delivery_doc)

        return successful_orders, total_revenue

    @staticmethod
    async def _generate_supplier_delays() -> list:
        suppliers = await SupplierRepository.get_all(limit=100)
        delays = []
        for supplier in suppliers:
            # Lower reliability = higher chance of delay
            delay_probability = (100 - supplier["reliability_score"]) / 300  # tuned to keep delays infrequent
            if random.random() < delay_probability:
                delay_days = random.randint(1, 5)
                delays.append({"supplier_id": str(supplier["_id"]), "delay_days": delay_days})
                await SupplierRepository.adjust_reliability(str(supplier["_id"]), -3)
        return delays

    @staticmethod
    async def _generate_warehouse_failures() -> list:
        warehouses = await WarehouseRepository.get_all(limit=100)
        failures = []
        for warehouse in warehouses:
            if random.random() < 0.02:  # 2% chance per warehouse per day
                failures.append(str(warehouse["_id"]))
        return failures

    @staticmethod
    async def get_day(day_number: int) -> dict:
        day = await SimulationRepository.get_day(day_number)
        if not day:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation day not found")
        return day

    @staticmethod
    async def get_recent_days(limit: int = 30) -> List[dict]:
        return await SimulationRepository.get_recent_days(limit)