import os


class Settings:

    PROJECT_NAME: str = "Rappi - Optimización de Rutas"

    VERSION: str = "1.0.0"

    API_PREFIX: str = "/api"

    FRONTEND_URL: str = os.getenv(
        "FRONTEND_URL",
        "http://localhost:3000"
    )

    BACKEND_URL: str = os.getenv(
        "BACKEND_URL",
        "http://localhost:8000"
    )

    CITY: str = "Lima"

    DISTRICTS: list[str] = [
        "Miraflores",
        "San Isidro"
    ]

    MIN_GRAPH_NODES: int = 1500


settings = Settings()