from fastapi import APIRouter, HTTPException

from app.services.route_service import calculate_route

import logging
logger = logging.getLogger(__name__)


from app.schemas.route import (
    DeliveryRouteRequest,
    DeliveryRouteResponse,
    RouteRequest,
    RouteResponse,
)

from app.services.delivery_service import (
    calculate_delivery_route,
)

router = APIRouter(
    prefix="/routes",
    tags=["Routes"],
)


@router.get("/")
def get_routes():
    return {
        "message": "Módulo de rutas funcionando",
        "algorithms": [
            "dijkstra",
        ],
    }


@router.post(
    "/calculate",
    response_model=RouteResponse,
)
def calculate_route_endpoint(request: RouteRequest):
    try:
        return calculate_route(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc



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
        raise HTTPException(
            status_code=500,
            detail=(
                "Error interno al optimizar "
                "las entregas"
            ),
        ) from error