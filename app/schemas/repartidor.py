from typing import Literal
from pydantic import BaseModel


class Repartidor(BaseModel):
    ubicacion_inicial: str
    algoritmo: Literal[
        "fuerzaBruta",
        "backtracking",
        "divideVenceras"
    ]