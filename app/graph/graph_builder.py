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

        data["distance_m"] = distance_m
        data["traffic_factor"] = factor
        data["weight"] = distance_m * factor

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