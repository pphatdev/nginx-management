# Access Control

Control who can access sensitive paths.

## IP Allow/Deny

```nginx
location /admin/ {
    allow 10.0.0.0/24;
    allow 192.168.1.10;
    deny all;

    proxy_pass http://127.0.0.1:3000;
}
```

## Basic Authentication

```nginx
location /internal/ {
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;

    proxy_pass http://127.0.0.1:3000;
}
```

## Combined Controls

You can combine IP restrictions and auth for defense in depth.
