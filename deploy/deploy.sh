#!/usr/bin/env bash
# deploy.sh — Install or update nginx-management on this server.
# Usage:
#   First deploy:  sudo bash deploy/deploy.sh --install [--user=USERNAME]
#   Update only:   sudo bash deploy/deploy.sh --update

set -euo pipefail

APP_NAME="nginx-management"
APP_DIR="/var/www/nginx-management"
APP_USER="${SUDO_USER:-www-data}"
SERVICE_FILE="deploy/${APP_NAME}.service"
NGINX_CONF="deploy/${APP_NAME}.conf"

INSTALL=false
UPDATE=false

for arg in "$@"; do
  case $arg in
    --install)  INSTALL=true ;;
    --update)   UPDATE=true ;;
    --user=*)   APP_USER="${arg#*=}" ;;
    *)
      echo "Usage: $0 --install | --update [--user=USERNAME]"
      exit 1
      ;;
  esac
done

if [[ "$INSTALL" == false && "$UPDATE" == false ]]; then
  echo "Usage: $0 --install | --update [--user=USERNAME]"
  exit 1
fi

# Validate the deployment user exists before proceeding
if ! id -u "${APP_USER}" &>/dev/null; then
  echo "Error: user '${APP_USER}' does not exist."
  echo "       Create the user first or specify an existing one with --user=USERNAME"
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

echo "==> Setting directory ownership (user: ${APP_USER})..."
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
SERVICE_DEST="/etc/systemd/system/${APP_NAME}.service"
sed \
  -e "s|__APP_USER__|${APP_USER}|g" \
  -e "s|__APP_DIR__|${APP_DIR}|g" \
  "${SERVICE_FILE}" > "${SERVICE_DEST}"
systemctl daemon-reload
systemctl enable "${APP_NAME}"
systemctl start "${APP_NAME}"
systemctl status "${APP_NAME}" --no-pager

echo "==> Installing sudoers drop-in for nginx privilege delegation..."
NGINX_BIN="$(command -v nginx 2>/dev/null || echo /usr/sbin/nginx)"
NGINX_CONF_PATH="${NGINX_CONFIG_PATH:-/etc/nginx/nginx.conf}"
SUDOERS_DEST="/etc/sudoers.d/${APP_NAME}"
sed \
  -e "s|__APP_USER__|${APP_USER}|g" \
  -e "s|__NGINX_BIN__|${NGINX_BIN}|g" \
  -e "s|__NGINX_CONF__|${NGINX_CONF_PATH}|g" \
  "deploy/nginx-management-sudoers" > "${SUDOERS_DEST}"
chmod 0440 "${SUDOERS_DEST}"
visudo -cf "${SUDOERS_DEST}" || { echo "Error: generated sudoers file is invalid — aborting"; rm -f "${SUDOERS_DEST}"; exit 1; }

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
