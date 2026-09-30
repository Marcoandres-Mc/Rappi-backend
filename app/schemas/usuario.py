from pydantic import BaseModel


class Usuario(BaseModel):
    id: int
    nombre: str
    producto: str
    ubicacion_actual: str