from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import subprocess
import os
from datetime import datetime

router = APIRouter()

import psutil
import time

@router.get("/stats")
async def get_stats():
    # Real-time system stats
    cpu_usage = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Network stats (delta)
    net_1 = psutil.net_io_counters()
    time.sleep(0.1)
    net_2 = psutil.net_io_counters()
    
    net_in = (net_2.bytes_recv - net_1.bytes_recv) * 8 / 1024 / 1024 / 0.1 # Mbps
    net_out = (net_2.bytes_sent - net_1.bytes_sent) * 8 / 1024 / 1024 / 0.1 # Mbps

    # Uptime
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    
    # Nginx connections (Mocked or read from stub_status if enabled)
    # For now, we'll keep a semi-realistic mock for Nginx specific stats
    # unless we want to parse stub_status
    
    return {
        "cpu_usage": cpu_usage,
        "memory_usage": memory.percent,
        "memory_used": memory.used / (1024**3), # GB
        "memory_total": memory.total / (1024**3), # GB
        "disk_usage": disk.percent,
        "network_in": round(net_in, 2),
        "network_out": round(net_out, 2),
        "uptime": str(uptime).split('.')[0],
        "status": "Healthy"
    }



@router.post("/nginx/reload")
async def reload_nginx():
    # Placeholder for reload logic
    return {"message": "Nginx reloaded successfully"}


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

@router.get("/deployments")
async def get_deployments():
    base_path = "/var/www"
    deployments = []
    
    if not os.path.exists(base_path):
        return []

    try:
        items = []
        for item in os.listdir(base_path):
            full_path = os.path.join(base_path, item)
            if os.path.isdir(full_path):
                mtime = os.path.getmtime(full_path)
                items.append({
                    "id": f"#{item[:7].replace('-', '')}",
                    "name": item,
                    "timestamp": datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    "raw_time": mtime,
                    "status": "Success" if (datetime.now().timestamp() - mtime) > 60 else "Deploying"
                })
        
        items.sort(key=lambda x: x['raw_time'], reverse=True)
        deployments = items[:3]
    except Exception:
        pass

    return deployments
