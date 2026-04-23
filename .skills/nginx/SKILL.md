---
name: nginx-configuration
summary: Build, review, and troubleshoot Nginx configuration by feature using modular reference files.
---

# Nginx Configuration Skill

Use this skill when the user asks to:

- Create or update Nginx configuration
- Configure a specific Nginx feature (SSL, proxy, caching, headers, etc.)
- Review or harden an existing Nginx setup
- Troubleshoot Nginx runtime/configuration issues
- Prepare deployment checklists or production-ready examples

## Behavior

1. Identify the requested feature or outcome.
2. Open the matching feature file from this folder.
3. Provide production-safe configuration examples.
4. Explain why each non-obvious directive is needed.
5. Include validation/reload commands (`nginx -t` then reload).
6. Call out security and rollback considerations for risky changes.

## Feature Map

- Core structure: `01-core-structure.md`
- Server blocks: `02-server-blocks.md`
- Locations/routing: `03-locations-routing.md`
- Reverse proxy: `04-reverse-proxy.md`
- Upstreams/load balancing: `05-upstreams-load-balancing.md`
- SSL/TLS HTTPS: `06-ssl-tls-https.md`
- HTTP to HTTPS redirects: `07-http-https-redirects.md`
- Static files/assets: `08-static-files-assets.md`
- Caching: `09-caching.md`
- Compression: `10-compression.md`
- Security headers: `11-security-headers.md`
- Rate limiting/connection limits: `12-rate-limiting-limits.md`
- Access control: `13-access-control.md`
- Custom error pages: `14-custom-error-pages.md`
- Logging/observability: `15-logging-observability.md`
- WebSocket and HTTP/2: `16-websocket-http2.md`
- Performance tuning: `17-performance-tuning.md`
- Deployment checklist: `18-deployment-checklist.md`
- Troubleshooting: `19-troubleshooting.md`

## Response Style

- Prefer concise, copy-paste-ready Nginx blocks.
- Keep examples separated by concern (server block, location, upstream).
- Mention assumptions clearly (paths, cert files, backend ports).
- Avoid changing unrelated directives.

## Minimum Verification Steps

Always include these unless the user explicitly asks not to:

```bash
nginx -t
nginx -T
nginx -s reload
```

If systemd is used:

```bash
systemctl reload nginx
systemctl status nginx
```

## Escalation Pattern

If the issue is unclear:

1. Request current `server`/`location` snippet.
2. Request current error log lines.
3. Suggest the smallest safe change first.
4. Re-test and iterate.
