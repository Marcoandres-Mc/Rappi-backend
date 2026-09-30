from fastapi import APIRouter

from app.schemas.usuario import Usuario
from app.schemas.repartidor import Repartidor

from app.services.route_service import (
    crear_usuario,
    calculate_route
)

router = APIRouter(
    prefix="/routes",
    tags=["Routes"]
)


# =====================================
# USUARIO
# =====================================

@router.post("/usuario")
def registrar_usuario(usuario: Usuario):
    return crear_usuario(usuario)


# =====================================
# REPARTIDOR
# =====================================

@router.post("/repartidor")
def registrar_repartidor(repartidor: Repartidor):
    return calculate_route(repartidor)