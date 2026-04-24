from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.services import nginx, store

BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "client" / "templates"))

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    servers = store.get_servers()
    upstreams = store.get_upstreams()
    total_backends = sum(len(u.backends) for u in upstreams)
    up_backends = sum(1 for u in upstreams for b in u.backends if b.status == "up")
    active_servers = sum(1 for s in servers if s.status == "active")
    return templates.TemplateResponse("index.html", {
        "request": request,
        "page": "dashboard",
        "stats": nginx.get_stats(),
        "active_servers": active_servers,
        "total_servers": len(servers),
        "up_backends": up_backends,
        "total_backends": total_backends,
        "upstreams": [u.model_dump() for u in upstreams],
    })


@router.get("/servers", response_class=HTMLResponse)
async def servers_page(request: Request):
    return templates.TemplateResponse("servers.html", {
        "request": request,
        "page": "servers",
        "servers": [s.model_dump() for s in store.get_servers()],
    })


@router.get("/upstreams", response_class=HTMLResponse)
async def upstreams_page(request: Request):
    return templates.TemplateResponse("upstreams.html", {
        "request": request,
        "page": "upstreams",
        "upstreams": [u.model_dump() for u in store.get_upstreams()],
    })


@router.get("/config", response_class=HTMLResponse)
async def config_page(request: Request):
    return templates.TemplateResponse("config.html", {
        "request": request,
        "page": "config",
        "config": nginx.read_config(),
    })


@router.get("/deployments", response_class=HTMLResponse)
async def deployments_page(request: Request):
    return templates.TemplateResponse("deployments.html", {
        "request": request,
        "page": "deployments",
    })


@router.get("/dns", response_class=HTMLResponse)
async def dns_page(request: Request):
    return templates.TemplateResponse("dns.html", {
        "request": request,
        "page": "dns",
    })


@router.get("/monitoring", response_class=HTMLResponse)
async def monitoring_page(request: Request):
    return templates.TemplateResponse("monitoring.html", {
        "request": request,
        "page": "monitoring",
    })


@router.get("/loadbalancing", response_class=HTMLResponse)
async def loadbalancing_page(request: Request):
    return templates.TemplateResponse("loadbalancing.html", {
        "request": request,
        "page": "loadbalancing",
    })

