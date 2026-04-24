"""
Nginx service — wraps subprocess calls to the nginx binary and filesystem
operations on nginx.conf.

Falls back gracefully when nginx is not installed (development mode).
"""
import datetime
import os
import subprocess
from pathlib import Path

from core.config import settings

_DEFAULT_CONFIG = """\
user  nginx;
worker_processes  auto;

error_log  /var/log/nginx/error.log notice;
pid        /var/run/nginx.pid;

events {
    worker_connections  1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    keepalive_timeout  65;
    gzip  on;

    include /etc/nginx/conf.d/*.conf;
}
"""


def _run(cmd: list[str], stdin: str | None = None) -> tuple[bool, str]:
    """Run a subprocess command. Returns (success, combined output)."""
    try:
        result = subprocess.run(
            cmd,
            input=stdin,
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0, output
    except FileNotFoundError:
        return False, f"Command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return False, "Command timed out"


def _sudo(cmd: list[str]) -> list[str]:
    """Prepend 'sudo --non-interactive' when nginx_use_sudo is enabled."""
    if settings.nginx_use_sudo:
        return ["sudo", "--non-interactive"] + cmd
    return cmd


def is_running() -> bool:
    """Check if nginx is running via its PID file."""
    pid_path = Path(settings.nginx_pid_path)
    if not pid_path.exists():
        return False
    try:
        pid = int(pid_path.read_text().strip())
        os.kill(pid, 0)
        return True
    except (ValueError, ProcessLookupError, PermissionError):
        return False


def get_version() -> str:
    """Return the installed nginx version string, or 'unknown'."""
    _, out = _run([settings.nginx_binary, "-v"])
    for line in out.splitlines():
        if "nginx/" in line:
            return line.split("nginx/")[-1].strip()
    return "unknown"


def test_config() -> tuple[bool, str]:
    """Run `nginx -t` to validate the active config."""
    return _run(_sudo([settings.nginx_binary, "-t"]))


def reload() -> tuple[bool, str]:
    """Validate config then send a reload signal to nginx."""
    ok, out = test_config()
    if not ok:
        return False, f"Config test failed: {out}"
    return _run([settings.nginx_binary, "-s", "reload"])


def read_config() -> str:
    """Read nginx.conf from disk. Returns a stub when not present (dev mode)."""
    path = Path(settings.nginx_config_path)
    if path.exists():
        return path.read_text()
    return _DEFAULT_CONFIG


def write_config(content: str) -> tuple[bool, str]:
    """
    Write new config content to disk and validate with `nginx -t`.
    Automatically rolls back to the previous config if validation fails.

    In production (nginx_use_sudo=True) the write is done via `sudo tee` so
    the unprivileged service account does not need direct write access to
    nginx.conf.  The sudoers drop-in (deploy/nginx-management-sudoers) grants
    only the minimum commands required.

    Returns (success, message).
    """
    path = Path(settings.nginx_config_path)
    if not path.exists():
        return True, "Config saved (dev mode — no file written)"

    if settings.nginx_use_sudo:
        # Read backup (nginx.conf is world-readable; no sudo needed for read)
        try:
            backup = path.read_text()
        except PermissionError:
            return False, "Permission denied reading nginx.conf"

        # Write via sudo tee (stdout discarded, only exit code matters)
        ok, out = _run(
            ["sudo", "--non-interactive", "tee", str(path)],
            stdin=content,
        )
        if not ok:
            return False, f"Permission denied writing nginx.conf: {out}"

        # Validate; roll back on failure
        valid, out = test_config()
        if not valid:
            _run(["sudo", "--non-interactive", "tee", str(path)], stdin=backup)
            return False, f"Validation failed, rolled back: {out}"
        return True, "Config saved and validated"

    try:
        backup = path.read_text()
        path.write_text(content)
        ok, out = test_config()
        if not ok:
            path.write_text(backup)
            return False, f"Validation failed, rolled back: {out}"
        return True, "Config saved and validated"
    except PermissionError:
        return False, "Permission denied — set NGINX_USE_SUDO=true and install the sudoers drop-in"


def get_stats() -> dict:
    """
    Return a stats dict for the dashboard.
    Active connections and throughput require the nginx stub_status module;
    simulated values are returned when it is not configured.
    """
    return {
        "nginx_version": get_version(),
        "running": is_running(),
        "uptime": "N/A",
        "active_connections": 0,
        "requests_per_sec": 0,
        "bytes_in": "N/A",
        "bytes_out": "N/A",
        "last_reload": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
