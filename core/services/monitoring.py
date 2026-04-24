from typing import List, Optional, Dict
from datetime import datetime
import random
from core.models import (
    MonitoringConfig, MonitoringConfigCreate, MonitoringAlert, MonitoringAlertCreate,
    MonitoringMetrics, MonitoringReport
)

# In-memory storage
_monitoring_configs: Dict[int, MonitoringConfig] = {}
_monitoring_alerts: Dict[int, MonitoringAlert] = {}
_alert_triggers: List[Dict] = []
_config_counter = 1
_alert_counter = 1


# Monitoring Config functions
def create_monitoring_config(data: MonitoringConfigCreate) -> MonitoringConfig:
    global _config_counter
    config = MonitoringConfig(
        id=_config_counter,
        deployment_id=data.deployment_id,
        enabled=True,
        check_interval=data.check_interval,
        metrics_to_collect=data.metrics_to_collect,
        retention_days=data.retention_days,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    _monitoring_configs[_config_counter] = config
    _config_counter += 1
    return config


def get_monitoring_config(deployment_id: int) -> Optional[MonitoringConfig]:
    for config in _monitoring_configs.values():
        if config.deployment_id == deployment_id:
            return config
    return None


def get_all_monitoring_configs() -> List[MonitoringConfig]:
    return list(_monitoring_configs.values())


# Monitoring Alert functions
def create_alert(data: MonitoringAlertCreate) -> MonitoringAlert:
    global _alert_counter
    alert = MonitoringAlert(
        id=_alert_counter,
        deployment_id=data.deployment_id,
        metric=data.metric,
        threshold=data.threshold,
        comparison=data.comparison,
        enabled=True,
        created_at=datetime.now()
    )
    _monitoring_alerts[_alert_counter] = alert
    _alert_counter += 1
    return alert


def get_alert(alert_id: int) -> Optional[MonitoringAlert]:
    return _monitoring_alerts.get(alert_id)


def get_alerts_by_deployment(deployment_id: int) -> List[MonitoringAlert]:
    return [a for a in _monitoring_alerts.values() if a.deployment_id == deployment_id]


def delete_alert(alert_id: int) -> bool:
    if alert_id in _monitoring_alerts:
        del _monitoring_alerts[alert_id]
        return True
    return False


# Monitoring Metrics (simulated)
def get_metrics(deployment_id: int) -> MonitoringMetrics:
    return MonitoringMetrics(
        deployment_id=deployment_id,
        cpu_usage=random.uniform(10, 80),
        memory_usage=random.uniform(30, 70),
        disk_usage=random.uniform(20, 60),
        request_count=random.randint(1000, 50000),
        error_count=random.randint(0, 100),
        response_time_ms=random.uniform(50, 500),
        uptime_percentage=99.9 + random.uniform(-0.1, 0),
        last_check=datetime.now()
    )


# Alert Triggers (simulated)
def add_alert_trigger(deployment_id: int, metric: str, value: float, threshold: float):
    _alert_triggers.append({
        "deployment_id": deployment_id,
        "metric": metric,
        "value": value,
        "threshold": threshold,
        "triggered_at": datetime.now()
    })
    # Keep only last 100 triggers
    if len(_alert_triggers) > 100:
        _alert_triggers.pop(0)


def get_alert_triggers(deployment_id: int, limit: int = 50) -> List[Dict]:
    return [t for t in _alert_triggers if t["deployment_id"] == deployment_id][-limit:]


# Monitoring Report (simulated)
def generate_report(deployment_id: int, period: str) -> MonitoringReport:
    return MonitoringReport(
        deployment_id=deployment_id,
        period=period,
        summary={
            "avg_cpu": round(random.uniform(20, 60), 2),
            "avg_memory": round(random.uniform(30, 70), 2),
            "total_requests": random.randint(50000, 500000),
            "total_errors": random.randint(10, 1000),
            "uptime": 99.9
        },
        alerts_triggered=random.randint(0, 10),
        generated_at=datetime.now()
    )
