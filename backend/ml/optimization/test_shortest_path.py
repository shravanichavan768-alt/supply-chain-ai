from shortest_path import Graph, dijkstra, a_star

g = Graph()
g.add_node("Mumbai_WH", 19.0760, 72.8777)
g.add_node("Pune_WH", 18.5204, 73.8567)
g.add_node("Delhi_WH", 28.7041, 77.1025)
g.add_node("Bangalore_WH", 12.9716, 77.5946)
g.add_node("Nashik", 19.9975, 73.7898)
g.add_node("Nagpur", 21.1458, 79.0882)

g.add_edge("Mumbai_WH", "Pune_WH")
g.add_edge("Mumbai_WH", "Nashik")
g.add_edge("Nashik", "Pune_WH")
g.add_edge("Nashik", "Nagpur")
g.add_edge("Pune_WH", "Nagpur")
g.add_edge("Nagpur", "Delhi_WH")
g.add_edge("Pune_WH", "Bangalore_WH")

print("=== Dijkstra: Mumbai_WH -> Delhi_WH ===")
path, distance, explored = dijkstra(g, "Mumbai_WH", "Delhi_WH")
print(f"Path: {' -> '.join(path)}")
print(f"Distance: {distance:.2f} km")
print(f"Nodes explored: {explored}")

print("\n=== A*: Mumbai_WH -> Delhi_WH ===")
path, distance, explored = a_star(g, "Mumbai_WH", "Delhi_WH")
print(f"Path: {' -> '.join(path)}")
print(f"Distance: {distance:.2f} km")
print(f"Nodes explored: {explored}")