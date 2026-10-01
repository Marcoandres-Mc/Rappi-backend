from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class BacktrackingResult:
    order: list[int]
    total_cost: float
    states_explored: int
    branches_pruned: int


def backtracking(
    cost_matrix: list[list[float]],
    return_to_origin: bool = False,
) -> BacktrackingResult:
    """
    Resuelve el orden de entregas exactamente
    mediante búsqueda con poda.
    """

    validate_cost_matrix(cost_matrix)

    size = len(cost_matrix)

    if size == 1:
        return BacktrackingResult(
            order=[0],
            total_cost=0.0,
            states_explored=1,
            branches_pruned=0,
        )

    best_order, best_cost = greedy_upper_bound(
        cost_matrix,
        return_to_origin,
    )

    states_explored = 0
    branches_pruned = 0

    def search(
        current: int,
        remaining: tuple[int, ...],
        current_order: list[int],
        current_cost: float,
    ) -> None:
        nonlocal best_order
        nonlocal best_cost
        nonlocal states_explored
        nonlocal branches_pruned

        states_explored += 1

        if not remaining:
            final_cost = current_cost
            final_order = current_order

            if return_to_origin:
                final_cost += cost_matrix[current][0]
                final_order = [
                    *current_order,
                    0,
                ]

            if final_cost < best_cost:
                best_cost = final_cost
                best_order = final_order.copy()

            return

        candidates = sorted(
            remaining,
            key=lambda destination:
                cost_matrix[current][destination],
        )

        for destination in candidates:
            candidate_cost = (
                current_cost
                + cost_matrix[current][destination]
            )

            if candidate_cost >= best_cost:
                branches_pruned += 1
                continue

            next_remaining = tuple(
                node
                for node in remaining
                if node != destination
            )

            search(
                destination,
                next_remaining,
                [
                    *current_order,
                    destination,
                ],
                candidate_cost,
            )

    search(
        current=0,
        remaining=tuple(range(1, size)),
        current_order=[0],
        current_cost=0.0,
    )

    return BacktrackingResult(
        order=best_order,
        total_cost=best_cost,
        states_explored=states_explored,
        branches_pruned=branches_pruned,
    )


def greedy_upper_bound(
    cost_matrix: list[list[float]],
    return_to_origin: bool,
) -> tuple[list[int], float]:
    """
    Construye una solución inicial para comenzar
    backtracking con una cota superior.
    """

    remaining = set(
        range(1, len(cost_matrix))
    )

    order = [0]
    current = 0
    total_cost = 0.0

    while remaining:
        destination = min(
            remaining,
            key=lambda node:
                cost_matrix[current][node],
        )

        total_cost += (
            cost_matrix[current][destination]
        )

        order.append(destination)
        remaining.remove(destination)
        current = destination

    if return_to_origin:
        total_cost += cost_matrix[current][0]
        order.append(0)

    return order, total_cost


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

    if any(
        not isfinite(cost) or cost < 0
        for row in cost_matrix
        for cost in row
    ):
        raise ValueError(
            "La matriz solo puede contener "
            "costos finitos no negativos."
        )