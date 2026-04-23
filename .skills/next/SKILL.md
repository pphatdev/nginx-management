---
name: nextjs-nginx-deployment
summary: Deploy, operate, and troubleshoot Next.js behind Nginx using either systemd or Docker/Compose on Ubuntu.
---

# Next.js + Nginx Deployment Skill

Use this skill when the user asks to:

- Deploy a Next.js app behind Nginx
- Choose between non-container and Docker-based deployments
- Add HTTPS, reverse proxy, and production hardening
- Troubleshoot startup, proxy, TLS, or port issues

## Routing Logic

1. If user asks for Docker, containerization, image build, compose, or CI deploys: use `deployment-docker.md`.
2. If user asks for VM-style process management with systemd: use `deployment.md`.
3. If user does not specify: present both options briefly and continue with the safer/default path for their environment.

## Files in This Skill

- Non-Docker path: `deployment.md`
- Docker path: `deployment-docker.md`

## Output Requirements

- Provide copy-paste-ready commands and config blocks.
- State assumptions (domain, app path, ports, env vars).
- Include validation steps after each major stage.
- Include rollback and troubleshooting notes.
- Keep Nginx as the public entrypoint and avoid exposing app port publicly unless explicitly requested.

## Minimum Verification

Always include these checks unless user asks not to:

```bash
docker compose ps
docker compose logs --tail=100 app
sudo nginx -t
sudo systemctl reload nginx
curl -I http://127.0.0.1:3000
```

For HTTPS:

```bash
sudo certbot renew --dry-run
curl -I https://example.com
```
