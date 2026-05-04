from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="www/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "active_page": "dashboard",
        "title": "Dashboard | Nginx Management"
    })

@router.get("/servers", response_class=HTMLResponse)
async def servers(request: Request):
    return templates.TemplateResponse("servers.html", {
        "request": request,
        "active_page": "servers",
        "title": "Virtual Hosts | Nginx Management"
    })

@router.get("/upstreams", response_class=HTMLResponse)
async def upstreams(request: Request):
    return templates.TemplateResponse("upstreams.html", {
        "request": request,
        "active_page": "upstreams",
        "title": "Upstreams | Nginx Management"
    })

@router.get("/config", response_class=HTMLResponse)
async def config_editor(request: Request):
    return templates.TemplateResponse("config.html", {
        "request": request,
        "active_page": "config",
        "title": "Config Editor | Nginx Management"
    })

@router.get("/monitoring", response_class=HTMLResponse)
async def monitoring(request: Request):
    return templates.TemplateResponse("monitoring.html", {
        "request": request,
        "active_page": "monitoring",
        "title": "Monitoring | NGINX CONTROL"
    })

@router.get("/projects", response_class=HTMLResponse)
async def projects(request: Request):
    return templates.TemplateResponse("projects.html", {
        "request": request,
        "active_page": "projects",
        "title": "Project Management | NGINX CONTROL"
    })
