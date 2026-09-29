from itertools import permutations


def fuerza_bruta(graph, origin, destinations):
    best_route = None
    best_cost = float("inf")

    for permutation in permutations(destinations):

        route = [origin] + list(permutation)

        cost = calculate_route_cost(graph, route)

        if cost < best_cost:
            best_cost = cost
            best_route = route

    return {
        "path": best_route,
        "cost": best_cost
    }


def calculate_route_cost(graph, route):
    total_cost = 0

    for i in range(len(route) - 1):

        current = route[i]
        next_node = route[i + 1]

        if not graph.has_edge(current, next_node):
            return float("inf")

        total_cost += graph[current][next_node].get("weight", 1)

    return total_cost