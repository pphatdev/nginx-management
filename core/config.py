from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    APP_NAME: str = "Nginx Management"
    HOST: str = "0.0.0.0"
    PORT: int = 9991
    RELOAD: bool = True
    NGINX_USE_SUDO: bool = True
    NGINX_CONF_PATH: str = "/etc/nginx/nginx.conf"
    
    ENV: str = "development"
    
    class Config:
        env_file = ".env"
        env_prefix = "APP_"
        extra = "ignore"

settings = Settings()
