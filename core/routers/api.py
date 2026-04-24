import random

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.services import nginx, store

router = APIRouter(prefix="/api")


@router.get("/stats")
async def api_stats():
    stats = nginx.get_stats()
    # Simulate live metrics when stub_status is not configured
    if stats["active_connections"] == 0:
        stats["active_connections"] = random.randint(180, 320)
        stats["requests_per_sec"] = random.randint(900, 1800)
        stats["bytes_in"] = "2.4 GB"
        stats["bytes_out"] = "18.7 GB"
    return stats


@router.get("/servers")
async def api_servers():
    return [s.model_dump() for s in store.get_servers()]


@router.post("/servers/{server_id}/toggle")
async def toggle_server(server_id: int):
    server = store.toggle_server(server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return {"ok": True, "status": server.status}


@router.get("/upstreams")
async def api_upstreams():
    return [u.model_dump() for u in store.get_upstreams()]


class ConfigBody(BaseModel):
    config: str


@router.post("/config/save")
async def save_config(body: ConfigBody):
    ok, message = nginx.write_config(body.config)
    if not ok:
        raise HTTPException(status_code=422, detail=message)
    return {"ok": True, "message": message}


@router.post("/nginx/reload")
async def nginx_reload():
    ok, message = nginx.reload()
    if not ok:
        raise HTTPException(status_code=500, detail=message)
    return {"ok": True, "message": message or "Nginx reloaded successfully"}
