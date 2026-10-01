import random

from app.algoritmos.dijkstra import dijkstra
from app.services.cost_matrix_service import build_cost_matrix
from app.services.route_service import (
    get_prepared_graph,
)

graph, adjacency = get_prepared_graph(8)

random.seed(1)
nodes = random.sample(list(adjacency), 6)

matrix = build_cost_matrix(adjacency, nodes)

for i, a in enumerate(nodes):
    for j, b in enumerate(nodes):
        if i == j:
            continue
        esperado = dijkstra(adjacency, a, b).total_cost
        obtenido = matrix.costs[i][j]
        assert abs(esperado - obtenido) < 1e-6, (a, b)

print("OK: la matriz coincide con Dijkstra punto a punto")