# Reverse Proxy

Nginx commonly proxies requests to backend services.

## Basic Proxy Configuration

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Important Proxy Settings

- `proxy_connect_timeout`: time to establish upstream connection
- `proxy_send_timeout`: timeout for sending request to upstream
- `proxy_read_timeout`: timeout for reading upstream response
- `client_max_body_size`: upload limit

## Path Rewriting Behavior

Trailing slash matters:

```nginx
location /api/ {
    proxy_pass http://backend/;
}
```

This strips `/api/` from forwarded path. Without trailing `/`, path is preserved differently. Test route mapping explicitly.
