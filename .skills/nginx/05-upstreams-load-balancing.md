# Upstreams and Load Balancing

Use upstream groups to distribute traffic across multiple backends.

## Upstream Group

```nginx
upstream app_backend {
    least_conn;
    server 10.0.0.11:3000 max_fails=3 fail_timeout=30s;
    server 10.0.0.12:3000 max_fails=3 fail_timeout=30s;
    keepalive 64;
}

server {
    listen 80;
    server_name app.example.com;

    location / {
        proxy_pass http://app_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
    }
}
```

## Balancing Methods

- Round-robin: default
- `least_conn`: least active connections
- `ip_hash`: sticky by client IP
- `hash $request_uri`: deterministic distribution by key

## Health and Resilience

- `max_fails` and `fail_timeout` avoid repeatedly failing nodes
- Configure upstream timeouts to prevent long hangs
- Keep backend instance configs identical for predictable behavior
