from inventory_optimization import optimize_inventory_policy

result = optimize_inventory_policy(
    annual_demand=3650,        
    avg_daily_demand=10,
    demand_std_dev=3.5,        
    lead_time_days=7,          
    ordering_cost_per_order=50,    
    holding_cost_per_unit_per_year=6,  
)

print("Optimal Inventory Policy for PROD-001:")
for key, value in result.items():
    print(f"  {key}: {value}")