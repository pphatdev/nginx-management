# Core Structure

## Typical File Layout

```text
/etc/nginx/
  nginx.conf
  conf.d/*.conf
  sites-available/*
  sites-enabled/*
  snippets/*
```

- `nginx.conf`: global configuration entry point.
- `http` block: most web traffic directives.
- `events` block: connection handling.
- `server` block: virtual host per domain/app.
- `location` block: request path matching and handling.

## Minimal Baseline

```nginx
user nginx;
worker_processes auto;

events {
    worker_connections 1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;

    sendfile on;
    keepalive_timeout 65;

    include /etc/nginx/conf.d/*.conf;
}
```

## Include Strategy

Keep files focused and modular:

- Global defaults in `nginx.conf`
- One server/application per file in `conf.d` or `sites-available`
- Shared snippets for repeated directives

## Validation and Reload

```bash
nginx -t
nginx -s reload
```

Always validate first to avoid applying broken configuration.
