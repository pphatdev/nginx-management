from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from core.routers import api, pages

BASE_DIR = Path(__file__).resolve().parent

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class HeadMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "HEAD":
            # Change method to GET to let the route handler process it
            request.scope["method"] = "GET"
            response = await call_next(request)
            return Response(
                content=b"",
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
        return await call_next(request)

app = FastAPI(title="Nginx Management UI", version="1.0.0")
app.add_middleware(HeadMiddleware)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "client" / "static")), name="static")

app.include_router(pages.router)
app.include_router(api.router)

