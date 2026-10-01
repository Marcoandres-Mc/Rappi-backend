import logging

from fastapi import APIRouter, HTTPException

from app.schemas.route import (
    DeliveryRouteRequest,
    DeliveryRouteResponse,
    RouteRequest,
    RouteResponse,
)
from app.services.delivery_service import (
    calculate_delivery_route,
)
from app.services.route_service import calculate_route

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/routes",
    tags=["Routes"],
)


@router.get("/")
def get_routes():
    return {
        "message": "Módulo de rutas funcionando",
        "algorithms": {
            "direct_route": ["dijkstra"],
            "deliveries": [
                {
                    "name": "brute_force",
                    "max_deliveries": 8,
                    "optimal": True,
                },
                {
                    "name": "backtracking",
                    "max_deliveries": 12,
                    "optimal": True,
                },
                {
                    "name": "divide_conquer",
                    "max_deliveries": 30,
                    "optimal": False,
                },
            ],
        },
    }


@router.post(
    "/calculate",
    response_model=RouteResponse,
)
def calculate_route_endpoint(request: RouteRequest):
    try:
        return calculate_route(request)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception("Error en /routes/calculate")
        raise HTTPException(
            status_code=500,
            detail="Error interno al calcular la ruta",
        ) from error


@router.post(
    "/deliveries",
    response_model=DeliveryRouteResponse,
)
def calculate_deliveries_endpoint(
    request: DeliveryRouteRequest,
):
    try:
        return calculate_delivery_route(request)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception("Error en /routes/deliveries")
        raise HTTPException(
            status_code=500,
            detail=(
                "Error interno al optimizar "
                "las entregas"
            ),
        ) from error