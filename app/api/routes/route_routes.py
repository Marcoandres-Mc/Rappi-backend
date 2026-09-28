from fastapi import APIRouter

router = APIRouter(
    prefix="/routes",
    tags=["Routes"]
)


@router.get("/")
def get_routes():
    return {
        "message": "Módulo de rutas funcionando"
    }


@router.post("/calculate")
def calculate_route(data: dict):
    return {
        "message": "Solicitud de ruta recibida",
        "data": data
    }