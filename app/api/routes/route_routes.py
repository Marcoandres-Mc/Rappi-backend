from fastapi import APIRouter, HTTPException

from app.schemas.route import RouteRequest, RouteResponse
from app.services.route_service import calculate_route

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
