# Nginx Management UI

A lightweight web-based dashboard for managing Nginx — built with **FastAPI** and **Jinja2 templates**, styled with **Tailwind CSS**.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009639?logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

| Page | Description |
|------|-------------|
| **Dashboard** | Live stats — active connections, requests/s, backend health, uptime |
| **Virtual Hosts** | View, toggle, and add Nginx server blocks |
| **Upstreams** | Manage upstream pools and individual backend health |
| **Config Editor** | Edit `nginx.conf` directly in the browser with line numbers |

- Auto-refreshing dashboard stats every 5 seconds
- Reload Nginx from the sidebar or topbar
- Toast notifications for all actions
- Dark UI built with Tailwind CSS

---

## Project Structure

```
nginx-management/
├── app.py              # FastAPI app factory — mounts static, registers routers
├── main.py             # Uvicorn entrypoint (python main.py)
├── requirements.txt
├── .env.example
├── core/
│   ├── config.py       # Settings via pydantic-settings (reads .env)
│   ├── models/
│   │   ├── server.py   # Server Pydantic model
│   │   └── upstream.py # Upstream / Backend Pydantic models
│   ├── routers/
│   │   ├── pages.py    # HTML page routes (/, /servers, /upstreams, /config)
│   │   └── api.py      # JSON API routes (/api/*)
│   └── services/
│       ├── nginx.py    # Nginx subprocess service (reload, test, read/write config)
│       └── store.py    # In-memory data store (swap for DB when ready)
├── templates/
│   ├── base.html       # Sidebar layout shell
│   ├── index.html      # Dashboard
│   ├── servers.html    # Virtual hosts
│   ├── upstreams.html  # Upstream pools
│   └── config.html     # Config editor
├── static/
│   ├── css/style.css
│   └── js/app.js
└── deploy/
    ├── deploy.sh                 # Install / update script
    ├── nginx-management.service  # systemd unit file
    └── nginx-management.conf     # Nginx reverse proxy config
```

---

## Getting Started

### Prerequisites

- Python 3.10+

### Installation

```bash
# Clone the repository
git clone https://github.com/pphatdev/nginx-management.git
cd nginx-management

# Create and activate a virtual environment (recommended)
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

Then open [http://localhost:9991](http://localhost:9991) in your browser.

The server starts with **hot-reload** enabled by default (`reload=True`).

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/stats` | Current Nginx stats |
| `GET` | `/api/servers` | List all virtual hosts |
| `POST` | `/api/servers/{id}/toggle` | Toggle server active/inactive |
| `GET` | `/api/upstreams` | List all upstream pools |
| `POST` | `/api/config/save` | Save nginx.conf content |
| `POST` | `/api/nginx/reload` | Trigger Nginx reload |

Interactive API docs are available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.111.0 | Web framework |
| `uvicorn` | 0.29.0 | ASGI server |
| `jinja2` | 3.1.4 | HTML templating |
| `python-multipart` | 0.0.26 | Form data parsing |

---

## Deployment

Production deployment uses **Gunicorn + Uvicorn workers** behind **Nginx**, managed by systemd.

### Files

```
deploy/
├── deploy.sh                   # Install / update script
├── nginx-management.service    # systemd unit file
└── nginx-management.conf       # Nginx reverse proxy config
```

### First Deploy

```bash
# On the target server (Ubuntu 22.04+)
git clone https://github.com/pphatdev/nginx-management.git /var/www/nginx-management
cd /var/www/nginx-management

# Run the install script (requires root).
# --user defaults to www-data; pass --user=USERNAME to use a different account.
sudo bash deploy/deploy.sh --install
# or with an explicit user:
sudo bash deploy/deploy.sh --install --user=myapp
```

> **Note:** The specified user must already exist on the system. If it doesn't,
> the script will exit with an error before making any changes. Create the user
> first with `sudo useradd --system --no-create-home myapp`.

The script will:

1. Install `python3`, `python3-venv`, `nginx`, and `ufw`
2. Create a virtualenv and install dependencies
3. Copy `.env.example` → `.env` (edit before starting)
4. Register and start the `nginx-management` systemd service
5. Install and enable the Nginx site config

### Configure Domain

Edit `deploy/nginx-management.conf` and replace `example.com` with your domain, then reload Nginx:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

### Enable HTTPS

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Deploy Updates

```bash
cd /var/www/nginx-management
sudo bash deploy/deploy.sh --update
```

### Verify

Verify the Nginx listener on `9991`:

```bash
systemctl status nginx-management
curl -I http://127.0.0.1:9991
sudo nginx -t
```

If your FastAPI upstream listens on a different internal port (for example `8000`), verify that separately from the Nginx listener.

### Troubleshoot

```bash
journalctl -u nginx-management -f
sudo tail -n 100 /var/log/nginx/error.log
sudo ss -tulpn | grep -E '(:80|:443|:9991)'
```

---

## License

MIT — see [LICENSE](LICENSE) for details.
