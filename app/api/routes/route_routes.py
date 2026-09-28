from fastapi import APIRouter, HTTPException

from app.schemas.route import RouteRequest
from app.services.route_service import calculate_route


router = APIRouter(
    prefix="/routes",
    tags=["Routes"]
)


@router.get("/")
def get_routes():
    return {
        "message": "Módulo de rutas funcionando",
        "algorithms": [
            "brute_force",
            "backtracking",
            "divide_conquer"
        ]
    }


@router.post("/calculate")
def calculate_route_endpoint(request: RouteRequest):

    try:
        result = calculate_route(request)
        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error interno al calcular la ruta"
        )