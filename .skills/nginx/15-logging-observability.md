# Logging and Observability

Logs are essential for debugging, security analysis, and traffic insight.

## Access and Error Logs

```nginx
access_log /var/log/nginx/example.access.log;
error_log  /var/log/nginx/example.error.log warn;
```

## Structured Log Format

```nginx
log_format json_combined escape=json
    '{"time":"$time_iso8601",'
    '"remote_addr":"$remote_addr",'
    '"method":"$request_method",'
    '"uri":"$request_uri",'
    '"status":$status,'
    '"bytes_sent":$body_bytes_sent,'
    '"request_time":$request_time,'
    '"upstream_time":"$upstream_response_time",'
    '"user_agent":"$http_user_agent"}';

access_log /var/log/nginx/access.json json_combined;
```

## Operational Practices

- Rotate logs (logrotate/system logging stack)
- Centralize logs in ELK/Loki/Cloud logging
- Alert on high 5xx rates and latency spikes
