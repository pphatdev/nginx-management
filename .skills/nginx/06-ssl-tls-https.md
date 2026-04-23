# SSL/TLS and HTTPS

Secure traffic with TLS certificates and modern protocol settings.

## HTTPS Server Example

```nginx
server {
    listen 443 ssl http2;
    server_name example.com www.example.com;

    ssl_certificate     /etc/ssl/certs/example.crt;
    ssl_certificate_key /etc/ssl/private/example.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;

    location / {
        proxy_pass http://127.0.0.1:3000;
    }
}
```

## OCSP Stapling (If Supported)

```nginx
ssl_stapling on;
ssl_stapling_verify on;
resolver 1.1.1.1 8.8.8.8 valid=300s;
resolver_timeout 5s;
```

## Certificate Automation

For Let's Encrypt, renew automatically and reload Nginx after renewal.

## Security Notes

- Disable old protocols/ciphers
- Protect private key permissions
- Test with SSL Labs or equivalent tooling
