from time import perf_counter

from app.algoritmos.backtracking import backtracking
from app.algoritmos.divide_venceras import divide_venceras
from app.algoritmos.fuerza_bruta import fuerza_bruta

from app.graph.graph_builder import (
    build_adjacency_list,
    prepare_graph,
)

from app.graph.graph_utils import (
    find_nearest_node,
    get_path_coordinates,
    get_path_distance_m,
)

from app.schemas.route import (
    DeliveryRouteRequest,
    DeliveryRouteResponse,
)

from app.services.cost_matrix_service import (
    build_cost_matrix,
)

from app.services.route_service import get_base_graph


ALGORITHM_LIMITS = {
    "brute_force": 8,
    "backtracking": 12,
    "divide_conquer": 30,
}


def calculate_delivery_route(
    request: DeliveryRouteRequest,
) -> DeliveryRouteResponse:
    validate_delivery_count(
        request.algorithm,
        len(request.destinations),
    )

    graph = prepare_graph(
        get_base_graph(),
        request.traffic_hour,
    )

    adjacency = build_adjacency_list(graph)

    requested_coordinates = [
        request.origin,
        *request.destinations,
    ]

    nodes = [
        find_nearest_node(
            graph,
            coordinate.lat,
            coordinate.lon,
        )
        for coordinate in requested_coordinates
    ]

    if len(nodes) != len(set(nodes)):
        raise ValueError(
            "Dos o más ubicaciones corresponden "
            "al mismo nodo vial."
        )

    matrix_start = perf_counter()

    matrix = build_cost_matrix(
        adjacency,
        nodes,
    )

    matrix_time_ms = (
        perf_counter() - matrix_start
    ) * 1000

    algorithm_start = perf_counter()

    optimization = run_algorithm(
        request,
        matrix.costs,
    )

    execution_time_ms = (
        perf_counter() - algorithm_start
    ) * 1000

    node_path = reconstruct_node_path(
        matrix.paths,
        matrix.nodes,
        optimization["order"],
    )

    return DeliveryRouteResponse(
        algorithm=request.algorithm,
        execution_time_ms=execution_time_ms,
        matrix_time_ms=matrix_time_ms,
        nodos_visitados=matrix.nodes_visited,
        states_explored=(
            optimization["states_explored"]
        ),
        branches_pruned=(
            optimization["branches_pruned"]
        ),
        distancia_total_m=get_path_distance_m(
            graph,
            node_path,
        ),
        weighted_cost=optimization["total_cost"],
        delivery_order=optimization["order"],
        is_optimal=optimization["is_optimal"],
        path=get_path_coordinates(
            graph,
            node_path,
        ),
    )


def run_algorithm(
    request: DeliveryRouteRequest,
    costs: list[list[float]],
) -> dict:
    if request.algorithm == "brute_force":
        result = fuerza_bruta(
            costs,
            request.return_to_origin,
        )

        return {
            "order": result.order,
            "total_cost": result.total_cost,
            "states_explored":
                result.states_explored,
            "branches_pruned": 0,
            "is_optimal": True,
        }

    if request.algorithm == "backtracking":
        result = backtracking(
            costs,
            request.return_to_origin,
        )

        return {
            "order": result.order,
            "total_cost": result.total_cost,
            "states_explored":
                result.states_explored,
            "branches_pruned":
                result.branches_pruned,
            "is_optimal": True,
        }

    coordinates = [
        (
            request.origin.lat,
            request.origin.lon,
        ),
        *[
            (
                destination.lat,
                destination.lon,
            )
            for destination
            in request.destinations
        ],
    ]

    result = divide_venceras(
        costs,
        coordinates,
        request.return_to_origin,
    )

    return {
        "order": result.order,
        "total_cost": result.total_cost,
        "states_explored":
            result.states_explored,
        "branches_pruned": 0,
        "is_optimal": False,
    }


def reconstruct_node_path(
    paths: list[list[list[int]]],
    nodes: list[int],
    order: list[int],
) -> list[int]:
    if len(order) == 1:
        return [nodes[order[0]]]

    complete_path = []

    for origin, destination in zip(
        order,
        order[1:],
    ):
        segment = paths[origin][destination]

        if not segment:
            raise ValueError(
                "No existe camino reconstruido "
                f"entre {origin} y {destination}."
            )

        if not complete_path:
            complete_path.extend(segment)
        else:
            complete_path.extend(segment[1:])

    return complete_path


def validate_delivery_count(
    algorithm: str,
    count: int,
) -> None:
    limit = ALGORITHM_LIMITS[algorithm]

    if count > limit:
        raise ValueError(
            f"'{algorithm}' admite como máximo "
            f"{limit} entregas; se recibieron "
            f"{count}."
        )