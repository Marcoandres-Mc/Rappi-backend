"""
Tests de los algoritmos puros (no necesitan el grafo real).
Ejecutar:  python -m pytest -v
"""
import random

import pytest

from app.algoritmos.backtracking import backtracking
from app.algoritmos.dijkstra import (
    PathNotFoundError,
    dijkstra,
    dijkstra_to_targets,
)
from app.algoritmos.divide_venceras import divide_venceras
from app.algoritmos.fuerza_bruta import fuerza_bruta
from app.graph.graph_builder import get_traffic_factor
from app.services.cost_matrix_service import build_cost_matrix


# ---------- utilidades ----------

def random_matrix(size: int, seed: int) -> list[list[float]]:
    """Matriz asimétrica (como un grafo con calles de un solo sentido)."""
    rng = random.Random(seed)
    return [
        [0.0 if i == j else round(rng.uniform(1, 100), 2) for j in range(size)]
        for i in range(size)
    ]


def random_coordinates(size: int, seed: int) -> list[tuple[float, float]]:
    rng = random.Random(seed)
    return [
        (-12.12 + rng.uniform(0, 0.03), -77.04 + rng.uniform(0, 0.03))
        for _ in range(size)
    ]


def assert_valid_order(order: list[int], size: int, returns: bool) -> None:
    """Empieza en 0, visita cada entrega una sola vez (y vuelve a 0 si aplica)."""
    assert order[0] == 0
    visited = order[1:-1] if returns else order[1:]
    if returns:
        assert order[-1] == 0
    assert sorted(visited) == list(range(1, size))


# ---------- Dijkstra ----------

GRAPH = {
    1: [(2, 1.0), (3, 4.0)],
    2: [(3, 1.0)],
    3: [],
    4: [],
}


def test_dijkstra_encuentra_camino_minimo():
    result = dijkstra(GRAPH, 1, 3)
    assert result.path == [1, 2, 3]
    assert result.total_cost == pytest.approx(2.0)


def test_dijkstra_mismo_origen_y_destino():
    result = dijkstra(GRAPH, 1, 1)
    assert result.path == [1]
    assert result.total_cost == 0.0


def test_dijkstra_sin_camino():
    with pytest.raises(PathNotFoundError):
        dijkstra(GRAPH, 1, 4)


def test_dijkstra_nodo_inexistente():
    with pytest.raises(ValueError):
        dijkstra(GRAPH, 1, 99)


def test_dijkstra_rechaza_pesos_negativos():
    with pytest.raises(ValueError, match="negativos"):
        dijkstra({1: [(2, -1.0)], 2: []}, 1, 2)


def test_dijkstra_to_targets_coincide_con_dijkstra():
    results, visited = dijkstra_to_targets(GRAPH, 1, {2, 3})
    assert visited > 0
    for target in (2, 3):
        esperado = dijkstra(GRAPH, 1, target)
        assert results[target].total_cost == pytest.approx(esperado.total_cost)
        assert results[target].path == esperado.path


# ---------- Matriz de costos ----------

def test_matriz_de_costos_es_asimetrica_y_correcta():
    ciclo = {1: [(2, 1.0)], 2: [(3, 1.0)], 3: [(1, 5.0)]}
    matrix = build_cost_matrix(ciclo, [1, 2, 3])
    assert matrix.costs == [
        [0.0, 1.0, 2.0],
        [6.0, 0.0, 1.0],
        [5.0, 6.0, 0.0],
    ]
    assert matrix.paths[0][2] == [1, 2, 3]


def test_matriz_rechaza_nodos_repetidos():
    with pytest.raises(ValueError):
        build_cost_matrix(GRAPH, [1, 1])


def test_matriz_falla_si_no_hay_camino():
    with pytest.raises(PathNotFoundError):
        build_cost_matrix(GRAPH, [1, 3])  # de 3 no se llega a 1


# ---------- TSP: fuerza bruta vs backtracking ----------

@pytest.mark.parametrize("returns", [False, True])
@pytest.mark.parametrize("size", [2, 3, 4, 5, 6, 7])
@pytest.mark.parametrize("seed", [1, 2, 3])
def test_backtracking_igual_a_fuerza_bruta(size, seed, returns):
    matrix = random_matrix(size, seed)
    brute = fuerza_bruta(matrix, returns)
    back = backtracking(matrix, returns)

    assert back.total_cost == pytest.approx(brute.total_cost)
    assert_valid_order(brute.order, size, returns)
    assert_valid_order(back.order, size, returns)


def test_backtracking_explora_menos_que_fuerza_bruta():
    matrix = random_matrix(8, seed=7)
    brute = fuerza_bruta(matrix)
    back = backtracking(matrix)
    assert back.states_explored < brute.states_explored
    assert back.branches_pruned > 0


def test_solo_deposito():
    assert fuerza_bruta([[0.0]]).order == [0]
    assert backtracking([[0.0]]).order == [0]


def test_fuerza_bruta_cuenta_permutaciones():
    assert fuerza_bruta(random_matrix(5, 1)).states_explored == 24  # 4!


def test_matriz_invalida():
    with pytest.raises(ValueError):
        fuerza_bruta([])
    with pytest.raises(ValueError):
        fuerza_bruta([[0.0, 1.0]])
    with pytest.raises(ValueError):
        backtracking([[0.0, -1.0], [1.0, 0.0]])


# ---------- Divide y vencerás ----------

@pytest.mark.parametrize("returns", [False, True])
@pytest.mark.parametrize("size", [3, 6, 8, 10])
@pytest.mark.parametrize("seed", [1, 2, 3])
def test_divide_venceras_valido_y_no_mejor_que_el_optimo(size, seed, returns):
    matrix = random_matrix(size, seed)
    coords = random_coordinates(size, seed)

    dc = divide_venceras(matrix, coords, returns)
    optimo = backtracking(matrix, returns)

    assert_valid_order(dc.order, size, returns)
    assert dc.total_cost >= optimo.total_cost - 1e-9
    assert dc.is_optimal is False


def test_divide_venceras_soporta_30_entregas():
    size = 31  # depósito + 30
    dc = divide_venceras(random_matrix(size, 5), random_coordinates(size, 5))
    assert_valid_order(dc.order, size, returns=False)


# ---------- Tráfico ----------

@pytest.mark.parametrize(
    "hour,expected",
    [(0, 1.0), (3, 1.0), (7, 2.5), (9, 2.5), (10, 1.5),
     (16, 1.5), (17, 2.5), (19, 2.5), (20, 1.5), (22, 1.0), (23, 1.0)],
)
def test_factor_de_trafico(hour, expected):
    assert get_traffic_factor(hour) == expected


@pytest.mark.parametrize("hour", [-1, 24])
def test_hora_invalida(hour):
    with pytest.raises(ValueError):
        get_traffic_factor(hour)