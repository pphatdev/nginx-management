# Deploy Python (FastAPI) on Ubuntu with Docker and Nginx

This guide provides a production-ready Docker workflow for a Python (FastAPI) app behind Nginx.

## 1. Server Prerequisites

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git nginx ufw ca-certificates gnupg
sudo systemctl enable nginx
sudo systemctl start nginx
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

## 2. Install Docker Engine + Compose

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

## 3. Project Directory

```bash
sudo mkdir -p /opt/my-python-app
sudo chown -R $USER:$USER /opt/my-python-app
cd /opt/my-python-app
git clone <your-repository-url> .
```

## 4. Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.12-slim AS base
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

FROM base AS deps
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt gunicorn

FROM deps AS runtime
COPY . .
EXPOSE 8000
CMD ["gunicorn", "app:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

Notes:

- Replace `app:app` with `module:variable` matching your entrypoint (e.g. `main:app`).
- For Flask (WSGI) apps, omit `--worker-class` to use the default sync worker.

## 5. Docker Compose

Create `docker-compose.yml`:

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: my-python-app
    restart: unless-stopped
    env_file:
      - .env
    environment:
      APP_ENV: production
    ports:
      - "127.0.0.1:8000:8000"
```

## 6. Environment Variables

```bash
cp .env.example .env
nano .env
```

Example:

```env
APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=8000
```

## 7. Build and Start

```bash
docker compose build --pull
docker compose up -d
docker compose ps
docker compose logs --tail=100 app
```

## 8. Nginx Reverse Proxy

Create `/etc/nginx/sites-available/my-python-app`:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name example.com www.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and reload:

```bash
sudo ln -s /etc/nginx/sites-available/my-python-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 9. HTTPS

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d example.com -d www.example.com
sudo certbot renew --dry-run
```

## 10. Deploy Updates

```bash
cd /opt/my-python-app
git pull origin main
docker compose build --pull
docker compose up -d --remove-orphans
docker image prune -f
```

## 11. Troubleshooting

```bash
docker compose logs -f app
docker compose ps
sudo nginx -t
sudo tail -n 100 /var/log/nginx/error.log
sudo ss -tulpn | grep -E '(:80|:443|:8000)'
```
