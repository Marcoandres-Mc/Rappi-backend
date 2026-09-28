import osmnx as ox


def load_city_graph():
    """
    Obtiene la red vial de Miraflores y San Isidro
    desde OpenStreetMap.
    """

    places = [
        "Miraflores, Lima, Peru",
        "San Isidro, Lima, Peru"
    ]

    graphs = []

    for place in places:
        graph = ox.graph_from_place(
            place,
            network_type="drive"
        )

        graphs.append(graph)

    return graphs