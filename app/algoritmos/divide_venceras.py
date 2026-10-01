from dataclasses import dataclass
from itertools import permutations, product
from math import isfinite


Coordinate = tuple[float, float]


@dataclass(frozen=True)
class DivideConquerResult:
    order: list[int]
    total_cost: float
    states_explored: int
    divisions: int
    is_optimal: bool = False


def divide_venceras(
    cost_matrix: list[list[float]],
    coordinates: list[Coordinate],
    return_to_origin: bool = False,
    base_case_size: int = 3,
) -> DivideConquerResult:
    """
    Construye una ruta aproximada mediante
    particiones geográficas.
    """

    validate_inputs(
        cost_matrix,
        coordinates,
        base_case_size,
    )

    delivery_indexes = list(
        range(1, len(cost_matrix))
    )

    if not delivery_indexes:
        return DivideConquerResult(
            order=[0],
            total_cost=0.0,
            states_explored=1,
            divisions=0,
        )

    states_explored = 0
    divisions = 0

    def solve(
        indexes: list[int],
    ) -> list[int]:
        nonlocal states_explored
        nonlocal divisions

        # Caso base: evaluar todas las
        # permutaciones del grupo pequeño.
        if len(indexes) <= base_case_size:
            best_sequence = None
            best_cost = float("inf")

            for candidate in permutations(indexes):
                sequence = list(candidate)

                cost = sequence_cost(
                    cost_matrix,
                    sequence,
                )

                states_explored += 1

                if cost < best_cost:
                    best_cost = cost
                    best_sequence = sequence

            return best_sequence or []

        divisions += 1

        latitude_range = (
            max(
                coordinates[index][0]
                for index in indexes
            )
            - min(
                coordinates[index][0]
                for index in indexes
            )
        )

        longitude_range = (
            max(
                coordinates[index][1]
                for index in indexes
            )
            - min(
                coordinates[index][1]
                for index in indexes
            )
        )

        # 0 = latitud, 1 = longitud.
        axis = (
            0
            if latitude_range >= longitude_range
            else 1
        )

        ordered_indexes = sorted(
            indexes,
            key=lambda index:
                coordinates[index][axis],
        )

        middle = len(ordered_indexes) // 2

        left = solve(
            ordered_indexes[:middle]
        )

        right = solve(
            ordered_indexes[middle:]
        )

        candidates = []

        # Probar ambos órdenes de los grupos
        # y ambas orientaciones internas.
        for first, second in (
            (left, right),
            (right, left),
        ):
            for reverse_first, reverse_second in product(
                (False, True),
                repeat=2,
            ):
                first_part = (
                    list(reversed(first))
                    if reverse_first
                    else first
                )

                second_part = (
                    list(reversed(second))
                    if reverse_second
                    else second
                )

                candidates.append([
                    *first_part,
                    *second_part,
                ])

        states_explored += len(candidates)

        return min(
            candidates,
            key=lambda sequence:
                sequence_cost(
                    cost_matrix,
                    sequence,
                ),
        )

    delivery_order = solve(
        delivery_indexes
    )

    final_order = [
        0,
        *delivery_order,
    ]

    if return_to_origin:
        final_order.append(0)

    return DivideConquerResult(
        order=final_order,
        total_cost=order_cost(
            cost_matrix,
            final_order,
        ),
        states_explored=states_explored,
        divisions=divisions,
    )


def sequence_cost(
    cost_matrix: list[list[float]],
    delivery_sequence: list[int],
) -> float:
    return order_cost(
        cost_matrix,
        [0, *delivery_sequence],
    )


def order_cost(
    cost_matrix: list[list[float]],
    order: list[int],
) -> float:
    return sum(
        cost_matrix[origin][destination]
        for origin, destination
        in zip(order, order[1:])
    )


def validate_inputs(
    cost_matrix: list[list[float]],
    coordinates: list[Coordinate],
    base_case_size: int,
) -> None:
    if not cost_matrix:
        raise ValueError(
            "La matriz no puede estar vacía."
        )

    size = len(cost_matrix)

    if any(
        len(row) != size
        for row in cost_matrix
    ):
        raise ValueError(
            "La matriz debe ser cuadrada."
        )

    if len(coordinates) != size:
        raise ValueError(
            "Debe existir una coordenada "
            "por cada fila de la matriz."
        )

    if base_case_size < 1:
        raise ValueError(
            "El caso base debe contener "
            "al menos un destino."
        )

    if any(
        not isfinite(cost) or cost < 0
        for row in cost_matrix
        for cost in row
    ):
        raise ValueError(
            "Los costos deben ser finitos "
            "y no negativos."
        )