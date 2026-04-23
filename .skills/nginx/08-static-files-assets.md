# Static Files and Asset Delivery

Serve static content directly from Nginx for speed and lower backend load.

## Static Location Example

```nginx
location /assets/ {
    alias /var/www/example/assets/;
    access_log off;
    expires 30d;
    add_header Cache-Control "public, max-age=2592000, immutable";
}
```

## Common File-Type Caching

```nginx
location ~* \.(css|js|png|jpg|jpeg|gif|svg|ico|woff2?)$ {
    expires 30d;
    access_log off;
    add_header Cache-Control "public, max-age=2592000, immutable";
}
```

## Download Security

```nginx
location ~* \.(php|pl|py|sh|cgi)$ {
    deny all;
}
```

Avoid exposing executable scripts in static directories.
