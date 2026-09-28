from app.models.route_request import RouteRequest


from app.shemas.route import RouteRequest


def calculate_route(request: RouteRequest):
    """
    Coordina el cálculo de una ruta.

    Recibe:
    - origen
    - destino
    - algoritmo

    Luego selecciona el algoritmo correspondiente.
    """

    algorithm = request.algorithm.lower()


    if algorithm == "brute_force":
        return calculate_with_brute_force(request)

    elif algorithm == "backtracking":
        return calculate_with_backtracking(request)

    elif algorithm == "divide_conquer":
        return calculate_with_divide_conquer(request)

    else:
        raise ValueError(
            f"Algoritmo no soportado: {request.algorithm}"
        )





def calculate_with_brute_force(request: RouteRequest):
    """
    Calcula una ruta utilizando Fuerza Bruta.
    """

    return {
        "algorithm": "brute_force",
        "distance_km": 0,
        "estimated_time_min": 0,
        "nodes_explored": 0,
        "route": [
            {
                "lat": request.origin.lat,
                "lon": request.origin.lon
            },
            {
                "lat": request.destination.lat,
                "lon": request.destination.lon
            }
        ]
    }


def calculate_with_backtracking(request: RouteRequest):
    """
    Calcula una ruta utilizando Backtracking.
    """

    return {
        "algorithm": "backtracking",
        "distance_km": 0,
        "estimated_time_min": 0,
        "nodes_explored": 0,
        "route": [
            {
                "lat": request.origin.lat,
                "lon": request.origin.lon
            },
            {
                "lat": request.destination.lat,
                "lon": request.destination.lon
            }
        ]
    }


def calculate_with_divide_conquer(request: RouteRequest):
    """
    Calcula una ruta utilizando Divide y Vencerás.
    """

    return {
        "algorithm": "divide_conquer",
        "distance_km": 0,
        "estimated_time_min": 0,
        "nodes_explored": 0,
        "route": [
            {
                "lat": request.origin.lat,
                "lon": request.origin.lon
            },
            {
                "lat": request.destination.lat,
                "lon": request.destination.lon
            }
        ]
    }