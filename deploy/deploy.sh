#!/usr/bin/env bash
# deploy.sh — Install or update nginx-management on this server.
# Usage:
#   First deploy:  sudo bash deploy/deploy.sh --install
#   Update only:   sudo bash deploy/deploy.sh --update

set -euo pipefail

APP_NAME="nginx-management"
APP_DIR="/var/www/nginx-management"
APP_USER="${SUDO_USER:-pphat}"
SERVICE_FILE="deploy/${APP_NAME}.service"
NGINX_CONF="deploy/${APP_NAME}.conf"

INSTALL=false
UPDATE=false

for arg in "$@"; do
  case $arg in
    --install) INSTALL=true ;;
    --update)  UPDATE=true ;;
    *)
      echo "Usage: $0 --install | --update"
      exit 1
      ;;
  esac
done

if [[ "$INSTALL" == false && "$UPDATE" == false ]]; then
  echo "Usage: $0 --install | --update"
  exit 1
fi

# ── Update: pull code, sync deps, restart service ────────────────────────────
if [[ "$UPDATE" == true ]]; then
  echo "==> Pulling latest code..."
  cd "$APP_DIR"
  git pull origin master

  echo "==> Updating dependencies..."
  source .venv/bin/activate
  pip install --quiet --upgrade pip
  pip install --quiet -r requirements.txt

  echo "==> Restarting service..."
  systemctl restart "${APP_NAME}"
  systemctl status "${APP_NAME}" --no-pager
  echo "==> Update complete."
  exit 0
fi

# ── Install: full first-time setup ───────────────────────────────────────────
echo "==> Installing system packages..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv nginx ufw

echo "==> Configuring firewall..."
ufw allow OpenSSH
ufw allow 9991/tcp
ufw --force enable

echo "==> Setting directory ownership..."
chown -R "${APP_USER}:${APP_USER}" "$APP_DIR"

echo "==> Creating virtual environment..."
cd "$APP_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo "==> Setting up .env..."
if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "    .env created from .env.example — edit it before starting the service."
fi

echo "==> Installing systemd service..."
cp "${SERVICE_FILE}" /etc/systemd/system/
systemctl daemon-reload
systemctl enable "${APP_NAME}"
systemctl start "${APP_NAME}"
systemctl status "${APP_NAME}" --no-pager

echo "==> Installing Nginx config..."
cp "${NGINX_CONF}" /etc/nginx/sites-available/
ln -sf "/etc/nginx/sites-available/${APP_NAME}.conf" \
       "/etc/nginx/sites-enabled/${APP_NAME}.conf"
nginx -t
systemctl reload nginx

echo ""
echo "==> Done! Verify:"
echo "    systemctl status ${APP_NAME}"
echo "    curl -I http://127.0.0.1:9991"
echo ""
echo "    To enable HTTPS:"
echo "    sudo certbot --nginx -d <your-domain>"
