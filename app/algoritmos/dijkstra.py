from dataclasses import dataclass
from heapq import heappop, heappush
from math import inf


AdjacencyList = dict[int, list[tuple[int, float]]]


@dataclass(frozen=True)
class ShortestPathResult:
    path: list[int]
    total_cost: float
    nodes_visited: int


class PathNotFoundError(ValueError):
    """No existe un camino dirigido entre los nodos."""


def dijkstra(
    adjacency: AdjacencyList,
    origin: int,
    destination: int,
) -> ShortestPathResult:
    if origin not in adjacency:
        raise ValueError(
            f"El nodo de origen no existe: {origin}"
        )

    if destination not in adjacency:
        raise ValueError(
            f"El nodo de destino no existe: {destination}"
        )

    distances = {
        node: inf
        for node in adjacency
    }

    previous: dict[int, int] = {}
    visited: set[int] = set()
    priority_queue: list[tuple[float, int]] = []

    distances[origin] = 0.0
    heappush(priority_queue, (0.0, origin))

    while priority_queue:
        current_cost, current = heappop(
            priority_queue
        )

        if current in visited:
            continue

        if current_cost > distances[current]:
            continue

        visited.add(current)

        if current == destination:
            return ShortestPathResult(
                path=reconstruct_path(
                    previous,
                    origin,
                    destination,
                ),
                total_cost=current_cost,
                nodes_visited=len(visited),
            )

        for neighbor, edge_cost in adjacency[current]:
            if edge_cost < 0:
                raise ValueError(
                    "Dijkstra no admite pesos negativos: "
                    f"({current}, {neighbor}) tiene "
                    f"costo {edge_cost}."
                )

            if neighbor not in adjacency:
                raise ValueError(
                    "La lista de adyacencia referencia "
                    f"un nodo inexistente: {neighbor}"
                )

            candidate_cost = (
                current_cost + edge_cost
            )

            if candidate_cost < distances[neighbor]:
                distances[neighbor] = candidate_cost
                previous[neighbor] = current

                heappush(
                    priority_queue,
                    (candidate_cost, neighbor),
                )

    raise PathNotFoundError(
        "No existe un camino dirigido entre "
        f"{origin} y {destination}."
    )


def reconstruct_path(
    previous: dict[int, int],
    origin: int,
    destination: int,
) -> list[int]:
    path = [destination]
    current = destination

    while current != origin:
        current = previous[current]
        path.append(current)

    path.reverse()
    return path