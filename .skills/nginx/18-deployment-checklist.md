# Deployment Checklist

This checklist aligns with GUI-driven deployment flow and Nginx best practices.

## Pre-Deployment

- Verify build and local tests
- Prepare environment variables/secrets
- Backup current Nginx config and app files
- Prepare SSL certificates (or ACME automation)

## Server Configuration

- Create/update server block
- Set `server_name`, `root`, and `index`
- Configure proxy/static routes
- Add security headers
- Configure gzip and cache headers

## TLS and Redirects

- Install certificate and key
- Enable HTTPS server block
- Add HTTP to HTTPS redirect
- Confirm certificate chain and expiry

## Validation

- Run `nginx -t`
- Reload Nginx
- Verify key routes (`/`, `/health`, APIs)
- Confirm static assets and uploads
- Check logs for 4xx/5xx anomalies

## Post-Deployment

- Monitor latency/error rate
- Verify backup and rollback plan
- Record config changes and release details
