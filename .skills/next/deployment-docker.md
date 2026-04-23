# Deploy Next.js on Ubuntu with Docker and Nginx

This guide provides a production-ready Docker workflow for Next.js behind Nginx.

It uses:

- Docker multi-stage build for a smaller runtime image
- Docker Compose for app lifecycle management
- Nginx on host as reverse proxy and TLS termination

## 1. Server Prerequisites

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git nginx ufw ca-certificates gnupg
```

Enable Nginx and firewall:

```bash
sudo systemctl enable nginx
sudo systemctl start nginx
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

## 2. Install Docker Engine + Compose Plugin

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
```

Optional non-root Docker usage:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

## 3. App Directory and Source

```bash
sudo mkdir -p /opt/my-next-app
sudo chown -R $USER:$USER /opt/my-next-app
cd /opt/my-next-app
git clone <your-repository-url> .
```

## 4. Create Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

COPY package.json package-lock.json* ./
RUN npm ci --omit=dev && npm cache clean --force
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.* ./

EXPOSE 3000
CMD ["npm", "run", "start"]
```

## 5. Create Docker Compose File

Create `docker-compose.yml`:

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: my-next-app
    restart: unless-stopped
    env_file:
      - .env
    environment:
      NODE_ENV: production
      PORT: 3000
      HOSTNAME: 0.0.0.0
    ports:
      - "127.0.0.1:3000:3000"
```

Binding to `127.0.0.1` keeps the app private to the host and accessible only via Nginx.

## 6. Environment Variables

```bash
cp .env.example .env
nano .env
```

Example:

```env
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1
PORT=3000
HOSTNAME=0.0.0.0
```

## 7. Build and Start Container

```bash
cd /opt/my-next-app
docker compose build --pull
docker compose up -d
docker compose ps
docker compose logs --tail=100 app
```

## 8. Configure Nginx Reverse Proxy

Create site file:

```bash
sudo nano /etc/nginx/sites-available/my-next-app
```

Paste:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name example.com www.example.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable and reload:

```bash
sudo ln -s /etc/nginx/sites-available/my-next-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 9. Enable HTTPS

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d example.com -d www.example.com
sudo certbot renew --dry-run
```

## 10. Deploy Updates

```bash
cd /opt/my-next-app
git pull origin main
docker compose build --pull
docker compose up -d --remove-orphans
docker image prune -f
```

## 11. Rollback Strategy

- Keep previous image tag instead of only `latest`
- Roll back with a pinned image tag in compose
- Reload Nginx only after health checks pass

## 12. Troubleshooting

App logs:

```bash
docker compose logs -f app
```

Container/process health:

```bash
docker compose ps
docker stats --no-stream
```

Nginx checks:

```bash
sudo nginx -t
sudo systemctl status nginx --no-pager
sudo tail -n 100 /var/log/nginx/error.log
```

Port checks:

```bash
sudo ss -tulpn | grep -E '(:80|:443|:3000)'
```
