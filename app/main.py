from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.route_routes import router as route_router


app = FastAPI(
    title="Rappi - Optimización de Rutas",
    description="Sistema de optimización de rutas para Miraflores y San Isidro",
    version="1.0.0"
)


# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://rappi-frontend-alpha.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Registrar endpoints
app.include_router(route_router)


@app.get("/")
def root():
    return {
        "message": "Backend conectado y funcionando"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }