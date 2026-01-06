# backend/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.file_router import router as file_router
from backend.routers.prompt_router import router as prompt_router
from backend.routers.image_generation_router import router as image_generation_router
from backend.routers.video_generation_router import router as video_generation_router


app = FastAPI(
    title="Course Visual Generation Platform",
    description=(
        "A JSON-driven platform for generating course visuals using AI. "
        "Supports file upload, storyboard prompt generation, image generation, and video generation."
    ),
    version="2.0.0",
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------
# Routers
# -------------------------------------------------
app.include_router(file_router)
app.include_router(prompt_router)
app.include_router(image_generation_router)
app.include_router(video_generation_router)


# -------------------------------------------------
# Health / Root
# -------------------------------------------------
@app.get("/api/info", tags=["health"])
async def root():
    """
    API Information endpoint.
    
    Returns system status and version information.
    """
    return {
        "service": "Course Visual Generation Platform",
        "status": "running",
        "version": "2.0.0",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",  # Add actual DB check if needed
        "ai_services": {
            "openai": "configured",
            "higgsfield": "configured",
        }
    }

# -------------------------------------------------
# Frontend Static Files
# -------------------------------------------------
frontend_dir = os.path.join(os.path.dirname(__file__), "../frontend_dist")

if os.path.exists(frontend_dir):
    # Mount assets folder
    assets_dir = os.path.join(frontend_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # Catch-all for SPA
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Check if file exists in frontend_dir
        potential_path = os.path.join(frontend_dir, full_path)
        if os.path.exists(potential_path) and os.path.isfile(potential_path):
            return FileResponse(potential_path)
        
        # Default to index.html for unknown routes (SPA)
        # But ensure we don't capture API routes if they fell through (though they shouldn't)
        return FileResponse(os.path.join(frontend_dir, "index.html"))

