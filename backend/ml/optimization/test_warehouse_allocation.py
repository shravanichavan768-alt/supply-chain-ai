from warehouse_allocation import allocate_warehouse

warehouses = [
    {
        "id": "wh1", "name": "Mumbai Central Warehouse",
        "latitude": 19.0760, "longitude": 72.8777,
        "inventory": [{"product_id": "PROD-001", "quantity": 400}],
    },
    {
        "id": "wh2", "name": "Pune Warehouse",
        "latitude": 18.5204, "longitude": 73.8567,
        "inventory": [{"product_id": "PROD-001", "quantity": 50}],
    },
    {
        "id": "wh3", "name": "Delhi NCR Warehouse",
        "latitude": 28.7041, "longitude": 77.1025,
        "inventory": [{"product_id": "PROD-001", "quantity": 600}],
    },
]

destination_lat, destination_lng = 18.5679, 73.9143

best, all_candidates = allocate_warehouse(destination_lat, destination_lng, "PROD-001", 30, warehouses)

print(f"Best warehouse: {best['warehouse']['name']}")
print(f"  Distance: {best['distance_km']} km")
print(f"  Available stock: {best['available_stock']}")
print(f"  Stock health after order: {best['stock_health']}")
print(f"  Score: {best['score']}\n")

print("All candidates ranked:")
for c in all_candidates:
    print(f"  {c['warehouse']['name']}: distance={c['distance_km']}km, stock={c['available_stock']}, score={c['score']}")