
import asyncio
import sys
import os
import pandas as pd
from datetime import datetime

# Allow importing from the backend app package
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from app.db.mongodb import database

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


async def export_daily_demand():
    
    days_collection = database.get_collection("simulation_days")
    cursor = days_collection.find().sort("day_number", 1)
    days = await cursor.to_list(length=None)

    rows = []
    for day in days:
        rows.append({
            "day_number": day["day_number"],
            "weather": day["weather"],
            "traffic_level": day["traffic_level"],
            "is_festival": int(day["is_festival"]),
            "demand_multiplier": day["demand_multiplier"],
            "orders_generated": day["orders_generated"],
            "total_revenue": day["total_revenue"],
            "num_supplier_delays": len(day["supplier_delays"]),
            "num_warehouse_failures": len(day["warehouse_failures"]),
            "day_of_week": day["day_number"] % 7,  # proxy since we don't track real calendar dates
        })

    df = pd.DataFrame(rows)
    path = os.path.join(OUTPUT_DIR, "daily_demand.csv")
    df.to_csv(path, index=False)
    print(f"Exported {len(df)} rows to {path}")
    return df


async def export_delivery_records():
    
    deliveries_collection = database.get_collection("deliveries")
    trucks_collection = database.get_collection("trucks")

    cursor = deliveries_collection.find({"status": "delivered"})
    deliveries = await cursor.to_list(length=None)

    # Build a truck capacity lookup to include "truck load" as a feature
    trucks_cursor = trucks_collection.find()
    trucks = await trucks_cursor.to_list(length=None)
    truck_capacity_map = {str(t["_id"]): t["capacity"] for t in trucks}

    rows = []
    for d in deliveries:
        if d.get("actual_delivery_time_minutes") is None:
            continue
        rows.append({
            "distance_km": d["distance_km"],
            "truck_capacity": truck_capacity_map.get(d["truck_id"], 300),
            "estimated_delivery_time_minutes": d["estimated_delivery_time_minutes"],
            "actual_delivery_time_minutes": d["actual_delivery_time_minutes"],
        })

    df = pd.DataFrame(rows)
    path = os.path.join(OUTPUT_DIR, "delivery_records.csv")
    df.to_csv(path, index=False)
    print(f"Exported {len(df)} rows to {path}")
    return df


async def export_customer_orders():
    
    orders_collection = database.get_collection("orders")
    cursor = orders_collection.find()
    orders = await cursor.to_list(length=None)

    rows = []
    for o in orders:
        total_quantity = sum(item["quantity"] for item in o["items"])
        rows.append({
            "customer_email": o["customer_email"],
            "total_amount": o["total_amount"],
            "total_quantity": total_quantity,
            "num_items": len(o["items"]),
            "is_bulk": int(o["is_bulk"]),
            "priority": o["priority"],
            "status": o["status"],
        })

    df = pd.DataFrame(rows)
    path = os.path.join(OUTPUT_DIR, "customer_orders.csv")
    df.to_csv(path, index=False)
    print(f"Exported {len(df)} rows to {path}")
    return df


async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Exporting daily demand data...")
    await export_daily_demand()
    print("Exporting delivery records...")
    await export_delivery_records()
    print("Exporting customer orders...")
    await export_customer_orders()
    print("Export complete.")


if __name__ == "__main__":
    asyncio.run(main())