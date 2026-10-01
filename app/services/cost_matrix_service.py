from dataclasses import dataclass

from app.algoritmos.dijkstra import (
    PathNotFoundError,
    dijkstra_to_targets,
)

AdjacencyList = dict[
    int,
    list[tuple[int, float]],
]


@dataclass(frozen=True)
class CostMatrixResult:
    nodes: list[int]
    costs: list[list[float]]
    paths: list[list[list[int]]]
    nodes_visited: int


def build_cost_matrix(
    adjacency: AdjacencyList,
    nodes: list[int],
) -> CostMatrixResult:
    """
    Calcula los costos y caminos mínimos dirigidos entre
    todos los puntos importantes, con un Dijkstra por origen.
    """

    if not nodes:
        raise ValueError("Se requiere al menos un nodo.")

    if len(nodes) != len(set(nodes)):
        raise ValueError(
            "Los nodos de la matriz no pueden estar repetidos."
        )

    size = len(nodes)

    costs = [[0.0] * size for _ in range(size)]
    paths = [[[] for _ in range(size)] for _ in range(size)]

    total_nodes_visited = 0

    for i, origin in enumerate(nodes):
        if origin not in adjacency:
            raise ValueError(f"El nodo no existe: {origin}")

        paths[i][i] = [origin]

        targets = {n for n in nodes if n != origin}

        results, visited = dijkstra_to_targets(
            adjacency,
            origin,
            targets,
        )

        total_nodes_visited += visited

        for j, destination in enumerate(nodes):
            if i == j:
                continue

            if destination not in results:
                raise PathNotFoundError(
                    "No se puede construir la matriz: "
                    "no existe camino dirigido entre "
                    f"{origin} y {destination}."
                )

            costs[i][j] = results[destination].total_cost
            paths[i][j] = results[destination].path

    return CostMatrixResult(
        nodes=nodes.copy(),
        costs=costs,
        paths=paths,
        nodes_visited=total_nodes_visited,
    )