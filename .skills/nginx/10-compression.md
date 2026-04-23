# Compression (Gzip/Brotli)

Compression reduces transferred bytes and improves perceived speed.

## Gzip Configuration

```nginx
gzip on;
gzip_comp_level 5;
gzip_min_length 1024;
gzip_vary on;
gzip_proxied any;
gzip_types
    text/plain
    text/css
    text/javascript
    application/javascript
    application/json
    application/xml
    image/svg+xml;
```

## Brotli (If Module Available)

```nginx
brotli on;
brotli_comp_level 5;
brotli_static on;
brotli_types text/plain text/css application/javascript application/json image/svg+xml;
```

## Recommendations

- Prefer moderate compression level (4-6)
- Skip already-compressed formats (zip, mp4, jpg)
- Validate CPU impact under load
