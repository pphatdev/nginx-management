from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from core.routers import api, pages

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Nginx Management UI", version="1.0.0")

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "client" / "static")), name="static")

app.include_router(pages.router)
app.include_router(api.router)

