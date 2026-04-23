# Rate Limiting and Connection Limits

Use request and connection limits to protect upstream services.

## Define Shared Zones

```nginx
limit_req_zone $binary_remote_addr zone=req_per_ip:10m rate=10r/s;
limit_conn_zone $binary_remote_addr zone=conn_per_ip:10m;
```

## Apply in Server/Location

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        limit_req zone=req_per_ip burst=20 nodelay;
        limit_conn conn_per_ip 20;

        proxy_pass http://127.0.0.1:3000;
    }
}
```

## Tuning Guidance

- Start leniently, then tighten from observed traffic
- Exclude trusted internal networks if needed
- Return meaningful status (`429 Too Many Requests`)
