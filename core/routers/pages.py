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

@router.get("/import", response_class=HTMLResponse)
async def import_project(request: Request):
    return templates.TemplateResponse("import.html", {
        "request": request,
        "active_page": "import",
        "title": "Import Project | Nginx Management"
    })
