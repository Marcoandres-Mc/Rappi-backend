from fastapi import APIRouter

from app.schemas.usuario import Usuario
from app.schemas.repartidor import Repartidor
from app.schemas.pedido import Pedido
from app.services.pedido_service import crear_pedido
from app.services.route_service import (
    crear_usuario,
    calculate_route,
    obtener_informacion_grafo
)

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


@router.post("/pedido")
def registrar_pedido(pedido: Pedido):
    return crear_pedido(pedido)

@router.get("/grafo")
def consultar_grafo():

    try:

        return obtener_informacion_grafo()

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )