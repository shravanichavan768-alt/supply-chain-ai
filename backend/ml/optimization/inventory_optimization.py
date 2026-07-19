
import math


def calculate_eoq(annual_demand: float, ordering_cost_per_order: float, holding_cost_per_unit_per_year: float) -> float:
    
    if holding_cost_per_unit_per_year <= 0:
        raise ValueError("Holding cost must be positive")
    return math.sqrt((2 * annual_demand * ordering_cost_per_order) / holding_cost_per_unit_per_year)


def calculate_safety_stock(demand_std_dev: float, lead_time_days: float, service_level_z: float = 1.65) -> float:
    
    return service_level_z * demand_std_dev * math.sqrt(lead_time_days)


def calculate_reorder_point(avg_daily_demand: float, lead_time_days: float, safety_stock: float) -> float:
    
    return (avg_daily_demand * lead_time_days) + safety_stock


def optimize_inventory_policy(
    annual_demand: float,
    avg_daily_demand: float,
    demand_std_dev: float,
    lead_time_days: float,
    ordering_cost_per_order: float,
    holding_cost_per_unit_per_year: float,
    service_level_z: float = 1.65,
) -> dict:
    
    eoq = calculate_eoq(annual_demand, ordering_cost_per_order, holding_cost_per_unit_per_year)
    safety_stock = calculate_safety_stock(demand_std_dev, lead_time_days, service_level_z)
    reorder_point = calculate_reorder_point(avg_daily_demand, lead_time_days, safety_stock)

    orders_per_year = annual_demand / eoq
    annual_ordering_cost = orders_per_year * ordering_cost_per_order
    annual_holding_cost = (eoq / 2) * holding_cost_per_unit_per_year
    total_annual_cost = annual_ordering_cost + annual_holding_cost

    return {
        "economic_order_quantity": round(eoq, 1),
        "safety_stock": round(safety_stock, 1),
        "reorder_point": round(reorder_point, 1),
        "orders_per_year": round(orders_per_year, 1),
        "annual_ordering_cost": round(annual_ordering_cost, 2),
        "annual_holding_cost": round(annual_holding_cost, 2),
        "total_annual_cost": round(total_annual_cost, 2),
    }