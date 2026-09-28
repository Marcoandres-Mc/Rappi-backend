def backtracking(graph, origin, destinations):
    best_route = None
    best_cost = float("inf")

    def search(current, remaining, route, current_cost):

        nonlocal best_route, best_cost

        if not remaining:

            if current_cost < best_cost:
                best_cost = current_cost
                best_route = route.copy()

            return

        for destination in remaining:

            if not graph.has_edge(current, destination):
                continue

            edge_cost = graph[current][destination].get("weight", 1)

            new_cost = current_cost + edge_cost

            # Poda
            if new_cost >= best_cost:
                continue

            new_remaining = [
                node
                for node in remaining
                if node != destination
            ]

            search(
                destination,
                new_remaining,
                route + [destination],
                new_cost
            )

    search(
        origin,
        destinations,
        [origin],
        0
    )

    return {
        "path": best_route,
        "cost": best_cost
    }