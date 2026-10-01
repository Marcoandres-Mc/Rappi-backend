import networkx as nx
from typing import Any
from math import cos, radians, sin


def get_graph_info(graph):
    """
    Devuelve información básica del grafo.
    """

    return {
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges()
    }


def get_node_coordinates(graph, node):
    """
    Obtiene las coordenadas de un nodo.
    """

    data = graph.nodes[node]

    return {
        "lat": data.get("y"),
        "lon": data.get("x")
    }



def find_nearest_node(
    graph: nx.MultiDiGraph,
    latitude: float,
    longitude: float,
) -> int:
    """
    Encuentra el nodo geográficamente más cercano
    mediante la fórmula de Haversine.

    Complejidad temporal: O(V).
    Complejidad espacial: O(1).
    """

    if not -90 <= latitude <= 90:
        raise ValueError(
            "La latitud debe estar entre -90 y 90."
        )

    if not -180 <= longitude <= 180:
        raise ValueError(
            "La longitud debe estar entre -180 y 180."
        )

    target_latitude = radians(latitude)
    target_longitude = radians(longitude)

    nearest_node = None
    minimum_distance = float("inf")

    for node, data in graph.nodes(data=True):
        try:
            node_latitude = radians(
                float(data["y"])
            )
            node_longitude = radians(
                float(data["x"])
            )
        except (KeyError, TypeError, ValueError):
            continue

        latitude_difference = (
            node_latitude - target_latitude
        )

        longitude_difference = (
            node_longitude - target_longitude
        )

        haversine_value = (
            sin(latitude_difference / 2) ** 2
            + cos(target_latitude)
            * cos(node_latitude)
            * sin(longitude_difference / 2) ** 2
        )

        if haversine_value < minimum_distance:
            minimum_distance = haversine_value
            nearest_node = node

    if nearest_node is None:
        raise ValueError(
            "El grafo no contiene nodos con "
            "coordenadas válidas."
        )

    return int(nearest_node)







def get_path_coordinates(
    graph: nx.MultiDiGraph,
    path: list[int],
) -> list[dict[str, float]]:
    """
    Expande el camino utilizando la geometría
    real de cada calle.
    """

    if not path:
        return []

    coordinates = [
        get_node_coordinates(graph, path[0])
    ]

    for origin, destination in zip(
        path,
        path[1:],
    ):
        edge_data = get_best_parallel_edge(
            graph,
            origin,
            destination,
        )

        geometry = edge_data.get("geometry")

        if (
            geometry is None
            or not hasattr(geometry, "coords")
        ):
            segment = [
                get_node_coordinates(
                    graph,
                    destination,
                )
            ]

        else:
            geometry_coordinates = list(
                geometry.coords
            )

            origin_coordinates = (
                get_node_coordinates(graph, origin)
            )

            first_lon, first_lat = (
                geometry_coordinates[0]
            )

            last_lon, last_lat = (
                geometry_coordinates[-1]
            )

            distance_to_first = (
                (
                    first_lat
                    - origin_coordinates["lat"]
                ) ** 2
                + (
                    first_lon
                    - origin_coordinates["lon"]
                ) ** 2
            )

            distance_to_last = (
                (
                    last_lat
                    - origin_coordinates["lat"]
                ) ** 2
                + (
                    last_lon
                    - origin_coordinates["lon"]
                ) ** 2
            )

            if distance_to_last < distance_to_first:
                geometry_coordinates.reverse()

            segment = [
                {
                    "lat": float(lat),
                    "lon": float(lon),
                }
                for lon, lat
                in geometry_coordinates[1:]
            ]

        for point in segment:
            if point != coordinates[-1]:
                coordinates.append(point)

    return coordinates



def get_best_parallel_edge(
    graph: nx.MultiDiGraph,
    origin: int,
    destination: int,
    weight: str = "weight",
) -> dict[str, Any]:
    """
    Selecciona la arista paralela de menor peso.
    """

    edge_group = graph.get_edge_data(
        origin,
        destination,
    )

    if not edge_group:
        raise ValueError(
            "No existe la arista dirigida "
            f"({origin}, {destination})."
        )

    try:
        return min(
            edge_group.values(),
            key=lambda data: float(data[weight]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(
            f"La arista ({origin}, {destination}) "
            "no tiene un peso válido."
        ) from error


def get_path_distance_m(
    graph: nx.MultiDiGraph,
    path: list[int],
    weight: str = "weight",
) -> float:
    """
    Calcula la distancia física del camino en metros.
    """

    total_distance = 0.0

    for origin, destination in zip(
        path,
        path[1:],
    ):
        edge_data = get_best_parallel_edge(
            graph,
            origin,
            destination,
            weight,
        )

        try:
            distance = (
                edge_data["distance_m"]
                if "distance_m" in edge_data
                else edge_data["length"]
            )

            total_distance += float(distance)

        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(
                f"La arista ({origin}, {destination}) "
                "no tiene una distancia válida."
            ) from error

    return total_distance