from dataclasses import dataclass
from itertools import permutations
from math import isfinite


@dataclass(frozen=True)
class BruteForceResult:
    order: list[int]
    total_cost: float
    states_explored: int


def fuerza_bruta(
    cost_matrix: list[list[float]],
    return_to_origin: bool = False,
) -> BruteForceResult:
    """
    Encuentra el orden óptimo de las entregas.

    El índice 0 representa el depósito.
    """

    validate_cost_matrix(cost_matrix)

    delivery_indexes = range(
        1,
        len(cost_matrix),
    )

    best_order = None
    best_cost = float("inf")
    states_explored = 0

    for delivery_order in permutations(
        delivery_indexes
    ):
        candidate_order = [
            0,
            *delivery_order,
        ]

        if return_to_origin:
            candidate_order.append(0)

        candidate_cost = calculate_order_cost(
            cost_matrix,
            candidate_order,
        )

        states_explored += 1

        if candidate_cost < best_cost:
            best_cost = candidate_cost
            best_order = candidate_order

    # Caso donde solo existe el depósito.
    if best_order is None:
        best_order = [0]
        best_cost = 0.0
        states_explored = 1

    return BruteForceResult(
        order=best_order,
        total_cost=best_cost,
        states_explored=states_explored,
    )


def calculate_order_cost(
    cost_matrix: list[list[float]],
    order: list[int],
) -> float:
    return sum(
        cost_matrix[origin][destination]
        for origin, destination
        in zip(order, order[1:])
    )


def validate_cost_matrix(
    cost_matrix: list[list[float]],
) -> None:
    if not cost_matrix:
        raise ValueError(
            "La matriz de costos no puede estar vacía."
        )

    size = len(cost_matrix)

    if any(
        len(row) != size
        for row in cost_matrix
    ):
        raise ValueError(
            "La matriz de costos debe ser cuadrada."
        )

    for row in cost_matrix:
        for cost in row:
            if not isfinite(cost) or cost < 0:
                raise ValueError(
                    "La matriz solo puede contener "
                    "costos finitos no negativos."
                )