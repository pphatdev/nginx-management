# Troubleshooting

## 1. Nginx Won't Reload

Symptoms:

- Reload fails or service remains in failed state

Checks:

```bash
nginx -t
nginx -T
systemctl status nginx
```

Fixes:

- Correct syntax errors and missing includes
- Validate certificate/key paths and permissions

## 2. 502 Bad Gateway

Common causes:

- Upstream service down
- Wrong `proxy_pass` host/port
- Timeout too low

Checks:

- Confirm backend listening port
- Review error log for upstream messages
- Increase `proxy_read_timeout` if needed

## 3. 404 for Existing Static File

Common causes:

- `root`/`alias` mismatch
- Incorrect location precedence

Checks:

- Verify resolved filesystem path
- Re-check location match order

## 4. Redirect Loops

Common causes:

- Mixed HTTP/HTTPS rules between Nginx and upstream app

Fixes:

- Standardize redirect logic in one layer
- Ensure `X-Forwarded-Proto` is forwarded

## 5. SSL Handshake Problems

Common causes:

- Invalid certificate chain
- Unsupported protocol/cipher mismatch

Fixes:

- Install full chain/intermediate certs
- Keep TLS 1.2/1.3 enabled

## 6. High CPU/Memory Usage

Checks:

- Enable/inspect access logs and request patterns
- Detect abusive clients and apply rate limiting
- Revisit compression and worker tuning
