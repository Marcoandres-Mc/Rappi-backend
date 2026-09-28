import networkx as nx


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


def find_nearest_node(graph, latitude, longitude):
    """
    Busca el nodo del grafo más cercano
    a unas coordenadas.
    """

    import osmnx as ox

    node = ox.distance.nearest_nodes(
        graph,
        X=longitude,
        Y=latitude
    )

    return node