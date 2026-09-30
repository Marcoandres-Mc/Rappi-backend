
import math


# =========================================================
# 1. OBTENER COORDENADAS DE UN NODO
# =========================================================
def obtener_coordenadas(grafo, node_id):
    """
    Devuelve la latitud y longitud de un nodo.
    """

    if node_id not in grafo:
        return None

    datos = grafo.nodes[node_id]

    return {
        "lat": datos.get("lat"),
        "lon": datos.get("lon")
    }


# =========================================================
# 2. OBTENER DISTRITO DE UN NODO
# =========================================================
def obtener_distrito(grafo, node_id):
    """
    Devuelve el distrito al que pertenece un nodo.
    """

    if node_id not in grafo:
        return None

    return grafo.nodes[node_id].get("distrito")


# =========================================================
# 3. OBTENER VECINOS DE UN NODO
# =========================================================
def obtener_vecinos(grafo, node_id):
    """
    Devuelve los nodos a los que se puede llegar
    directamente desde el nodo indicado.
    """

    if node_id not in grafo:
        return []

    return list(grafo.successors(node_id))


# =========================================================
# 4. CANTIDAD DE NODOS
# =========================================================
def cantidad_nodos(grafo):
    """
    Devuelve el número total de nodos del grafo.
    """

    return grafo.number_of_nodes()


# =========================================================
# 5. CANTIDAD DE ARISTAS
# =========================================================
def cantidad_edges(grafo):
    """
    Devuelve el número total de aristas del grafo.
    """

    return grafo.number_of_edges()


# =========================================================
# 6. CALCULAR DISTANCIA GEOGRÁFICA
# =========================================================
def calcular_distancia_geografica(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia aproximada en metros
    entre dos coordenadas geográficas usando Haversine.
    """

    radio_tierra = 6371000

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    diferencia_lat = lat2 - lat1
    diferencia_lon = lon2 - lon1

    a = (
        math.sin(diferencia_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(diferencia_lon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return radio_tierra * c


# =========================================================
# 7. BUSCAR NODO MÁS CERCANO
# =========================================================
def buscar_nodo_mas_cercano(grafo, lat, lon):
    """
    Busca el nodo del grafo más cercano
    a una ubicación geográfica.
    """

    nodo_cercano = None
    distancia_minima = float("inf")

    for node_id, datos in grafo.nodes(data=True):

        node_lat = datos.get("lat")
        node_lon = datos.get("lon")

        if node_lat is None or node_lon is None:
            continue

        distancia = calcular_distancia_geografica(
            lat,
            lon,
            node_lat,
            node_lon
        )

        if distancia < distancia_minima:
            distancia_minima = distancia
            nodo_cercano = node_id

    return nodo_cercano


# =========================================================
# 8. OBTENER DISTANCIA DE UNA ARISTA
# =========================================================
def obtener_distancia_edge(grafo, source, target):
    """
    Devuelve la menor distancia entre dos nodos conectados.
    """

    if not grafo.has_edge(source, target):
        return None

    edges = grafo.get_edge_data(source, target)

    distancias = []

    for edge in edges.values():

        distancia = edge.get("distancia_m")

        if distancia is not None:
            distancias.append(distancia)

    if not distancias:
        return None

    return min(distancias)


# =========================================================
# 9. OBTENER INFORMACIÓN DE UNA ARISTA
# =========================================================
def obtener_datos_edge(grafo, source, target):
    """
    Devuelve información de las conexiones
    entre dos nodos.
    """

    if not grafo.has_edge(source, target):
        return None

    edges = grafo.get_edge_data(source, target)

    resultado = []

    for key, edge in edges.items():

        resultado.append({
            "key": key,
            "calle": edge.get("calle", "Sin nombre"),
            "distancia_m": edge.get("distancia_m", 0),
            "maxspeed": edge.get("maxspeed"),
            "highway": edge.get("highway"),
            "oneway": edge.get("oneway", False)
        })

    return resultado


# =========================================================
# 10. OBTENER COSTO DE UNA CONEXIÓN
# =========================================================
def obtener_costo_edge(grafo, source, target, criterio="distancia"):
    """
    Devuelve el costo de una conexión según el criterio:

    distancia → metros
    tiempo    → minutos
    trafico   → factor de tráfico

    Si existen varias conexiones, devuelve la de menor costo.
    """

    if not grafo.has_edge(source, target):
        return None

    edges = grafo.get_edge_data(source, target)

    costos = []

    campo = {
        "distancia": "distancia_m",
        "tiempo": "tiempo_min",
        "trafico": "trafico"
    }.get(criterio)

    if campo is None:
        raise ValueError("Criterio no válido")

    for edge in edges.values():

        costo = edge.get(campo)

        if costo is not None:
            costos.append(costo)

    if not costos:
        return None

    return min(costos)


# =========================================================
# 11. OBTENER ESTADÍSTICAS DEL GRAFO
# =========================================================
def obtener_estadisticas(grafo):
    """
    Devuelve información general del grafo.
    """

    return {
        "nodos": grafo.number_of_nodes(),
        "edges": grafo.number_of_edges(),
        "dirigido": grafo.is_directed(),
        "multigrafo": grafo.is_multigraph()
    }