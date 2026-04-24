from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class LoadBalancerRule(BaseModel):
    id: int
    name: str
    condition: Dict[str, Any]  # e.g., {"path": "/api/*", "method": "GET"}
    action: Dict[str, Any]  # e.g., {"upstream": "backend_pool", "weight": 100}
    enabled: bool
    order: int


class LoadBalancerRuleCreate(BaseModel):
    name: str
    condition: Dict[str, Any]
    action: Dict[str, Any]
    order: int = 0


class LoadBalancerRuleUpdate(BaseModel):
    name: Optional[str] = None
    condition: Optional[Dict[str, Any]] = None
    action: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None
    order: Optional[int] = None


class LoadBalancerConfig(BaseModel):
    id: int
    deployment_id: int
    algorithm: Literal["round_robin", "least_conn", "ip_hash", "weighted"]
    enabled: bool
    rules: List[LoadBalancerRule]
    session_persistence: bool
    session_timeout: int  # seconds
    health_check_enabled: bool
    health_check_interval: int  # seconds
    health_check_path: str
    created_at: datetime
    updated_at: datetime


class LoadBalancerConfigCreate(BaseModel):
    deployment_id: int
    algorithm: Literal["round_robin", "least_conn", "ip_hash", "weighted"] = "round_robin"
    session_persistence: bool = False
    session_timeout: int = 3600
    health_check_enabled: bool = True
    health_check_interval: int = 10
    health_check_path: str = "/"


class LoadBalancerConfigUpdate(BaseModel):
    algorithm: Optional[Literal["round_robin", "least_conn", "ip_hash", "weighted"]] = None
    enabled: Optional[bool] = None
    session_persistence: Optional[bool] = None
    session_timeout: Optional[int] = None
    health_check_enabled: Optional[bool] = None
    health_check_interval: Optional[int] = None
    health_check_path: Optional[str] = None


class LoadBalancerInstance(BaseModel):
    address: str
    port: int
    weight: int
    status: Literal["up", "down", "draining"]
    active_connections: int
    total_requests: int


class LoadBalancerMetrics(BaseModel):
    deployment_id: int
    total_requests: int
    requests_per_sec: float
    active_connections: int
    connection_errors: int
    average_response_time_ms: float
    instances: List[LoadBalancerInstance]
    last_updated: datetime
