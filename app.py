from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from core.routers import api, pages, ws
import os

app = FastAPI(title="Nginx Management API")

# Mount static files
app.mount("/static", StaticFiles(directory="www/static"), name="static")

# Include routers
app.include_router(api.router, prefix="/api")
app.include_router(ws.router)
app.include_router(pages.router)

if __name__ == "__main__":
    import uvicorn
    from core.config import settings
    uvicorn.run("app:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)
