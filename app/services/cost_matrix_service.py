from dataclasses import dataclass

from app.algoritmos.dijkstra import (
    PathNotFoundError,
    dijkstra,
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
    Calcula los costos y caminos mínimos dirigidos
    entre todos los puntos importantes.
    """

    if not nodes:
        raise ValueError(
            "Se requiere al menos un nodo."
        )

    if len(nodes) != len(set(nodes)):
        raise ValueError(
            "Los nodos de la matriz no pueden "
            "estar repetidos."
        )

    size = len(nodes)

    costs = [
        [0.0] * size
        for _ in range(size)
    ]

    paths = [
        [
            []
            for _ in range(size)
        ]
        for _ in range(size)
    ]

    total_nodes_visited = 0

    for origin_index, origin in enumerate(nodes):
        if origin not in adjacency:
            raise ValueError(
                f"El nodo no existe: {origin}"
            )

        paths[origin_index][origin_index] = [
            origin
        ]

        for destination_index, destination in enumerate(
            nodes
        ):
            if origin_index == destination_index:
                continue

            try:
                result = dijkstra(
                    adjacency,
                    origin,
                    destination,
                )

            except PathNotFoundError as error:
                raise PathNotFoundError(
                    "No se puede construir la matriz: "
                    "no existe camino dirigido entre "
                    f"{origin} y {destination}."
                ) from error

            costs[origin_index][destination_index] = (
                result.total_cost
            )

            paths[origin_index][destination_index] = (
                result.path
            )

            total_nodes_visited += (
                result.nodes_visited
            )

    return CostMatrixResult(
        nodes=nodes.copy(),
        costs=costs,
        paths=paths,
        nodes_visited=total_nodes_visited,
    )