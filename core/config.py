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
    app_port: int = 8000

    nginx_config_path: str = "/etc/nginx/nginx.conf"
    nginx_pid_path: str = "/var/run/nginx.pid"
    nginx_binary: str = "nginx"


settings = Settings()
