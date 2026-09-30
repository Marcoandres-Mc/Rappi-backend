# =========================================================
# IMPORTACIONES
# =========================================================

from app.schemas.repartidor import Repartidor

from app.grafo.grafo_cargador import load_city_graph

from app.grafo.grafo_utilidades import (
    buscar_nodo_mas_cercano,
    obtener_coordenadas,
    obtener_distrito,
    obtener_estadisticas
)

from app.algoritmos.fuerza_bruta import (
    resolver_ruta as resolver_fuerza_bruta
)

from app.algoritmos.backtracking import (
    resolver_ruta as resolver_backtracking
)

from app.algoritmos.divide_conquer import (
    resolver_ruta as resolver_divide_conquer
)


# =========================================================
# CARGAR GRAFO
# =========================================================

GRAFO = load_city_graph()


# =========================================================
# INFORMACIÓN DEL GRAFO
# =========================================================

def obtener_informacion_grafo():

    return {
        "mensaje": "Información del grafo",
        "grafo": obtener_estadisticas(GRAFO)
    }


# =========================================================
# OBTENER NODO MÁS CERCANO A UNA UBICACIÓN
# =========================================================

def obtener_nodo_ubicacion(lat: float, lon: float):

    nodo = buscar_nodo_mas_cercano(
        GRAFO,
        lat,
        lon
    )

    if nodo is None:
        raise ValueError(
            "No se encontró un nodo cercano a la ubicación"
        )

    coordenadas = obtener_coordenadas(
        GRAFO,
        nodo
    )

    distrito = obtener_distrito(
        GRAFO,
        nodo
    )

    return {
        "id": nodo,
        "lat": coordenadas["lat"],
        "lon": coordenadas["lon"],
        "distrito": distrito
    }


# =========================================================
# EJECUTAR ALGORITMO
# =========================================================

def ejecutar_algoritmo(
    algoritmo,
    origen,
    destinos,
    criterio="distancia"
):

    if algoritmo == "fuerzaBruta":

        return resolver_fuerza_bruta(
            GRAFO,
            origen,
            destinos,
            criterio
        )

    elif algoritmo == "backtracking":

        return resolver_backtracking(
            GRAFO,
            origen,
            destinos,
            criterio
        )

    elif algoritmo == "divideVencenas":

        return resolver_divide_conquer(
            GRAFO,
            origen,
            destinos,
            criterio
        )

    else:

        raise ValueError(
            f"Algoritmo no válido: {algoritmo}"
        )


# =========================================================
# CALCULAR RUTA
# =========================================================

def calculate_route(
    repartidor: Repartidor,
    destinos: list[int],
    criterio: str = "distancia"
):

    # -----------------------------------------------------
    # 1. OBTENER UBICACIÓN DEL REPARTIDOR
    # -----------------------------------------------------

    ubicacion_inicial = repartidor.ubicacion_inicial

    if not ubicacion_inicial:

        raise ValueError(
            "La ubicación inicial es obligatoria"
        )


    # -----------------------------------------------------
    # 2. CONVERTIR UBICACIÓN A COORDENADAS
    # -----------------------------------------------------

    try:

        lat, lon = map(
            float,
            ubicacion_inicial.split(",")
        )

    except ValueError:

        raise ValueError(
            "La ubicación debe tener el formato: latitud,longitud"
        )


    # -----------------------------------------------------
    # 3. BUSCAR NODO DE ORIGEN
    # -----------------------------------------------------

    origen = obtener_nodo_ubicacion(
        lat,
        lon
    )


    # -----------------------------------------------------
    # 4. VALIDAR DESTINOS
    # -----------------------------------------------------

    if not destinos:

        raise ValueError(
            "Debe existir al menos un destino"
        )


    for destino in destinos:

        if destino not in GRAFO:

            raise ValueError(
                f"El nodo destino {destino} no existe en el grafo"
            )


    # -----------------------------------------------------
    # 5. EJECUTAR ALGORITMO
    # -----------------------------------------------------

    resultado = ejecutar_algoritmo(
        algoritmo=repartidor.algoritmo,
        origen=origen["id"],
        destinos=destinos,
        criterio=criterio
    )


    # -----------------------------------------------------
    # 6. OBTENER RUTA
    # -----------------------------------------------------

    ruta = resultado.get(
        "ruta",
        []
    )


    # -----------------------------------------------------
    # 7. PREPARAR PUNTOS PARA EL MAPA
    # -----------------------------------------------------

    puntos_mapa = []

    for node_id in ruta:

        coordenadas = obtener_coordenadas(
            GRAFO,
            node_id
        )

        if coordenadas is None:
            continue

        puntos_mapa.append({
            "id": node_id,
            "lat": coordenadas["lat"],
            "lon": coordenadas["lon"],
            "distrito": obtener_distrito(
                GRAFO,
                node_id
            )
        })


    # -----------------------------------------------------
    # 8. RESPUESTA
    # -----------------------------------------------------

    return {
        "mensaje": "Ruta calculada correctamente",

        "algoritmo": repartidor.algoritmo,

        "criterio": criterio,

        "origen": origen,

        "destinos": destinos,

        "ruta": ruta,

        "puntos_mapa": puntos_mapa,

        "costo_total": resultado.get(
            "costo_total"
        ),

        "estadisticas_grafo": obtener_estadisticas(
            GRAFO
        )
    }