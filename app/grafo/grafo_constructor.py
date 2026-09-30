import json
from pathlib import Path

import networkx as nx
import osmnx as ox


# ==========================================
# RUTAS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "graph"

JSON_FILE = DATA_DIR / "miraflores_san_isidro.json"


# ==========================================
# CONFIGURACIÓN
# ==========================================

DISTRITOS = [
    "Miraflores, Lima, Peru",
    "San Isidro, Lima, Peru"
]


# ==========================================
# OBTENER GRAFO DESDE OPENSTREETMAP
# ==========================================

def obtener_grafo_distrito(nombre_lugar: str):

    print()
    print("=" * 50)
    print(f"DESCARGANDO: {nombre_lugar}")
    print("=" * 50)

    grafo = ox.graph_from_place(
        nombre_lugar,
        network_type="drive",
        simplify=True,
        retain_all=True
    )

    print(f"Nodos obtenidos: {grafo.number_of_nodes()}")
    print(f"Edges obtenidos: {grafo.number_of_edges()}")

    return grafo


# ==========================================
# CONVERTIR GRAFO A JSON
# ==========================================

def convertir_grafo_a_json(grafo, distrito):

    nodes = []
    edges = []

    # --------------------------------------
    # NODOS
    # --------------------------------------

    for node_id, datos in grafo.nodes(data=True):

        nodes.append({
            "id": str(node_id),
            "lat": datos.get("y"),
            "lon": datos.get("x"),
            "distrito": distrito
        })

    # --------------------------------------
    # EDGES
    # --------------------------------------

    for source, target, key, datos in grafo.edges(
        keys=True,
        data=True
    ):

        # Nombre de la calle
        calle = datos.get("name")

        if isinstance(calle, list):
            calle = ", ".join(str(nombre) for nombre in calle)

        if calle is None:
            calle = "Sin nombre"

        # Tipo de vía
        highway = datos.get("highway")

        if isinstance(highway, list):
            highway = ", ".join(str(tipo) for tipo in highway)

        # Longitud
        distancia = datos.get("length", 0)

        # Velocidad máxima
        maxspeed = datos.get("maxspeed")

        if isinstance(maxspeed, list):
            maxspeed = ", ".join(str(valor) for valor in maxspeed)

        # ----------------------------------
        # EDGE
        # ----------------------------------

        edges.append({
            "source": str(source),
            "target": str(target),

            "calle": calle,

            "distancia_m": distancia,

            "maxspeed": maxspeed,

            "highway": highway,

            "oneway": datos.get("oneway", False),

            "geometry": (
                list(datos["geometry"].coords)
                if datos.get("geometry") is not None
                else None
            )
        })

    return {
        "nodes": nodes,
        "edges": edges
    }


# ==========================================
# GENERAR DATASET COMPLETO
# ==========================================

def generar_dataset():

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print()
    print("=" * 60)
    print("GENERANDO DATASET DE CALLES")
    print("MIRAFLORES + SAN ISIDRO")
    print("=" * 60)

    todos_los_nodos = []
    todas_las_edges = []

    # --------------------------------------
    # DESCARGAR CADA DISTRITO
    # --------------------------------------

    for lugar in DISTRITOS:

        if "Miraflores" in lugar:
            distrito = "Miraflores"
        else:
            distrito = "San Isidro"

        grafo = obtener_grafo_distrito(lugar)

        datos = convertir_grafo_a_json(
            grafo,
            distrito
        )

        todos_los_nodos.extend(
            datos["nodes"]
        )

        todas_las_edges.extend(
            datos["edges"]
        )

    # --------------------------------------
    # DATASET FINAL
    # --------------------------------------

    dataset = {

        "fuente": "OpenStreetMap",

        "procesamiento": "OSMnx",

        "network_type": "drive",

        "distritos": [
            "Miraflores",
            "San Isidro"
        ],

        "nodes": todos_los_nodos,

        "edges": todas_las_edges
    }

    # --------------------------------------
    # GUARDAR JSON
    # --------------------------------------

    with open(
        JSON_FILE,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            dataset,
            archivo,
            ensure_ascii=False,
            indent=2
        )

    # --------------------------------------
    # ESTADÍSTICAS
    # --------------------------------------

    print()
    print("=" * 60)
    print("DATASET GENERADO")
    print("=" * 60)

    print(
        f"Nodos totales: {len(todos_los_nodos)}"
    )

    print(
        f"Edges totales: {len(todas_las_edges)}"
    )

    print()
    print(f"Archivo generado:")
    print(JSON_FILE)

    print("=" * 60)


# ==========================================
# CARGAR JSON COMO NETWORKX
# ==========================================

def cargar_grafo():

    if not JSON_FILE.exists():

        raise FileNotFoundError(
            f"No existe el archivo: {JSON_FILE}"
        )

    with open(
        JSON_FILE,
        "r",
        encoding="utf-8"
    ) as archivo:

        datos = json.load(archivo)

    grafo = nx.MultiDiGraph()

    # --------------------------------------
    # NODOS
    # --------------------------------------

    for node in datos["nodes"]:

        grafo.add_node(
            node["id"],

            lat=node["lat"],

            lon=node["lon"],

            distrito=node["distrito"]
        )

    # --------------------------------------
    # EDGES
    # --------------------------------------

    for edge in datos["edges"]:

        grafo.add_edge(

            edge["source"],

            edge["target"],

            calle=edge.get(
                "calle",
                "Sin nombre"
            ),

            distancia_m=edge.get(
                "distancia_m",
                0
            ),

            maxspeed=edge.get(
                "maxspeed"
            ),

            highway=edge.get(
                "highway"
            ),

            oneway=edge.get(
                "oneway",
                False
            ),

            geometry=edge.get(
                "geometry"
            )
        )

    return grafo


# ==========================================
# EJECUCIÓN
# ==========================================

if __name__ == "__main__":

    # Primero generamos el dataset real
    generar_dataset()

    # Después lo cargamos en NetworkX
    G = cargar_grafo()

    print()
    print("=" * 40)
    print("GRAFO CARGADO")
    print("=" * 40)

    print(
        f"Nodos: {G.number_of_nodes()}"
    )

    print(
        f"Edges: {G.number_of_edges()}"
    )

    print("=" * 40)