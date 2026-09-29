from pathlib import Path

import networkx as nx
import osmnx as ox


GRAPH_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "graph"
    / "miraflores_san_isidro.graphml"
)

MIN_GRAPH_NODES = 1500


def load_city_graph(
    path: str | Path | None = None,
) -> nx.MultiDiGraph:
    """
    Carga desde disco el grafo vial generado con OSMnx.

    No descarga datos durante el inicio de la API.
    """

    graph_path = Path(path) if path else GRAPH_PATH

    if not graph_path.is_file():
        raise FileNotFoundError(
            f"No se encontró el dataset: {graph_path}"
        )

    if graph_path.stat().st_size == 0:
        raise ValueError(
            f"El dataset está vacío: {graph_path}"
        )

    try:
        graph = ox.load_graphml(graph_path)
    except Exception as error:
        raise ValueError(
            f"No se pudo cargar el archivo GraphML: {graph_path}"
        ) from error

    if not isinstance(graph, nx.MultiDiGraph):
        graph = nx.MultiDiGraph(graph)

    if not graph.is_directed():
        raise ValueError(
            "El dataset debe representar un grafo dirigido."
        )

    node_count = graph.number_of_nodes()
    edge_count = graph.number_of_edges()

    if node_count <= MIN_GRAPH_NODES:
        raise ValueError(
            "El dataset debe contener más de "
            f"{MIN_GRAPH_NODES} nodos; contiene {node_count}."
        )

    if edge_count == 0:
        raise ValueError(
            "El dataset no contiene aristas."
        )

    return graph