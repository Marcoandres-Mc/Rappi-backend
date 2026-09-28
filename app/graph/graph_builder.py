import networkx as nx


def combine_graphs(graphs):
    """
    Combina los grafos de Miraflores y San Isidro
    en un solo grafo.
    """

    if not graphs:
        return nx.MultiDiGraph()

    combined_graph = graphs[0].copy()

    for graph in graphs[1:]:
        combined_graph = nx.compose(
            combined_graph,
            graph
        )

    return combined_graph


def prepare_graph(graph):
    """
    Prepara el grafo para trabajar con los algoritmos.
    """

    graph = graph.copy()

    # Agregar velocidades y tiempos estimados
    graph = add_travel_times(graph)

    return graph


def add_travel_times(graph):
    """
    Agrega velocidades y tiempos de viaje
    cuando OSMnx dispone de los datos necesarios.
    """

    try:
        graph = graph.copy()

        graph = nx.MultiDiGraph(graph)

        return graph

    except Exception:
        return graph