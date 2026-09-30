
from pydantic import BaseModel, Field
from typing import Optional


# =========================================================
# 1. ESQUEMA DE UN NODO
# =========================================================

class Nodo(BaseModel):
    id: str

    lat: float
    lon: float

    distrito: str


# =========================================================
# 2. ESQUEMA DE UNA ARISTA
# =========================================================

class Arista(BaseModel):
    source: str
    target: str

    calle: Optional[str] = "Sin nombre"

    distancia_m: float = Field(ge=0)

    tiempo_min: Optional[float] = Field(default=None, ge=0)

    trafico: Optional[float] = Field(default=None, ge=0)

    maxspeed: Optional[str] = None

    highway: Optional[str] = None

    oneway: Optional[bool] = False

    geometry: Optional[list[list[float]]] = None


# =========================================================
# 3. ESQUEMA DEL GRAFO COMPLETO
# =========================================================

class Grafo(BaseModel):
    nodes: list[Nodo]
    edges: list[Arista]


# =========================================================
# 4. ESQUEMA DE ESTADÍSTICAS
# =========================================================

class GrafoEstadisticas(BaseModel):
    nodos: int
    edges: int
    dirigido: bool
    multigrafo: bool