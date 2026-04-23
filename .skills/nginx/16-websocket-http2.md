# WebSocket and HTTP/2 Support

## WebSocket Proxying

WebSockets require explicit upgrade headers.

```nginx
location /socket/ {
    proxy_pass http://127.0.0.1:3000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_read_timeout 60s;
}
```

## HTTP/2 Enablement

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate     /etc/ssl/certs/example.crt;
    ssl_certificate_key /etc/ssl/private/example.key;
}
```

## Notes

- HTTP/2 requires TLS in most production setups
- Test clients and intermediaries for compatibility
- Monitor long-lived WebSocket connections for resource usage
