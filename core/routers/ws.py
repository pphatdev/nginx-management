from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import psutil
from datetime import datetime
import json

router = APIRouter()

@router.websocket("/ws/stats")
async def stats_streaming(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Initial call to set the baseline
            psutil.cpu_percent(interval=None)
            net_1 = psutil.net_io_counters()
            
            await asyncio.sleep(0.5) 
            
            # Second call to get the average over the sleep period
            cpu_usage = psutil.cpu_percent(interval=None)
            net_2 = psutil.net_io_counters()
            memory = psutil.virtual_memory()
            
            net_in = (net_2.bytes_recv - net_1.bytes_recv) * 8 / 1024 / 1024 / 0.5
            net_out = (net_2.bytes_sent - net_1.bytes_sent) * 8 / 1024 / 1024 / 0.5
            
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time

            data = {
                "cpu_usage": cpu_usage,
                "memory_usage": memory.percent,
                "memory_used": memory.used / (1024**3),
                "network_in": round(net_in, 2),
                "network_out": round(net_out, 2),
                "uptime": str(uptime).split('.')[0],
                "timestamp": datetime.now().strftime('%H:%M:%S')
            }
            
            await websocket.send_text(json.dumps(data))
    except WebSocketDisconnect:
        print("Client disconnected from stats stream")
    except Exception as e:
        print(f"Error in stats stream: {e}")

@router.websocket("/ws/import")
async def import_streaming(websocket: WebSocket):
    await websocket.accept()
    try:
        # Receive config (url and name)
        config_raw = await websocket.receive_text()
        config = json.loads(config_raw)
        
        url = config.get("url")
        name = config.get("name")
        domain = config.get("domain", "")
        env_content = config.get("env_content", "")
        start_cmd = config.get("start_cmd", "")
        port = config.get("port") # Use None to trigger auto-discovery
        auto_deploy = config.get("auto_deploy", False)
        target_path = f"/var/www/{name}"
        
        import os
        import psutil
        
        # Unique Port Validation & Auto-Discovery
        def find_next_available_port():
            forbidden_ports = {80, 443, 8080, 8000, 3306, 5432, 27017, 6379} # Common/Default ports to avoid
            used_ports = set()
            
            # 1. Check Nginx configs (listen and proxy_pass)
            sites_enabled = "/etc/nginx/sites-enabled"
            if os.path.exists(sites_enabled):
                for f in os.listdir(sites_enabled):
                    try:
                        with open(os.path.join(sites_enabled, f), 'r') as cf:
                            content = cf.read()
                            # Find all numbers that look like ports
                            import re
                            found = re.findall(r'[:\s](\d{2,5})[;\s]', content)
                            for p in found:
                                used_ports.add(int(p))
                    except: pass
            
            # 2. Check active system listeners
            try:
                for conn in psutil.net_connections(kind='inet'):
                    if conn.status == 'LISTEN':
                        used_ports.add(conn.laddr.port)
            except: pass
            
            # 3. Find next available starting from 3000
            candidate = 3000
            while candidate in used_ports or candidate in forbidden_ports:
                candidate += 1
            return candidate

        if not port or port == "":
            port = str(find_next_available_port())
            await websocket.send_text(json.dumps({"type": "log", "message": f"Auto-assigned collision-free port: {port}"}))

        def is_port_in_use(p):
            # 1. Check active processes
            for conn in psutil.net_connections():
                if conn.laddr.port == int(p):
                    return True
            # 2. Check Nginx configs for proxy_pass to this port
            sites_enabled = "/etc/nginx/sites-enabled"
            if os.path.exists(sites_enabled):
                for f in os.listdir(sites_enabled):
                    try:
                        with open(os.path.join(sites_enabled, f), 'r') as cf:
                            if f":{p}" in cf.read():
                                return True
                    except: pass
            return False

        if auto_deploy and is_port_in_use(port):
            await websocket.send_text(json.dumps({"type": "error", "message": f"Conflict: Port {port} is already in use by another service or project."}))
            await websocket.close()
            return

        if os.path.exists(target_path):
            await websocket.send_text(json.dumps({"type": "error", "message": "Directory already exists"}))
            await websocket.close()
            return

        # Start git clone with progress
        process = await asyncio.create_subprocess_exec(
            "git", "clone", "--progress", url, target_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        async def stream_output(stream, msg_type):
            while True:
                line = await stream.read(1024)
                if not line:
                    break
                text = line.decode(errors='replace')
                await websocket.send_text(json.dumps({"type": msg_type, "message": text}))

        await asyncio.gather(
            stream_output(process.stdout, "log"),
            stream_output(process.stderr, "progress")
        )
        
        await process.wait()
        
        async def execute_command(cmd, cwd=None, msg_type="log"):
            p = await asyncio.create_subprocess_shell(
                cmd, cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            async def read_stream(stream):
                while True:
                    line = await stream.read(1024)
                    if not line: break
                    await websocket.send_text(json.dumps({"type": msg_type, "message": line.decode(errors='replace')}))
            
            await asyncio.gather(read_stream(p.stdout), read_stream(p.stderr))
            await p.wait()
            return p.returncode

        if process.returncode == 0:
            await websocket.send_text(json.dumps({"type": "log", "message": "Analyzing project structure..."}))
            
            # Framework/Language detection
            framework = "static"
            package_json_path = os.path.join(target_path, "package.json")
            has_package_json = os.path.exists(package_json_path)
            
            package_data = {}
            if has_package_json:
                try:
                    with open(package_json_path, 'r') as f:
                        package_data = json.load(f)
                except: pass

            def has_dep(name):
                return name in package_data.get("dependencies", {}) or name in package_data.get("devDependencies", {})

            if os.path.exists(os.path.join(target_path, "next.config.js")) or \
               os.path.exists(os.path.join(target_path, "next.config.mjs")) or \
               os.path.exists(os.path.join(target_path, "next.config.ts")) or \
               has_dep("next"):
                framework = "next"
            elif os.path.exists(os.path.join(target_path, "nuxt.config.js")) or \
                 os.path.exists(os.path.join(target_path, "nuxt.config.ts")) or \
                 has_dep("nuxt"):
                framework = "nuxt"
            elif has_package_json:
                framework = "node"
            elif os.path.exists(os.path.join(target_path, "requirements.txt")):
                framework = "python"
            
            await websocket.send_text(json.dumps({"type": "log", "message": f"Detected framework: {framework.upper()}"}))

            # 1. .env Provisioning (Flow: Has .env? -> Update Port. No -> Create .env with free port)
            import re
            env_file_path = os.path.join(target_path, ".env")
            current_env_content = ""
            
            if os.path.exists(env_file_path):
                with open(env_file_path, 'r') as f:
                    current_env_content = f.read()
                await websocket.send_text(json.dumps({"type": "log", "message": "Existing .env detected, updating PORT..."}))
            elif env_content:
                current_env_content = env_content
                await websocket.send_text(json.dumps({"type": "log", "message": "Using provided environment variables..."}))
            else:
                await websocket.send_text(json.dumps({"type": "log", "message": "Creating new .env file..."}))

            if re.search(r'^PORT=', current_env_content, re.MULTILINE):
                current_env_content = re.sub(r'^PORT=.*', f'PORT={port}', current_env_content, flags=re.MULTILINE)
            else:
                if current_env_content and not current_env_content.endswith('\n'):
                    current_env_content += '\n'
                current_env_content += f'PORT={port}\n'
            
            try:
                with open(env_file_path, 'w') as f:
                    f.write(current_env_content)
            except Exception as e:
                await websocket.send_text(json.dumps({"type": "error", "message": f"Failed to write .env: {str(e)}"}))

            if auto_deploy:
                # 2. Dependency Installation
                if framework in ["next", "nuxt", "node"]:
                    await websocket.send_text(json.dumps({"type": "log", "message": "Installing Node.js dependencies (npm install)..."}))
                    if await execute_command("npm install", cwd=target_path) != 0:
                        await websocket.send_text(json.dumps({"type": "error", "message": "npm install failed"}))
                        return
                elif framework == "python":
                    await websocket.send_text(json.dumps({"type": "log", "message": "Creating virtualenv and installing requirements..."}))
                    py_cmd = "python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt"
                    if await execute_command(py_cmd, cwd=target_path) != 0:
                        await websocket.send_text(json.dumps({"type": "error", "message": "Python dependency installation failed"}))
                        return

                # 3. Build Step
                if framework in ["next", "nuxt"]:
                    await websocket.send_text(json.dumps({"type": "log", "message": f"Building {framework.upper()} application..."}))
                    if await execute_command("npm run build", cwd=target_path) != 0:
                        await websocket.send_text(json.dumps({"type": "error", "message": "Build failed"}))
                        return

                # 3. Process Management (Supervisor)
                if framework in ["next", "nuxt", "node"] or start_cmd:
                    await websocket.send_text(json.dumps({"type": "log", "message": "Provisioning Supervisor process manager..."}))
                    # Smart Start Command Generation
                    if not start_cmd:
                        if framework == "next":
                            actual_start_cmd = "npm start -- -p {{port}}"
                        elif framework == "nuxt":
                            actual_start_cmd = "npm start -- --port {{port}}"
                        else:
                            actual_start_cmd = "npm start"
                    else:
                        actual_start_cmd = start_cmd
                    
                    actual_start_cmd = actual_start_cmd.replace("{{port}}", port)
                    
                    # Load Supervisor template
                    sup_template_path = "/var/www/nginx-management/configs/supervisor/project.conf.template"
                    import getpass
                    current_user = getpass.getuser()
                    if os.path.exists(sup_template_path):
                        with open(sup_template_path, 'r') as f:
                            sup_config = f.read().replace("{{name}}", name)\
                                               .replace("{{start_command}}", actual_start_cmd)\
                                               .replace("{{project_path}}", target_path)\
                                               .replace("{{user}}", current_user)\
                                               .replace("{{port}}", port)\
                                               .replace("{{environment_vars}}", ',NODE_ENV="production"')
                        
                        temp_sup_conf = f"/tmp/{name}.sup.conf"
                        with open(temp_sup_conf, 'w') as f:
                            f.write(sup_config)
                        
                        deploy_sup_cmd = f"sudo /usr/bin/cp {temp_sup_conf} /etc/supervisor/conf.d/{name}.conf && " \
                                         f"sudo /usr/bin/supervisorctl reread && " \
                                         f"sudo /usr/bin/supervisorctl update"
                        
                        if await execute_command(deploy_sup_cmd) != 0:
                            await websocket.send_text(json.dumps({"type": "error", "message": "Supervisor configuration failed"}))
                            return
                
                elif framework == "python":
                    await websocket.send_text(json.dumps({"type": "log", "message": "Provisioning Systemd service..."}))
                    # Systemd logic (simplified for now)
                    pass

                # 4. Nginx Configuration
                await websocket.send_text(json.dumps({"type": "log", "message": "Provisioning Nginx virtual host..."}))
                nginx_template = f"/var/www/nginx-management/configs/nginx/{framework}.config"
                if not os.path.exists(nginx_template):
                    nginx_template = "/var/www/nginx-management/configs/nginx/node.config" # fallback

                if os.path.exists(nginx_template):
                    with open(nginx_template, 'r') as f:
                        template = f.read()
                    
                    config_content = template.replace("{{domain}}", domain if domain else f"{name}.local")\
                                           .replace("{{port}}", port)\
                                           .replace("{{project_path}}", target_path)
                    
                    temp_conf = f"/tmp/{name}.nginx.conf"
                    with open(temp_conf, 'w') as f:
                        f.write(config_content)
                    
                    deploy_cmd = f"sudo /usr/bin/cp /tmp/{name}.nginx.conf /etc/nginx/sites-available/{name}.conf && " \
                                 f"sudo /usr/bin/ln -sf /etc/nginx/sites-available/{name}.conf /etc/nginx/sites-enabled/ && " \
                                 f"sudo /usr/sbin/nginx -t && " \
                                 f"sudo /usr/sbin/nginx -s reload"
                    
                    if await execute_command(deploy_cmd) == 0:
                        await websocket.send_text(json.dumps({"type": "log", "message": "Nginx virtual host active"}))
                        
                        # 4b. Auto-config /etc/hosts for local resolution
                        final_domain = domain if domain else f"{name}.local"
                        await websocket.send_text(json.dumps({"type": "log", "message": f"Registering {final_domain} in /etc/hosts..."}))
                        hosts_cmd = f"grep -q ' {final_domain}' /etc/hosts || echo '127.0.0.1 {final_domain}' | sudo /usr/bin/tee -a /etc/hosts"
                        await execute_command(hosts_cmd)
                        
                        # 5. SSL Generation (only if domain is provided)
                        if domain:
                            await websocket.send_text(json.dumps({"type": "log", "message": "Provisioning Let's Encrypt SSL..."}))
                            ssl_cmd = f"sudo /usr/bin/certbot --nginx -d {domain} --non-interactive --agree-tos --register-unsafely-without-email --redirect"
                            if await execute_command(ssl_cmd) == 0:
                                # Step 5b: Apply custom SSL template if available
                                ssl_template = f"/var/www/nginx-management/configs/nginx/{framework}.ssl.config"
                                if not os.path.exists(ssl_template):
                                    ssl_template = "/var/www/nginx-management/configs/nginx/next.ssl.config" if framework == "next" else None
                                
                                if ssl_template and os.path.exists(ssl_template):
                                    await websocket.send_text(json.dumps({"type": "log", "message": f"Applying custom SSL optimizations ({os.path.basename(ssl_template)})..."}))
                                    with open(ssl_template, 'r') as f:
                                        template = f.read()
                                    config_content = template.replace("{{domain}}", domain).replace("{{port}}", port).replace("{{project_path}}", target_path)
                                    with open(f"/tmp/{name}.nginx.ssl.conf", 'w') as f:
                                        f.write(config_content)
                                    
                                    final_deploy_cmd = f"sudo /usr/bin/cp /tmp/{name}.nginx.ssl.conf /etc/nginx/sites-available/{name}.conf && " \
                                                      f"sudo /usr/sbin/nginx -t && " \
                                                      f"sudo /usr/sbin/nginx -s reload"
                                    if await execute_command(final_deploy_cmd) != 0:
                                        await websocket.send_text(json.dumps({"type": "error", "message": "Applying custom SSL template failed, using default certbot config"}))
                        
                        await websocket.send_text(json.dumps({"type": "success", "message": f"Full Stack Deployed Successfully!"}))
                    else:
                        await websocket.send_text(json.dumps({"type": "error", "message": "Nginx configuration failed"}))
                else:
                    await websocket.send_text(json.dumps({"type": "success", "message": "Imported and Services Started (Nginx template missing)"}))
            else:
                await websocket.send_text(json.dumps({"type": "success", "message": "Import completed successfully"}))
        else:
            await websocket.send_text(json.dumps({"type": "error", "message": f"Git Clone failed with exit code {process.returncode}"}))
            
    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
    finally:
        await websocket.close()
