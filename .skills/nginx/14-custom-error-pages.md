# Custom Error Pages

Custom error pages improve user experience and branding.

## Configuration Example

```nginx
server {
    listen 80;
    server_name example.com;
    root /var/www/example/public;

    error_page 404 /errors/404.html;
    error_page 500 502 503 504 /errors/50x.html;

    location /errors/ {
        internal;
    }
}
```

## Notes

- Keep error pages lightweight and static
- Use `internal` so users cannot request these files directly
- Optionally include incident/tracking IDs for support workflows
