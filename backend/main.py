from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import AUTH_MODE
from app.database import engine, Base
from app import models  # noqa: F401 - registers models with Base
from app.api import entries, lookups, users, auth, snapshots

# Create tables on startup (schema sbfo_ro must already exist in PostgreSQL)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SBFO R&O Tracker API", version="1.0.0")

if AUTH_MODE == "LOCAL":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # DBX mode: Databricks Apps proxy handles authentication
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(entries.router, prefix="/api/entries", tags=["entries"])
app.include_router(lookups.router, prefix="/api/lookups", tags=["lookups"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(snapshots.router, prefix="/api/snapshots", tags=["snapshots"])


@app.get("/health")
def health():
    return {"status": "ok"}


def _find_frontend_dist() -> Path | None:
    search_bases = [
        Path(__file__).parent.parent,  # project root (one level above backend/)
        Path.cwd(),
        Path("/app/python/source_code"),
    ]
    for base in search_bases:
        dist = base / "frontend" / "dist"
        if dist.exists() and (dist / "index.html").exists():
            return dist
    return None


_dist = _find_frontend_dist()

if _dist:
    assets_dir = _dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/")
    async def root():
        return FileResponse(str(_dist / "index.html"))

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith(("api/", "docs", "redoc", "openapi.json", "assets/")):
            return {"detail": "Not found"}
        return FileResponse(str(_dist / "index.html"))

else:
    @app.get("/")
    async def root():
        return {"error": "Frontend not built.", "fix": "Run 'cd frontend && npm run build'"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8008, reload=True)
