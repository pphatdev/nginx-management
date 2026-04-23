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
├── app.py              # FastAPI application & API routes
├── requirements.txt
├── templates/
│   ├── base.html       # Sidebar layout shell
│   ├── index.html      # Dashboard
│   ├── servers.html    # Virtual hosts
│   ├── upstreams.html  # Upstream pools
│   └── config.html     # Config editor
└── static/
    ├── css/style.css
    └── js/app.js
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
python app.py
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

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

## License

MIT — see [LICENSE](LICENSE) for details.
