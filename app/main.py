from fastapi import FastAPI
from app.api.routes.route_routes import router as route_router


app = FastAPI(
    title="Rappi - Optimización de Rutas",
    description="Sistema de optimización de rutas para Miraflores y San Isidro",
    version="1.0.0"
)


# Registrar las rutas de la API
app.include_router(route_router)


@app.get("/")
def root():
    return {
        "message": "Backend de optimización de rutas funcionando correctamente"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }