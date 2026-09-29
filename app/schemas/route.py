from typing import List, Optional, Literal
from pydantic import BaseModel


class Coordinate(BaseModel):
    lat: float
    lon: float


class RouteRequest(BaseModel):
    origin: Coordinate
    destination: Coordinate
    algorithm: Literal[
        "brute_force",
        "backtracking",
        "divide_conquer"
    ] = "backtracking"


class RouteResponse(BaseModel):
    algorithm: str
    distance_km: Optional[float] = None
    estimated_time_min: Optional[float] = None
    nodes_explored: Optional[int] = None
    branches_pruned: Optional[int] = None
    route: List[Coordinate]