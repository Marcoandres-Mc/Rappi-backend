from typing import Literal

from pydantic import BaseModel, Field



class Coordinate(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)


class RouteRequest(BaseModel):
    origin: Coordinate
    destination: Coordinate

    algorithm: Literal[
        "dijkstra",
        "brute_force",
        "backtracking",
        "divide_conquer",
    ] = "dijkstra"

    traffic_hour: int = Field(
        default=12,
        ge=0,
        le=23,
    )


class RouteResponse(BaseModel):
    algorithm: str
    execution_time_ms: float
    nodos_visitados: int
    distancia_total_m: float
    weighted_cost: float
    path: list[Coordinate]



class DeliveryRouteRequest(BaseModel):
    origin: Coordinate

    destinations: list[Coordinate] = Field(
        min_length=1,
        max_length=30,
    )

    algorithm: Literal[
        "brute_force",
        "backtracking",
        "divide_conquer",
    ]

    traffic_hour: int = Field(
        default=12,
        ge=0,
        le=23,
    )

    return_to_origin: bool = False


class DeliveryRouteResponse(BaseModel):
    algorithm: str
    execution_time_ms: float
    matrix_time_ms: float
    nodos_visitados: int
    states_explored: int
    branches_pruned: int
    distancia_total_m: float
    weighted_cost: float
    delivery_order: list[int]
    is_optimal: bool
    path: list[Coordinate]