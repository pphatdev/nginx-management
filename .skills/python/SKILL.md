---
name: python-nginx-deployment
summary: Deploy, operate, and troubleshoot a Python (FastAPI/Flask) app behind Nginx using either systemd+Gunicorn or Docker Compose on Ubuntu.
---

# Python + Nginx Deployment Skill

Use this skill when the user asks to:

- Deploy a Python (FastAPI or Flask) app behind Nginx
- Use Docker or non-Docker deployment paths
- Configure HTTPS and reverse proxy behavior
- Troubleshoot Uvicorn/Gunicorn runtime and proxy issues

## Routing Logic

1. If the user asks for Docker, containers, images, compose, or CI image workflows: use `deployment-docker.md`.
2. If the user asks for VM/service style process management: use `deployment.md`.
3. If unspecified: briefly offer both and continue with the path matching their environment.

## Files in This Skill

- Non-Docker: `deployment.md`
- Docker: `deployment-docker.md`

## Output Requirements

- Give copy-paste-ready commands and config blocks.
- State assumptions clearly (domain, ports, ASGI/WSGI mode, env vars).
- Keep app bound to localhost (127.0.0.1) when Nginx is the public entry point.
- Include verification and rollback steps.
- Use Gunicorn with Uvicorn workers for production (FastAPI/ASGI apps).

## Minimum Verification

```bash
docker compose ps
docker compose logs --tail=100 app
sudo nginx -t
sudo systemctl reload nginx
curl -I http://127.0.0.1:9991
```
