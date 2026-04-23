# Security Headers

Security headers reduce exploit surface in browsers.

## Recommended Baseline

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

## Content Security Policy (Adjust per App)

```nginx
add_header Content-Security-Policy "default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self' 'unsafe-inline';" always;
```

## Notes

- CSP should be tuned to application behavior
- Use `always` so headers are set on error responses too
- Test with browser DevTools and security scanners
