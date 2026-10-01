import networkx as nx

def get_traffic_factor(hour: int) -> float:
    if not 0 <= hour <= 23:
        raise ValueError(
            "La hora debe estar entre 0 y 23."
        )

    if 7 <= hour < 10 or 17 <= hour < 20:
        return 2.5

    if 10 <= hour < 17 or 20 <= hour < 22:
        return 1.5

    return 1.0


def prepare_graph(
    graph: nx.MultiDiGraph,
    hour: int,
) -> nx.MultiDiGraph:
    """
    Crea una copia del grafo y añade los pesos dinámicos.
    """

    prepared_graph = graph.copy()
    factor = get_traffic_factor(hour)

    for origin, destination, key, data in prepared_graph.edges(
        keys=True,
        data=True,
    ):
        try:
            distance_m = float(data["length"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(
                "La arista "
                f"({origin}, {destination}, {key}) "
                "no contiene una longitud válida."
            ) from error

        if distance_m < 0:
            raise ValueError(
                "Las distancias no pueden ser negativas."
            )
            
        edge_factor = get_edge_factor(factor, data)
        data["distance_m"] = distance_m
        data["traffic_factor"] = edge_factor
        data["weight"] = distance_m * edge_factor

    return prepared_graph


def build_adjacency_list(
    graph: nx.MultiDiGraph,
) -> dict[int, list[tuple[int, float]]]:
    """
    Convierte el MultiDiGraph en una lista de adyacencia.

    Cuando existen varias aristas entre los mismos nodos,
    conserva la de menor peso.
    """

    adjacency = {
        node: []
        for node in graph.nodes
    }

    for origin in graph.nodes:
        for destination, parallel_edges in graph.adj[origin].items():
            minimum_weight = min(
                float(data["weight"])
                for data in parallel_edges.values()
            )

            adjacency[origin].append(
                (destination, minimum_weight)
            )

    return adjacency




def _highway_type(data: dict) -> str:
    h = data.get("highway", "residential")
    return h[0] if isinstance(h, list) else h


# Qué tan sensible es cada tipo de vía a la congestión (1.0 = nada)
ROAD_SENSITIVITY = {
    "trunk": 1.0, "primary": 1.0,
    "secondary": 0.7, "tertiary": 0.5,
}
DEFAULT_SENSITIVITY = 0.2  # residential, service, etc.


def get_edge_factor(base_factor: float, data: dict) -> float:
    sensitivity = ROAD_SENSITIVITY.get(
        _highway_type(data), DEFAULT_SENSITIVITY
    )
    return 1.0 + (base_factor - 1.0) * sensitivity