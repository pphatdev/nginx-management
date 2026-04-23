# Nginx Configuration Skill Pack

This folder is a reusable skill pack for Nginx configuration tasks.

- Skill entrypoint: `SKILL.md`
- Feature references: `01` to `19` markdown files in this folder

This documentation set is organized by feature so each Nginx capability can be configured, reviewed, and maintained independently.

## Contents

1. [Core Structure](./01-core-structure.md)
2. [Server Blocks (Virtual Hosts)](./02-server-blocks.md)
3. [Locations and Request Routing](./03-locations-routing.md)
4. [Reverse Proxy](./04-reverse-proxy.md)
5. [Upstreams and Load Balancing](./05-upstreams-load-balancing.md)
6. [SSL/TLS and HTTPS](./06-ssl-tls-https.md)
7. [HTTP to HTTPS Redirects](./07-http-https-redirects.md)
8. [Static Files and Asset Delivery](./08-static-files-assets.md)
9. [Caching](./09-caching.md)
10. [Compression (Gzip/Brotli)](./10-compression.md)
11. [Security Headers](./11-security-headers.md)
12. [Rate Limiting and Connection Limits](./12-rate-limiting-limits.md)
13. [Access Control](./13-access-control.md)
14. [Custom Error Pages](./14-custom-error-pages.md)
15. [Logging and Observability](./15-logging-observability.md)
16. [WebSocket and HTTP/2 Support](./16-websocket-http2.md)
17. [Performance Tuning](./17-performance-tuning.md)
18. [Deployment Checklist](./18-deployment-checklist.md)
19. [Troubleshooting](./19-troubleshooting.md)

## Recommended Usage

- Start from core structure and server blocks.
- Add reverse proxy and upstreams for app backends.
- Enforce HTTPS and security hardening.
- Apply caching/compression/performance directives.
- Validate with `nginx -t` before reload.

## Common Commands

```bash
nginx -t
nginx -T
nginx -s reload
```

On systemd-based Linux distributions:

```bash
systemctl reload nginx
systemctl restart nginx
systemctl status nginx
```
