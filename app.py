from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import uvicorn
import datetime

app = FastAPI(title="Nginx Management UI", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ──────────────────────────────────────────────
# In-memory mock data
# ──────────────────────────────────────────────

SERVERS = [
    {"id": 1, "name": "api.example.com",   "port": 443, "ssl": True,  "status": "active",   "upstream": "api_pool"},
    {"id": 2, "name": "www.example.com",   "port": 80,  "ssl": False, "status": "active",   "upstream": "web_pool"},
    {"id": 3, "name": "admin.example.com", "port": 443, "ssl": True,  "status": "inactive", "upstream": "admin_pool"},
    {"id": 4, "name": "static.example.com","port": 80,  "ssl": False, "status": "active",   "upstream": "static_pool"},
]

UPSTREAMS = [
    {
        "id": 1,
        "name": "api_pool",
        "method": "round_robin",
        "backends": [
            {"address": "10.0.0.1:8001", "weight": 1, "status": "up"},
            {"address": "10.0.0.2:8001", "weight": 1, "status": "up"},
            {"address": "10.0.0.3:8001", "weight": 1, "status": "down"},
        ],
    },
    {
        "id": 2,
        "name": "web_pool",
        "method": "least_conn",
        "backends": [
            {"address": "10.0.1.1:3000", "weight": 2, "status": "up"},
            {"address": "10.0.1.2:3000", "weight": 1, "status": "up"},
        ],
    },
    {
        "id": 3,
        "name": "admin_pool",
        "method": "ip_hash",
        "backends": [
            {"address": "10.0.2.1:9000", "weight": 1, "status": "up"},
        ],
    },
    {
        "id": 4,
        "name": "static_pool",
        "method": "round_robin",
        "backends": [
            {"address": "10.0.3.1:8080", "weight": 1, "status": "up"},
            {"address": "10.0.3.2:8080", "weight": 1, "status": "up"},
        ],
    },
]

NGINX_CONFIG = """\
user  nginx;
worker_processes  auto;

error_log  /var/log/nginx/error.log notice;
pid        /var/run/nginx.pid;

events {
    worker_connections  1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    keepalive_timeout  65;
    gzip  on;

    include /etc/nginx/conf.d/*.conf;
}
"""

STATS = {
    "nginx_version": "1.25.3",
    "uptime": "14d 6h 42m",
    "active_connections": 248,
    "requests_per_sec": 1340,
    "bytes_in": "2.4 GB",
    "bytes_out": "18.7 GB",
    "last_reload": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
}

# ──────────────────────────────────────────────
# Page routes
# ──────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    total_backends = sum(len(u["backends"]) for u in UPSTREAMS)
    up_backends    = sum(1 for u in UPSTREAMS for b in u["backends"] if b["status"] == "up")
    active_servers = sum(1 for s in SERVERS if s["status"] == "active")
    return templates.TemplateResponse("index.html", {
        "request": request,
        "page": "dashboard",
        "stats": STATS,
        "active_servers": active_servers,
        "total_servers": len(SERVERS),
        "up_backends": up_backends,
        "total_backends": total_backends,
        "upstreams": UPSTREAMS,
    })


@app.get("/servers", response_class=HTMLResponse)
async def servers_page(request: Request):
    return templates.TemplateResponse("servers.html", {
        "request": request,
        "page": "servers",
        "servers": SERVERS,
    })


@app.get("/upstreams", response_class=HTMLResponse)
async def upstreams_page(request: Request):
    return templates.TemplateResponse("upstreams.html", {
        "request": request,
        "page": "upstreams",
        "upstreams": UPSTREAMS,
    })


@app.get("/config", response_class=HTMLResponse)
async def config_page(request: Request):
    return templates.TemplateResponse("config.html", {
        "request": request,
        "page": "config",
        "config": NGINX_CONFIG,
    })


# ──────────────────────────────────────────────
# API routes (JSON)
# ──────────────────────────────────────────────

@app.get("/api/stats")
async def api_stats():
    import random
    STATS["active_connections"] = random.randint(180, 320)
    STATS["requests_per_sec"]   = random.randint(900, 1800)
    return JSONResponse(STATS)


@app.get("/api/servers")
async def api_servers():
    return JSONResponse(SERVERS)


@app.post("/api/servers/{server_id}/toggle")
async def toggle_server(server_id: int):
    for s in SERVERS:
        if s["id"] == server_id:
            s["status"] = "inactive" if s["status"] == "active" else "active"
            return {"ok": True, "status": s["status"]}
    return JSONResponse({"ok": False, "error": "Not found"}, status_code=404)


@app.get("/api/upstreams")
async def api_upstreams():
    return JSONResponse(UPSTREAMS)


@app.post("/api/config/save")
async def save_config(request: Request):
    global NGINX_CONFIG
    body = await request.json()
    NGINX_CONFIG = body.get("config", NGINX_CONFIG)
    return {"ok": True, "message": "Configuration saved (dry-run)"}


@app.post("/api/nginx/reload")
async def nginx_reload():
    STATS["last_reload"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"ok": True, "message": "Nginx reload signal sent"}


# ──────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
