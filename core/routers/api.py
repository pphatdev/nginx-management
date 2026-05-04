from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import subprocess
import os
from datetime import datetime

router = APIRouter()

@router.get("/stats")
async def get_stats():
    # Mock stats for now
    return {
        "active_connections": 124,
        "requests_per_second": 45,
        "cpu_usage": 12.5,
        "memory_usage": 45.2,
        "uptime": "15 days, 4 hours",
        "status": "Healthy"
    }

@router.get("/servers")
async def get_servers():
    # Placeholder for virtual hosts
    return [
        {"id": 1, "name": "example.com", "port": 80, "active": True},
        {"id": 2, "name": "api.example.com", "port": 443, "active": True},
        {"id": 3, "name": "dev.example.com", "port": 80, "active": False},
    ]

@router.get("/upstreams")
async def get_upstreams():
    # Placeholder for upstreams
    return [
        {"name": "backend_pool", "servers": ["10.0.0.1:8000", "10.0.0.2:8000"], "status": "UP"},
        {"name": "api_pool", "servers": ["10.0.0.3:9000"], "status": "UP"},
    ]

@router.post("/nginx/reload")
async def reload_nginx():
    # Placeholder for reload logic
    return {"message": "Nginx reloaded successfully"}

@router.get("/config")
async def get_config():
    # In a real app, this would read /etc/nginx/nginx.conf
    # For now, we'll return a sample or read from the project root if available
    try:
        # Try to find a local nginx.conf or return a default
        return {"content": "user www-data;\nworker_processes auto;\npid /run/nginx.pid;\n\nevents {\n    worker_connections 768;\n}\n\nhttp {\n    sendfile on;\n    tcp_nopush on;\n    types_hash_max_size 2048;\n    include /etc/nginx/mime.types;\n    default_type application/octet-stream;\n\n    server {\n        listen 80;\n        server_name localhost;\n        location / {\n            root /var/www/html;\n        }\n    }\n}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config/save")
async def save_config(config: Dict[str, str]):
    # Placeholder for saving logic
    return {"message": "Configuration saved successfully"}

@router.get("/projects")
async def get_projects():
    base_path = "/var/www"
    nginx_path = "/etc/nginx/sites-enabled"
    projects = []
    
    if not os.path.exists(base_path):
        return []

    # Map project paths to domains/status from Nginx configs
    active_paths = {} # path -> {"domains": [], "ports": []}
    if os.path.exists(nginx_path):
        try:
            for conf in os.listdir(nginx_path):
                conf_path = os.path.join(nginx_path, conf)
                if os.path.isfile(conf_path) or os.path.islink(conf_path):
                    with open(conf_path, 'r') as f:
                        content = f.read()
                        import re
                        # Extract all paths starting with /var/www
                        paths_found = re.findall(r'/var/www/[a-zA-Z0-9\-_./]+', content)
                        domains = re.findall(r'server_name\s+([^;]+);', content)
                        ports = re.findall(r'listen\s+(\d+);', content)
                        
                        for p in paths_found:
                            # Normalize path to find the base project dir
                            p_parts = p.split('/')
                            if len(p_parts) >= 4: # /var/www/projectname
                                base_project_path = "/".join(p_parts[:4])
                                if base_project_path not in active_paths:
                                    active_paths[base_project_path] = {"domains": [], "ports": []}
                                active_paths[base_project_path]["domains"].extend([d.strip() for d in domains])
                                active_paths[base_project_path]["ports"].extend([p_strip.strip() for p_strip in ports])
        except Exception:
            pass 

    try:
        for item in os.listdir(base_path):
            full_path = os.path.join(base_path, item)
            if os.path.isdir(full_path):
                stats = os.stat(full_path)
                
                config_info = active_paths.get(full_path)
                if not config_info:
                    config_info = active_paths.get(os.path.join(full_path, "public"))
                if not config_info:
                    config_info = active_paths.get(os.path.join(full_path, "dist"))
                
                domain_list = config_info["domains"] if config_info else []
                port_list = config_info["ports"] if config_info else []
                
                is_active = len(domain_list) > 0 or len(port_list) > 0
                domain_name = ", ".join(domain_list) if domain_list else "None"
                port_name = ", ".join(set(port_list)) if port_list else "None"
                
                # Mock 'Deploying' state if modified in the last 30 seconds
                is_deploying = (datetime.now().timestamp() - stats.st_mtime) < 30

                # Check for common indicators
                project_type = "Generic"
                if os.path.exists(os.path.join(full_path, "package.json")):
                    project_type = "Node.js"
                elif os.path.exists(os.path.join(full_path, "requirements.txt")) or os.path.exists(os.path.join(full_path, "main.py")):
                    project_type = "Python"
                elif os.path.exists(os.path.join(full_path, "index.html")):
                    project_type = "Static"

                projects.append({
                    "name": item,
                    "path": full_path,
                    "type": project_type,
                    "domain": domain_name,
                    "port": port_name,
                    "active": is_active,
                    "deploying": is_deploying,
                    "last_modified": datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M'),
                    "size": "N/A"
                })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return projects
