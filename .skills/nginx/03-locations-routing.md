# Locations and Request Routing

`location` controls how Nginx matches request URIs.

## Match Order Summary

1. Exact match: `location = /path`
2. Prefix with `^~`: `location ^~ /assets/`
3. Regex (`~` case-sensitive, `~*` case-insensitive)
4. Longest normal prefix match

## Examples

```nginx
location = /health {
    return 200 "ok";
}

location ^~ /static/ {
    root /var/www/example;
}

location ~* \.(png|jpg|jpeg|gif|css|js)$ {
    expires 7d;
    access_log off;
}

location / {
    try_files $uri $uri/ /index.html;
}
```

## `root` vs `alias`

- `root`: appends request URI to configured path
- `alias`: replaces matching part of URI

Example:

```nginx
location /media/ {
    alias /srv/media/;
}
```

Request `/media/a.jpg` maps to `/srv/media/a.jpg`.

## SPA Fallback

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

Use this for frontend routers (React/Vue/Angular SPA).
