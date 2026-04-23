# HTTP to HTTPS Redirects

Always redirect plaintext HTTP to encrypted HTTPS.

## Standard Redirect

```nginx
server {
    listen 80;
    server_name example.com www.example.com;

    return 301 https://$host$request_uri;
}
```

## Canonical Host Redirect (Optional)

```nginx
server {
    listen 443 ssl http2;
    server_name www.example.com;

    ssl_certificate     /etc/ssl/certs/example.crt;
    ssl_certificate_key /etc/ssl/private/example.key;

    return 301 https://example.com$request_uri;
}
```

## HSTS (Only After HTTPS Is Stable)

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

Do not enable long HSTS until you are sure all subdomains support HTTPS.
