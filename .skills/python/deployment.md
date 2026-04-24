# Deploy Python (FastAPI) on Ubuntu with Nginx (From Scratch)

Docker users: use `deployment-docker.md` in this same folder for a containerized deployment path.

This skill provides a production-ready setup for deploying a Python (FastAPI) app on Ubuntu using:

- `systemd` to run the app as a background service via Gunicorn + Uvicorn workers
- `nginx` as a reverse proxy

It assumes a clean Ubuntu server and a FastAPI app served on a local port (for example `8000`).

## 1. Server Prerequisites

Update server packages:

```bash
sudo apt update && sudo apt upgrade -y
```

Install required tools:

```bash
sudo apt install -y curl git nginx ufw python3 python3-pip python3-venv
```

Enable and start Nginx:

```bash
sudo systemctl enable nginx
sudo systemctl start nginx
```

Configure firewall:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
sudo ufw status
```

## 2. Create Application Directory

Create a dedicated deploy user (optional but recommended):

```bash
sudo adduser --disabled-password --gecos "" deploy
sudo usermod -aG sudo deploy
```

Create app directory:

```bash
sudo mkdir -p /var/www/my-python-app
sudo chown -R $USER:$USER /var/www/my-python-app
cd /var/www/my-python-app
```

Clone or copy your project:

```bash
git clone <your-repository-url> .
```

## 3. Set Up Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

## 4. Configure Environment Variables

Create your environment file:

```bash
cp .env.example .env
nano .env
```

Set runtime environment (example):

```env
APP_ENV=production
APP_HOST=127.0.0.1
APP_PORT=8000
```

## 5. Create Systemd Service

Create service file:

```bash
sudo nano /etc/systemd/system/my-python-app.service
```

Paste:

```ini
[Unit]
Description=My Python App
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/my-python-app
EnvironmentFile=/var/www/my-python-app/.env
ExecStart=/var/www/my-python-app/.venv/bin/gunicorn app:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --access-logfile - \
    --error-logfile -
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Notes:

- Replace `app:app` with `module:variable` matching your entrypoint (e.g. `main:app`).
- Adjust `--workers` based on CPU count: `(2 × CPU cores) + 1` is a common starting point.
- For Flask (WSGI) apps, use `--worker-class sync` and omit the Uvicorn worker.

Enable and run service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable my-python-app
sudo systemctl start my-python-app
sudo systemctl status my-python-app --no-pager
```

View logs:

```bash
journalctl -u my-python-app -f
```

## 6. Configure Nginx Reverse Proxy

Create Nginx site config:

```bash
sudo nano /etc/nginx/sites-available/my-python-app
```

Paste:

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

		proxy_cache_bypass $http_upgrade;
	}
}
```

Enable site and validate config:

```bash
sudo ln -s /etc/nginx/sites-available/my-python-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

Optional: disable default site:

```bash
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

## 7. Enable HTTPS (Recommended)

Install Certbot:

```bash
sudo apt install -y certbot python3-certbot-nginx
```

Issue and install certificate:

```bash
sudo certbot --nginx -d example.com -d www.example.com
```

Test auto-renew:

```bash
sudo certbot renew --dry-run
```

## 8. Deploy Updates

From app directory:

```bash
cd /var/www/my-python-app
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart my-python-app
sudo systemctl status my-python-app --no-pager
```

## 9. Basic Troubleshooting

Check app service status:

```bash
sudo systemctl status my-python-app --no-pager
journalctl -u my-python-app -n 100 --no-pager
```

Check Nginx status and logs:

```bash
sudo systemctl status nginx --no-pager
sudo tail -n 100 /var/log/nginx/error.log
sudo tail -n 100 /var/log/nginx/access.log
```

Check open listening ports:

```bash
sudo ss -tulpn | grep -E '(:80|:443|:8000)'
```

## 10. Python Production Notes

- Run the service as a non-root user (`www-data` or a dedicated `deploy` user).
- Keep secrets in `.env` and restrict file permissions (`chmod 600 .env`).
- Use a virtual environment and pin versions in `requirements.txt`.
- For FastAPI, use Gunicorn with `uvicorn.workers.UvicornWorker` for production ASGI serving.
- For Flask (WSGI), use `--worker-class sync` (default) with Gunicorn.
- Confirm runtime config values are supplied through environment variables.
- Set up monitoring (for example `/health` endpoint + uptime checks).
- Automate deploy with CI/CD once manual flow is stable.
