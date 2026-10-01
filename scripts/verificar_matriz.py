from app.graph.graph_builder import (
    build_adjacency_list,
    prepare_graph,
)

from app.algoritmos.fuerza_bruta import (
    fuerza_bruta,
)

from app.algoritmos.backtracking import (
    backtracking,
)

from app.algoritmos.divide_venceras import (
    divide_venceras,
)

from app.graph.graph_loader import load_city_graph
from app.graph.graph_utils import find_nearest_node
from app.services.cost_matrix_service import (
    build_cost_matrix,
)


locations = [
    {
        "name": "Depósito Miraflores",
        "lat": -12.1219,
        "lon": -77.0297,
    },
    {
        "name": "Entrega San Isidro",
        "lat": -12.0925,
        "lon": -77.0365,
    },
    {
        "name": "Entrega Reducto",
        "lat": -12.1328,
        "lon": -77.0225,
    },
    {
        "name": "Entrega Larcomar",
        "lat": -12.1317,
        "lon": -77.0307,
    },
]


graph = load_city_graph()
prepared_graph = prepare_graph(
    graph,
    hour=8,
)

adjacency = build_adjacency_list(
    prepared_graph
)

nodes = [
    find_nearest_node(
        prepared_graph,
        location["lat"],
        location["lon"],
    )
    for location in locations
]

print("NODOS SELECCIONADOS")
print("-------------------")

for location, node in zip(locations, nodes):
    print(location["name"], "->", node)

assert len(nodes) == len(set(nodes)), (
    "Dos ubicaciones fueron asociadas "
    "al mismo nodo."
)

result = build_cost_matrix(
    adjacency,
    nodes,
)

print("\nMATRIZ DE COSTOS")
print("----------------")

for row in result.costs:
    print([
        round(value, 2)
        for value in row
    ])

print(
    "\nNodos visitados por Dijkstra:",
    result.nodes_visited,
)

print(
    "Camino depósito -> primera entrega:",
    result.paths[0][1],
)

print(
    "Cantidad de nodos del camino:",
    len(result.paths[0][1]),
)


size = len(nodes)

for index in range(size):
    assert result.costs[index][index] == 0
    assert result.paths[index][index] == [
        nodes[index]
    ]

for origin in range(size):
    for destination in range(size):
        if origin != destination:
            assert (
                result.costs[origin][destination]
                > 0
            )

            assert len(
                result.paths[origin][destination]
            ) >= 2

print("\nTODAS LAS VALIDACIONES PASARON")
print("La matriz está lista para TSP.")









brute_force_result = fuerza_bruta(
    result.costs,
    return_to_origin=False,
)

print("\nRESULTADO DE FUERZA BRUTA")
print("-------------------------")

print(
    "Orden por índices:",
    brute_force_result.order,
)

print(
    "Costo total:",
    brute_force_result.total_cost,
)

print(
    "Permutaciones evaluadas:",
    brute_force_result.states_explored,
)

location_order = [
    locations[index]["name"]
    for index in brute_force_result.order
]

print(
    "Orden de ubicaciones:",
    " -> ".join(location_order),
)

assert brute_force_result.order[0] == 0
assert brute_force_result.total_cost > 0
assert brute_force_result.states_explored == 6

print("\nFUERZA BRUTA FUNCIONA CORRECTAMENTE")















backtracking_result = backtracking(
    result.costs,
    return_to_origin=False,
)

print("\nRESULTADO DE BACKTRACKING")
print("-------------------------")

print(
    "Orden:",
    backtracking_result.order,
)

print(
    "Costo total:",
    backtracking_result.total_cost,
)

print(
    "Estados explorados:",
    backtracking_result.states_explored,
)

print(
    "Ramas podadas:",
    backtracking_result.branches_pruned,
)

backtracking_location_order = [
    locations[index]["name"]
    for index in backtracking_result.order
]

print(
    "Orden de ubicaciones:",
    " -> ".join(backtracking_location_order),
)

assert (
    backtracking_result.total_cost
    == brute_force_result.total_cost
)

assert (
    backtracking_result.order
    == brute_force_result.order
)

assert (
    backtracking_result.branches_pruned
    > 0
)

print(
    "\nBACKTRACKING Y FUERZA BRUTA "
    "OBTUVIERON LA MISMA SOLUCIÓN ÓPTIMA"
)













coordinates = [
    (
        location["lat"],
        location["lon"],
    )
    for location in locations
]

divide_result = divide_venceras(
    result.costs,
    coordinates,
    return_to_origin=False,
    base_case_size=2,
)

print("\nRESULTADO DE DIVIDE Y VENCERÁS")
print("------------------------------")

print(
    "Orden:",
    divide_result.order,
)

print(
    "Costo:",
    divide_result.total_cost,
)

print(
    "Estados evaluados:",
    divide_result.states_explored,
)

print(
    "Divisiones realizadas:",
    divide_result.divisions,
)

print(
    "¿Garantiza optimalidad?:",
    divide_result.is_optimal,
)

divide_location_order = [
    locations[index]["name"]
    for index in divide_result.order
]

print(
    "Recorrido:",
    " -> ".join(divide_location_order),
)

assert divide_result.order[0] == 0
assert sorted(divide_result.order[1:]) == [
    1,
    2,
    3,
]
assert divide_result.total_cost > 0
assert divide_result.is_optimal is False

quality_difference = (
    (
        divide_result.total_cost
        - brute_force_result.total_cost
    )
    / brute_force_result.total_cost
    * 100
)

print(
    "Diferencia frente al óptimo:",
    round(quality_difference, 2),
    "%",
)

print(
    "\nDIVIDE Y VENCERÁS "
    "FUNCIONA CORRECTAMENTE"
)