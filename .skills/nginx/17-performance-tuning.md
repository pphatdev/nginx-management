# Performance Tuning

Tune based on real workload metrics, not defaults alone.

## Common Baseline

```nginx
worker_processes auto;

events {
    worker_connections 4096;
    multi_accept on;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 30;
    keepalive_requests 1000;

    client_body_buffer_size 128k;
    client_max_body_size 20m;
}
```

## Reverse Proxy Efficiency

```nginx
proxy_http_version 1.1;
proxy_set_header Connection "";
```

Use keepalive to upstreams for better throughput.

## Measurement Loop

1. Baseline with current config
2. Change one variable at a time
3. Load test and compare latency/error rates
4. Keep only improvements
