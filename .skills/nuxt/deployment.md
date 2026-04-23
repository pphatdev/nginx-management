# Deploy Nuxt.js on Ubuntu with Nginx (From Scratch)

Docker users: use `deployment-docker.md` in this same folder for a containerized deployment path.

This skill provides a production-ready setup for deploying a Nuxt.js app on Ubuntu using:

- `systemd` to run Nuxt as a background service
- `nginx` as a reverse proxy

It assumes a clean Ubuntu server and a Nuxt app served by Nitro on a local port (for example `3000`).

## 1. Server Prerequisites

Update server packages:

```bash
sudo apt update && sudo apt upgrade -y
```

Install required tools:

```bash
sudo apt install -y curl git nginx ufw
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

## 2. Install Node.js (LTS)

Use NodeSource for a straightforward system-wide install.

```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs
node -v
npm -v
```

## 3. Create Application Directory

Create a dedicated deploy user (optional but recommended):

```bash
sudo adduser --disabled-password --gecos "" deploy
sudo usermod -aG sudo deploy
```

Create app directory:

```bash
sudo mkdir -p /var/www/my-nuxt-app
sudo chown -R $USER:$USER /var/www/my-nuxt-app
cd /var/www/my-nuxt-app
```

Clone or copy your project:

```bash
git clone <your-repository-url> .
npm ci --omit=dev
```

Build Nuxt for production:

```bash
npm run build
```

## 4. Configure Environment Variables

Create your environment file:

```bash
cp .env.example .env
nano .env
```

Set runtime environment (example):

```env
PORT=3000
NODE_ENV=production
NUXT_HOST=127.0.0.1
NUXT_PORT=3000
```

Nuxt should listen on `127.0.0.1:3000` (or `0.0.0.0:3000` if needed).

## 5. Create Systemd Service

Create service file:

```bash
sudo nano /etc/systemd/system/my-nuxt-app.service
```

Paste:

```ini
[Unit]
Description=My Nuxt App
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/my-nuxt-app
Environment=NODE_ENV=production
EnvironmentFile=/var/www/my-nuxt-app/.env
ExecStart=/usr/bin/node /var/www/my-nuxt-app/.output/server/index.mjs
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Notes:

- `ExecStart` uses Nuxt 3/Nitro build output.
- Ensure `npm run build` has been executed before starting the service.
- If your project uses a custom output or start command, adjust `ExecStart` accordingly.

Enable and run service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable my-nuxt-app
sudo systemctl start my-nuxt-app
sudo systemctl status my-nuxt-app --no-pager
```

View logs:

```bash
journalctl -u my-nuxt-app -f
```

## 6. Configure Nginx Reverse Proxy

Create Nginx site config:

```bash
sudo nano /etc/nginx/sites-available/my-nuxt-app
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

Enable site and validate config:

```bash
sudo ln -s /etc/nginx/sites-available/my-nuxt-app /etc/nginx/sites-enabled/
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
cd /var/www/my-nuxt-app
git pull origin main
npm ci --omit=dev
npm run build --if-present
sudo systemctl restart my-nuxt-app
sudo systemctl status my-nuxt-app --no-pager
```

## 9. Basic Troubleshooting

Check app service status:

```bash
sudo systemctl status my-nuxt-app --no-pager
journalctl -u my-nuxt-app -n 100 --no-pager
```

Check Nginx status and logs:

```bash
sudo systemctl status nginx --no-pager
sudo tail -n 100 /var/log/nginx/error.log
sudo tail -n 100 /var/log/nginx/access.log
```

Check open listening ports:

```bash
sudo ss -tulpn | grep -E '(:80|:443|:3000)'
```

## 10. Nuxt Production Notes

- Run the service as a non-root user.
- Keep secrets in `.env` and restrict file permissions.
- Use `npm ci` for deterministic installs.
- For Nuxt 3, deploy SSR output from `.output/` and restart service after each build.
- Confirm runtime config values are supplied through environment variables.
- Set up monitoring (for example health endpoint + uptime checks).
- Automate deploy with CI/CD once manual flow is stable.
