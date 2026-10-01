from functools import lru_cache
from time import perf_counter

import networkx as nx

from app.algoritmos.dijkstra import dijkstra
from app.graph.graph_builder import (
    build_adjacency_list,
    prepare_graph,
)
from app.graph.graph_loader import load_city_graph
from app.graph.graph_utils import (
    find_nearest_node,
    get_path_coordinates,
    get_path_distance_m,
)
from app.schemas.route import (
    RouteRequest,
    RouteResponse,
)


@lru_cache(maxsize=1)
def get_base_graph() -> nx.MultiDiGraph:
    """
    Carga el dataset una sola vez.
    """

    return load_city_graph()


@lru_cache(maxsize=24)
def get_prepared_graph(hour: int):
    """
    Devuelve (graph, adjacency) para una hora dada.
    Se calcula una sola vez por hora y se reutiliza.
    """
    graph = prepare_graph(get_base_graph(), hour)
    adjacency = build_adjacency_list(graph)
    return graph, adjacency




def calculate_route(
    request: RouteRequest,
) -> RouteResponse:
    if request.algorithm != "dijkstra":
        raise ValueError(
            f"El algoritmo '{request.algorithm}' "
            "todavía no está disponible."
        )

    graph, adjacency = get_prepared_graph(
    request.traffic_hour
    )

    origin_node = find_nearest_node(
        graph,
        request.origin.lat,
        request.origin.lon,
    )

    destination_node = find_nearest_node(
        graph,
        request.destination.lat,
        request.destination.lon,
    )

    start = perf_counter()

    result = dijkstra(
        adjacency,
        origin_node,
        destination_node,
    )

    execution_time_ms = (
        perf_counter() - start
    ) * 1000

    return RouteResponse(
        algorithm="dijkstra",
        execution_time_ms=execution_time_ms,
        nodos_visitados=result.nodes_visited,
        distancia_total_m=get_path_distance_m(
            graph,
            result.path,
        ),
        weighted_cost=result.total_cost,
        path=get_path_coordinates(
            graph,
            result.path,
        ),
    )