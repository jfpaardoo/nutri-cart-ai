import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routers.supermarkets import router as supermarkets_router
from app.api.routers.menus import router as menus_router

app = FastAPI(
    title="ComeYCuadra API",
    description="Planificador nutricional con integracion de supermercados en tiempo real (Mercadona, Aldi)",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers first so /api takes priority over static files
app.include_router(supermarkets_router)
app.include_router(menus_router)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ComeYCuadra",
        "patterns": ["Strategy", "Factory Method", "Adapter", "Proxy/Cache", "Chain of Responsibility", "Builder", "Repository"]
    }


# Mount Frontend static directory at root
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "frontend"))

if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
