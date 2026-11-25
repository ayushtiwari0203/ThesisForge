"""FastAPI entrypoint and ASGI application for ThesisForge AI."""

from __future__ import annotations
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.routes import router as api_router
from database.repository import Repository
from database.seed_data import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    repo = Repository()
    assets = repo.list_assets()
    if not assets:
        print("[Startup] Initializing seed data and demo document pack...")
        seed_database(repo)
    yield


app = FastAPI(
    title="ThesisForge AI - Investment Committee API",
    description="India-first, evidence-grounded investment research platform powered by multi-agent debate.",
    version="1.0.0",
    lifespan=lifespan,
)

raw_cors = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000")
origins = [o.strip() for o in raw_cors.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
def health_check():
    repo = Repository()
    assets = repo.list_assets()
    return {
        "status": "healthy",
        "service": "ThesisForge AI",
        "version": "1.0.0",
        "assets_loaded": len(assets),
        "database": "sqlite_active",
        "location": "Desktop/4vu5h/MTM606/web-app",
    }


frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/")
    def serve_index():
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "ThesisForge AI API active. Frontend index.html not found."}


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    print(f"Starting ThesisForge AI from {Path(__file__).resolve().parent.parent}")
    print(f"Web UI: http://localhost:{port}")
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
