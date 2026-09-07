import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routers.supermarkets import router as supermarkets_router
from app.api.routers.menus import router as menus_router

app = FastAPI(
    title="NutriSuper Planner API",
    description="AI Meal & Macro Planner with real-time Supermarket Integrations (Mercadona, Aldi)",
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

# Include Routers
app.include_router(supermarkets_router)
app.include_router(menus_router)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "NutriSuper Planner",
        "patterns": ["Strategy", "Factory Method", "Adapter", "Proxy/Cache", "Chain of Responsibility", "Builder", "Repository"]
    }


# Frontend static files path
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "frontend"))

if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    def serve_frontend():
        index_file = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Frontend index.html not found, but API is running!"}
