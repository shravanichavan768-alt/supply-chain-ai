
import heapq
import math


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class Graph:
    """A simple weighted graph where nodes are (id, lat, lng) locations."""

    def __init__(self):
        self.nodes = {}  # node_id -> (lat, lng)
        self.edges = {}  # node_id -> list of (neighbor_id, weight)

    def add_node(self, node_id, lat, lng):
        self.nodes[node_id] = (lat, lng)
        if node_id not in self.edges:
            self.edges[node_id] = []

    def add_edge(self, node_a, node_b, weight=None):
        if weight is None:
            lat1, lng1 = self.nodes[node_a]
            lat2, lng2 = self.nodes[node_b]
            weight = haversine_distance(lat1, lng1, lat2, lng2)
        self.edges[node_a].append((node_b, weight))
        self.edges[node_b].append((node_a, weight))  # undirected graph


def dijkstra(graph: Graph, start: str, end: str):
    
    distances = {node: float("inf") for node in graph.nodes}
    distances[start] = 0
    previous = {node: None for node in graph.nodes}
    visited = set()

    priority_queue = [(0, start)]
    nodes_explored = 0

    while priority_queue:
        current_dist, current_node = heapq.heappop(priority_queue)

        if current_node in visited:
            continue
        visited.add(current_node)
        nodes_explored += 1

        if current_node == end:
            break

        for neighbor, weight in graph.edges[current_node]:
            distance = current_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

    path = _reconstruct_path(previous, start, end)
    return path, distances[end], nodes_explored


def a_star(graph: Graph, start: str, end: str):
    
    end_lat, end_lng = graph.nodes[end]

    def heuristic(node):
        lat, lng = graph.nodes[node]
        return haversine_distance(lat, lng, end_lat, end_lng)

    distances = {node: float("inf") for node in graph.nodes}
    distances[start] = 0
    previous = {node: None for node in graph.nodes}
    visited = set()

    priority_queue = [(heuristic(start), start)]
    nodes_explored = 0

    while priority_queue:
        _, current_node = heapq.heappop(priority_queue)

        if current_node in visited:
            continue
        visited.add(current_node)
        nodes_explored += 1

        if current_node == end:
            break

        for neighbor, weight in graph.edges[current_node]:
            distance = distances[current_node] + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                priority = distance + heuristic(neighbor)
                heapq.heappush(priority_queue, (priority, neighbor))

    path = _reconstruct_path(previous, start, end)
    return path, distances[end], nodes_explored


def _reconstruct_path(previous, start, end):
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()
    return path if path[0] == start else []