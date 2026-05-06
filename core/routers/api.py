from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import subprocess
import os
import asyncio
from datetime import datetime
import json

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
    sup_path = "/etc/supervisor/conf.d"
    projects = []
    
    if not os.path.exists(base_path):
        return []

    # Get Supervisor status
    supervisor_status = {}
    try:
        process = await asyncio.create_subprocess_exec(
            "sudo", "/usr/bin/supervisorctl", "status",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()
        if process.returncode == 0:
            lines = stdout.decode().splitlines()
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[0]
                        status = parts[1]
                        supervisor_status[name] = status == 'RUNNING'
    except Exception as e:
        print(f"Supervisor status check failed: {e}")

    try:
        for item in os.listdir(base_path):
            full_path = os.path.join(base_path, item)
            if os.path.isdir(full_path) and not item.startswith('.'):
                stats = os.stat(full_path)
                
                domain_list = []
                port_list = []
                
                # 1. Try to get info from Nginx config
                nginx_conf = os.path.join(nginx_path, f"{item}.conf")
                if os.path.exists(nginx_conf):
                    try:
                        with open(nginx_conf, 'r') as f:
                            content = f.read()
                            import re
                            # Get domains
                            domains = re.findall(r'server_name\s+([^;]+);', content)
                            for d in domains:
                                domain_list.extend([x.strip() for x in d.split() if x.strip()])
                            
                            # Get proxy_pass ports
                            ports = re.findall(r'proxy_pass\s+http://127.0.0.1:(\d+);', content)
                            port_list.extend(ports)
                    except: pass

                # 2. Try to get info from Supervisor config
                sup_conf = os.path.join(sup_path, f"{item}.conf")
                if os.path.exists(sup_conf):
                    try:
                        with open(sup_conf, 'r') as f:
                            content = f.read()
                            import re
                            # Get port from environment
                            ports = re.findall(r'PORT="(\d+)"', content)
                            port_list.extend(ports)
                    except: pass
                
                domain_name = ", ".join(set(domain_list)) if domain_list else "None"
                port_name = ", ".join(set(port_list)) if port_list else "None"
                
                # Active if either Nginx config exists OR Supervisor process is online
                is_active = (len(domain_list) > 0 or len(port_list) > 0) or supervisor_status.get(item, False)
                
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

class GitImport(BaseModel):
    url: str
    name: str

@router.post("/projects/import")
async def import_git_project(data: GitImport):
    base_path = "/var/www"
    target_path = os.path.join(base_path, data.name)
    
    if os.path.exists(target_path):
        raise HTTPException(status_code=400, detail="Project directory already exists")
        
    try:
        # Using non-blocking asyncio subprocess
        process = await asyncio.create_subprocess_exec(
            "git", "clone", data.url, target_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode().strip() or "Unknown Git error"
            raise HTTPException(status_code=500, detail=f"Git clone failed: {error_msg}")
            
        return {"message": "Project imported successfully", "path": target_path}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/projects/{name}")
async def delete_project(name: str):
    base_path = "/var/www"
    target_path = os.path.join(base_path, name)
    
    # Security check: Ensure name doesn't contain path traversal
    if ".." in name or "/" in name:
        raise HTTPException(status_code=400, detail="Invalid project name")
        
    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail="Project not found")
        
    try:
        # 1. Cleanup Supervisor (if exists)
        cleanup_sup = f"sudo /usr/bin/rm -f /etc/supervisor/conf.d/{name}.conf && sudo /usr/bin/supervisorctl update"
        process_sup = await asyncio.create_subprocess_shell(cleanup_sup)
        await process_sup.wait()
        
        # 2. Cleanup Nginx Configs
        conf_path = f"/etc/nginx/sites-available/{name}.conf"
        enabled_path = f"/etc/nginx/sites-enabled/{name}.conf"
        
        cleanup_cmd = f"sudo /usr/bin/rm -f {conf_path} {enabled_path} && sudo /usr/sbin/nginx -s reload"
        process_nginx = await asyncio.create_subprocess_shell(cleanup_cmd)
        await process_nginx.wait()
        
        # 3. Cleanup Project Directory
        process_dir = await asyncio.create_subprocess_exec(
            "sudo", "/usr/bin/rm", "-rf", target_path
        )
        await process_dir.wait()
        
        if process_dir.returncode != 0:
            raise HTTPException(status_code=500, detail="Failed to delete project directory")
            
        return {"message": f"Project {name} and its configurations deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/{name}/start")
async def start_project(name: str):
    target_path = f"/var/www/{name}"
    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Supervisor handles starting via reread/update if config exists
    # or start command if already known
    cmd = f"sudo /usr/bin/supervisorctl start {name}"
    process = await asyncio.create_subprocess_shell(cmd)
    await process.wait()
    
    if process.returncode == 0:
        return {"message": f"Project {name} started"}
    else:
        raise HTTPException(status_code=500, detail="Failed to start project")

@router.post("/projects/{name}/stop")
async def stop_project(name: str):
    process = await asyncio.create_subprocess_exec("sudo", "/usr/bin/supervisorctl", "stop", name)
    await process.wait()
    return {"message": f"Project {name} stopped"}

@router.post("/projects/{name}/restart")
async def restart_project(name: str):
    process = await asyncio.create_subprocess_exec("sudo", "/usr/bin/supervisorctl", "restart", name)
    await process.wait()
    if process.returncode == 0:
        return {"message": f"Project {name} restarted"}
    else:
        # Try start if restart fails (might not be running)
        return await start_project(name)

@router.get("/check-port/{port}")
async def check_port(port: int):
    import psutil
    # 1. Check active processes
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            return {"in_use": True, "reason": "Process active on port"}
            
    # 2. Check Nginx configs
    sites_enabled = "/etc/nginx/sites-enabled"
    if os.path.exists(sites_enabled):
        for f in os.listdir(sites_enabled):
            try:
                with open(os.path.join(sites_enabled, f), 'r') as cf:
                    if f":{port}" in cf.read():
                        return {"in_use": True, "reason": f"Project {f} uses this port"}
            except: pass
            
    return {"in_use": False}
