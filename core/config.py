from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 9991

    nginx_config_path: str = "/etc/nginx/nginx.conf"
    nginx_pid_path: str = "/var/run/nginx.pid"
    nginx_binary: str = "nginx"
    # Set to True in production so nginx -t / nginx -s reload run via sudo.
    # Requires the sudoers drop-in from deploy/nginx-management-sudoers.
    nginx_use_sudo: bool = False


settings = Settings()
