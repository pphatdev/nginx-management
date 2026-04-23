# Server Blocks (Virtual Hosts)

Server blocks allow hosting multiple domains and apps on one Nginx instance.

## Basic Example

```nginx
server {
    listen 80;
    server_name example.com www.example.com;

    root /var/www/example/public;
    index index.html index.htm;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

## Common Directives

- `listen`: port and protocol (`80`, `443 ssl`, etc.)
- `server_name`: domain aliases
- `root` or `alias`: content path
- `index`: default file list

## Multiple Applications

Use separate files per app for maintainability.

```text
conf.d/app1.conf
conf.d/app2.conf
conf.d/admin.conf
```

## Best Practices

- Keep one logical app/domain per server block file
- Add explicit default server for unknown hosts
- Use dedicated access/error logs per app when possible
