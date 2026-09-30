import json
from pathlib import Path

import networkx as nx


BASE_DIR = Path(__file__).resolve().parent.parent

GRAPH_FILE = (
    BASE_DIR
    / "data"
    / "graph"
    / "miraflores_san_isidro.json"
)


def load_city_graph():

    if not GRAPH_FILE.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {GRAPH_FILE}"
        )

    with open(
        GRAPH_FILE,
        "r",
        encoding="utf-8"
    ) as archivo:

        data = json.load(archivo)

    graph = nx.MultiDiGraph()

    # -------------------------
    # NODOS
    # -------------------------

    for node in data["nodes"]:

        graph.add_node(
            node["id"],
            lat=node["lat"],
            lon=node["lon"],
            distrito=node["distrito"]
        )

    # -------------------------
    # EDGES
    # -------------------------

    for edge in data["edges"]:

        graph.add_edge(
            edge["source"],
            edge["target"],
            calle=edge.get("calle", "Sin nombre"),
            distancia_m=edge.get("distancia_m", 0),
            maxspeed=edge.get("maxspeed"),
            highway=edge.get("highway"),
            oneway=edge.get("oneway", False),
            geometry=edge.get("geometry")
        )

    return graph


if __name__ == "__main__":

    G = load_city_graph()

    print("==============================")
    print("GRAFO CARGADO")
    print("==============================")
    print(f"Nodos: {G.number_of_nodes()}")
    print(f"Edges: {G.number_of_edges()}")