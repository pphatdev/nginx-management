from typing import Literal, List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class DeploymentConfig(BaseModel):
    environment_vars: Optional[Dict[str, str]] = {}
    custom_config: Optional[Dict[str, Any]] = {}


class Deployment(BaseModel):
    id: int
    name: str
    project_type: Literal["nextjs", "nuxtjs", "nodejs", "python", "static"]
    service_type: Literal["supervisorctl", "systemd", "pm2", "docker"]
    domain: str
    status: Literal["active", "inactive", "error"]
    config: DeploymentConfig
    created_at: datetime
    updated_at: datetime


class DeploymentCreate(BaseModel):
    name: str
    project_type: Literal["nextjs", "nuxtjs", "nodejs", "python", "static"]
    service_type: Literal["supervisorctl", "systemd", "pm2", "docker"]
    domain: str
    config: DeploymentConfig


class DeploymentUpdate(BaseModel):
    project_type: Optional[Literal["nextjs", "nuxtjs", "nodejs", "python", "static"]] = None
    service_type: Optional[Literal["supervisorctl", "systemd", "pm2", "docker"]] = None
    domain: Optional[str] = None
    status: Optional[Literal["active", "inactive", "error"]] = None
    config: Optional[DeploymentConfig] = None
