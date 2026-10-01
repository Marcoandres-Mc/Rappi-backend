from math import isclose

from app.schemas.route import RouteRequest
from app.services.route_service import calculate_route


request = RouteRequest(
    origin={
        "lat": -12.1219,
        "lon": -77.0297,
    },
    destination={
        "lat": -12.0925,
        "lon": -77.0365,
    },
    algorithm="dijkstra",
    traffic_hour=8,
)

result = calculate_route(request)

print("\nRESULTADO DE DIJKSTRA")
print("---------------------")
print("Algoritmo:", result.algorithm)
print("Tiempo:", result.execution_time_ms, "ms")
print("Nodos visitados:", result.nodos_visitados)
print("Distancia:", result.distancia_total_m, "m")
print("Costo ponderado:", result.weighted_cost)
print("Coordenadas:", len(result.path))
print("Inicio:", result.path[0])
print("Fin:", result.path[-1])

assert result.algorithm == "dijkstra"
assert result.execution_time_ms >= 0
assert result.nodos_visitados > 0
assert result.distancia_total_m > 0
assert result.weighted_cost > 0
assert len(result.path) >= 2

# A las 08:00 el factor configurado es 2.5.
assert isclose(
    result.weighted_cost,
    result.distancia_total_m * 2.5,
    rel_tol=1e-6,
)

print("\nTODAS LAS VALIDACIONES PASARON")
print("Dijkstra funciona correctamente.")