
import asyncio
from datetime import datetime
from app.db.mongodb import database

warehouses_collection = database.get_collection("warehouses")
suppliers_collection = database.get_collection("suppliers")
trucks_collection = database.get_collection("trucks")

PRODUCTS = [
    {"product_id": "PROD-001", "product_name": "Wireless Mouse"},
    {"product_id": "PROD-002", "product_name": "Bluetooth Keyboard"},
    {"product_id": "PROD-003", "product_name": "USB-C Hub"},
    {"product_id": "PROD-004", "product_name": "Laptop Stand"},
]

WAREHOUSES = [
    {"name": "Mumbai Central Warehouse", "location": "Mumbai, Maharashtra", "latitude": 19.0760, "longitude": 72.8777, "capacity": 10000},
    {"name": "Pune Warehouse", "location": "Pune, Maharashtra", "latitude": 18.5204, "longitude": 73.8567, "capacity": 5000},
    {"name": "Delhi NCR Warehouse", "location": "Delhi", "latitude": 28.7041, "longitude": 77.1025, "capacity": 12000},
    {"name": "Bangalore Warehouse", "location": "Bangalore, Karnataka", "latitude": 12.9716, "longitude": 77.5946, "capacity": 8000},
]

SUPPLIERS = [
    {"name": "TechParts Manufacturing", "contact_email": "sales@techparts.com", "contact_phone": "+91-9876543210", "production_capacity": 5000, "lead_time_days": 7, "cost_per_unit": 12.50, "reliability_score": 95.0, "products_supplied": ["PROD-001", "PROD-002"]},
    {"name": "Global Electronics Supply", "contact_email": "contact@globalelec.com", "contact_phone": "+91-9876543211", "production_capacity": 8000, "lead_time_days": 5, "cost_per_unit": 18.00, "reliability_score": 88.0, "products_supplied": ["PROD-003", "PROD-004"]},
    {"name": "Budget Peripherals Co", "contact_email": "info@budgetperipherals.com", "contact_phone": "+91-9876543212", "production_capacity": 3000, "lead_time_days": 10, "cost_per_unit": 9.00, "reliability_score": 70.0, "products_supplied": ["PROD-001"]},
    {"name": "Premium Tech Components", "contact_email": "sales@premiumtech.com", "contact_phone": "+91-9876543213", "production_capacity": 4000, "lead_time_days": 4, "cost_per_unit": 25.00, "reliability_score": 98.0, "products_supplied": ["PROD-002", "PROD-003", "PROD-004"]},
    {"name": "Regional Distributors Ltd", "contact_email": "orders@regionaldist.com", "contact_phone": "+91-9876543214", "production_capacity": 6000, "lead_time_days": 8, "cost_per_unit": 14.75, "reliability_score": 80.0, "products_supplied": ["PROD-001", "PROD-003"]},
]

TRUCK_COUNT_PER_WAREHOUSE = 2


async def seed():
    print("Seeding warehouses...")
    for w in WAREHOUSES:
        w["inventory"] = [
            {"product_id": p["product_id"], "product_name": p["product_name"], "quantity": 800}
            for p in PRODUCTS
        ]
        w["manager_id"] = None
        w["created_at"] = datetime.utcnow()
        w["updated_at"] = datetime.utcnow()
        await warehouses_collection.insert_one(w)
        print(f"  Created warehouse: {w['name']}")

    print("Seeding suppliers...")
    for s in SUPPLIERS:
        s["created_at"] = datetime.utcnow()
        s["updated_at"] = datetime.utcnow()
        await suppliers_collection.insert_one(s)
        print(f"  Created supplier: {s['name']} (reliability: {s['reliability_score']})")

    print("Seeding trucks...")
    for w in WAREHOUSES:
        for i in range(TRUCK_COUNT_PER_WAREHOUSE):
            truck = {
                "truck_number": f"{w['location'][:2].upper()}-TRUCK-{i+1}",
                "capacity": 300,
                "current_latitude": w["latitude"],
                "current_longitude": w["longitude"],
                "status": "idle",
                "fuel_cost_per_km": 8.5,
                "route_history": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            await trucks_collection.insert_one(truck)
            print(f"  Created truck: {truck['truck_number']}")

    print("Seeding complete.")


if __name__ == "__main__":
    asyncio.run(seed())