from typing import Literal, Optional, List, Any, Dict
from pydantic import BaseModel
from datetime import datetime


class MetricDataPoint(BaseModel):
    timestamp: datetime
    value: float


class MonitoringAlert(BaseModel):
    id: int
    deployment_id: int
    metric: str
    threshold: float
    comparison: Literal["greater_than", "less_than", "equal"]
    enabled: bool
    created_at: datetime


class MonitoringAlertCreate(BaseModel):
    deployment_id: int
    metric: str
    threshold: float
    comparison: Literal["greater_than", "less_than", "equal"]


class MonitoringConfig(BaseModel):
    id: int
    deployment_id: int
    enabled: bool
    check_interval: int  # seconds
    metrics_to_collect: List[str]
    retention_days: int
    created_at: datetime
    updated_at: datetime


class MonitoringConfigCreate(BaseModel):
    deployment_id: int
    check_interval: int = 60
    metrics_to_collect: List[str] = ["cpu", "memory", "disk", "requests"]
    retention_days: int = 30


class MonitoringMetrics(BaseModel):
    deployment_id: int
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    request_count: int
    error_count: int
    response_time_ms: float
    uptime_percentage: float
    last_check: datetime


class MonitoringReport(BaseModel):
    deployment_id: int
    period: Literal["hourly", "daily", "weekly", "monthly"]
    summary: Dict[str, Any]
    alerts_triggered: int
    generated_at: datetime
