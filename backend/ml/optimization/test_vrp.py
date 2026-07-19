from vehicle_routing import solve_vrp


depot = (18.5204, 73.8567)

deliveries = [
    (18.5679, 73.9143),  
    (18.4575, 73.8508),
    (18.6298, 73.7997),
    (18.5089, 73.9260),
    (18.5904, 73.7389),
    (18.4655, 73.9068),
]

demands = [15, 20, 10, 25, 12, 18]  
truck_capacities = [50, 50]  

result = solve_vrp(depot, deliveries, demands, truck_capacities)

if result:
    print(f"Total distance across all trucks: {result['total_distance_km']:.2f} km\n")
    for route_info in result["routes"]:
        print(f"Truck {route_info['vehicle_id']}: route = {route_info['route']}, distance = {route_info['distance_km']:.2f} km")
else:
    print("No solution found.")