
import math


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def allocate_warehouse(destination_lat, destination_lng, product_id, quantity_needed, warehouses):
    
    candidates = []

    for warehouse in warehouses:
        stock_item = next(
            (item for item in warehouse["inventory"] if item["product_id"] == product_id), None
        )
        available_stock = stock_item["quantity"] if stock_item else 0

        if available_stock < quantity_needed:
            continue  

        distance = haversine_distance(
            warehouse["latitude"], warehouse["longitude"], destination_lat, destination_lng
        )

        
        stock_health = (available_stock - quantity_needed) / max(available_stock, 1)

        
        normalized_distance = distance / 100  
        score = (normalized_distance * 0.8) + ((1 - stock_health) * 0.2)

        candidates.append({
            "warehouse": warehouse,
            "distance_km": round(distance, 2),
            "available_stock": available_stock,
            "stock_health": round(stock_health, 3),
            "score": round(score, 4),
        })

    if not candidates:
        return None

    candidates.sort(key=lambda c: c["score"])
    return candidates[0], candidates  