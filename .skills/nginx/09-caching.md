# Caching

Nginx supports browser caching headers and reverse proxy caching.

## Browser Caching

```nginx
location ~* \.(css|js|png|jpg|jpeg|gif|svg|ico)$ {
    expires 7d;
    add_header Cache-Control "public, max-age=604800";
}
```

## Proxy Cache Setup

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=app_cache:100m max_size=2g inactive=60m use_temp_path=off;

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_cache app_cache;
        proxy_cache_valid 200 10m;
        proxy_cache_valid 404 1m;
        proxy_cache_bypass $http_cache_control;
        add_header X-Cache-Status $upstream_cache_status always;

        proxy_pass http://127.0.0.1:3000;
    }
}
```

## Cache Strategy Tips

- Cache only idempotent responses by default
- Do not cache authenticated/private API responses unless designed for it
- Expose cache status header for debugging
