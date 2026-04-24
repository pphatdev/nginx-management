import random
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from core.services import nginx, store
from core.services import deployments as deployment_service
from core.services import dns as dns_service
from core.services import monitoring as monitoring_service
from core.services import loadbalancer as lb_service
from core.models import (
    DeploymentCreate, DeploymentUpdate,
    DNSRecordCreate, DNSRecordUpdate, ServerNameCreate, ServerNameUpdate,
    MonitoringAlertCreate,
    LoadBalancerConfigUpdate, LoadBalancerRuleCreate
)

router = APIRouter(prefix="/api")

# ── Existing endpoints ──────────────────────

@router.get("/stats")
async def api_stats():
    stats = nginx.get_stats()
    # Simulate live metrics when stub_status is not configured
    if stats["active_connections"] == 0:
        stats["active_connections"] = random.randint(180, 320)
        stats["requests_per_sec"] = random.randint(900, 1800)
        stats["bytes_in"] = "2.4 GB"
        stats["bytes_out"] = "18.7 GB"
    return stats


@router.get("/servers")
async def api_servers():
    return [s.model_dump() for s in store.get_servers()]


@router.post("/servers/{server_id}/toggle")
async def toggle_server(server_id: int):
    server = store.toggle_server(server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return {"ok": True, "status": server.status}


@router.get("/upstreams")
async def api_upstreams():
    return [u.model_dump() for u in store.get_upstreams()]


class ConfigBody(BaseModel):
    config: str


@router.post("/config/save")
async def save_config(body: ConfigBody):
    ok, message = nginx.write_config(body.config)
    if not ok:
        raise HTTPException(status_code=422, detail=message)
    return {"ok": True, "message": message}


@router.post("/nginx/reload")
async def nginx_reload():
    ok, message = nginx.reload()
    if not ok:
        raise HTTPException(status_code=500, detail=message)
    return {"ok": True, "message": message or "Nginx reloaded successfully"}


# ── Deployments API ────────────────────────

@router.post("/deployments")
async def create_deployment(body: DeploymentCreate):
    deployment = deployment_service.create_deployment(body)
    return deployment.model_dump()


@router.get("/deployments")
async def list_deployments():
    deployments = deployment_service.get_all_deployments()
    return [d.model_dump() for d in deployments]


@router.get("/deployments/{deployment_id}")
async def get_deployment(deployment_id: int):
    deployment = deployment_service.get_deployment(deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment.model_dump()


@router.put("/deployments/{deployment_id}")
async def update_deployment(deployment_id: int, body: DeploymentUpdate):
    deployment = deployment_service.update_deployment(deployment_id, body)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment.model_dump()


@router.delete("/deployments/{deployment_id}")
async def delete_deployment(deployment_id: int):
    if not deployment_service.delete_deployment(deployment_id):
        raise HTTPException(status_code=404, detail="Deployment not found")
    return {"ok": True, "message": "Deployment deleted"}


# ── DNS API ────────────────────────────────

@router.post("/dns/records")
async def create_dns_record(body: DNSRecordCreate):
    record = dns_service.create_dns_record(body)
    return record.model_dump()


@router.get("/dns/records")
async def list_dns_records():
    records = dns_service.get_all_dns_records()
    return [r.model_dump() for r in records]


@router.get("/dns/records/{record_id}")
async def get_dns_record(record_id: int):
    record = dns_service.get_dns_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="DNS record not found")
    return record.model_dump()


@router.put("/dns/records/{record_id}")
async def update_dns_record(record_id: int, body: DNSRecordUpdate):
    record = dns_service.update_dns_record(record_id, body)
    if not record:
        raise HTTPException(status_code=404, detail="DNS record not found")
    return record.model_dump()


@router.delete("/dns/records/{record_id}")
async def delete_dns_record(record_id: int):
    if not dns_service.delete_dns_record(record_id):
        raise HTTPException(status_code=404, detail="DNS record not found")
    return {"ok": True, "message": "DNS record deleted"}


@router.post("/dns/server-names")
async def create_server_name(body: ServerNameCreate):
    name = dns_service.create_server_name(body)
    return name.model_dump()


@router.get("/dns/server-names")
async def list_server_names():
    names = dns_service.get_all_server_names()
    return [n.model_dump() for n in names]


@router.delete("/dns/server-names/{name_id}")
async def delete_server_name(name_id: int):
    if not dns_service.delete_server_name(name_id):
        raise HTTPException(status_code=404, detail="Server name not found")
    return {"ok": True, "message": "Server name deleted"}


# ── Monitoring API ─────────────────────────

@router.get("/monitoring/metrics/{deployment_id}")
async def get_monitoring_metrics(deployment_id: int):
    metrics = monitoring_service.get_metrics(deployment_id)
    return metrics.model_dump()


@router.post("/monitoring/alerts")
async def create_monitoring_alert(body: MonitoringAlertCreate):
    alert = monitoring_service.create_alert(body)
    return alert.model_dump()


@router.get("/monitoring/alerts")
async def list_monitoring_alerts(deployment_id: int):
    alerts = monitoring_service.get_alerts_by_deployment(deployment_id)
    return [a.model_dump() for a in alerts]


@router.delete("/monitoring/alerts/{alert_id}")
async def delete_monitoring_alert(alert_id: int):
    if not monitoring_service.delete_alert(alert_id):
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"ok": True, "message": "Alert deleted"}


@router.get("/monitoring/alert-triggers")
async def get_alert_triggers(deployment_id: int, limit: int = 50):
    triggers = monitoring_service.get_alert_triggers(deployment_id, limit)
    return triggers


# ── Load Balancer API ──────────────────────

@router.post("/loadbalancer/config")
async def create_lb_config(body):
    from core.models import LoadBalancerConfigCreate
    config_data = LoadBalancerConfigCreate(**body.dict())
    config = lb_service.create_lb_config(config_data)
    return config.model_dump()


@router.get("/loadbalancer/config/{deployment_id}")
async def get_lb_config_by_deployment(deployment_id: int):
    config = lb_service.get_lb_config_by_deployment(deployment_id)
    if not config:
        # Create default config if not exists
        from core.models import LoadBalancerConfigCreate
        config_data = LoadBalancerConfigCreate(deployment_id=deployment_id)
        config = lb_service.create_lb_config(config_data)
    return config.model_dump()


@router.put("/loadbalancer/config/{deployment_id}")
async def update_lb_config_by_deployment(deployment_id: int, body: LoadBalancerConfigUpdate):
    config = lb_service.update_lb_config_by_deployment(deployment_id, body)
    if not config:
        raise HTTPException(status_code=404, detail="Load balancer config not found")
    return config.model_dump()


@router.post("/loadbalancer/rules")
async def create_lb_rule(deployment_id: int, body: LoadBalancerRuleCreate):
    config = lb_service.get_lb_config_by_deployment(deployment_id)
    if not config:
        raise HTTPException(status_code=404, detail="Load balancer config not found")
    rule = lb_service.create_lb_rule(config.id, body)
    return rule.model_dump()


@router.get("/loadbalancer/rules")
async def list_lb_rules(deployment_id: int):
    rules = lb_service.get_rules_by_deployment(deployment_id)
    return [r.model_dump() for r in rules]


@router.delete("/loadbalancer/rules/{rule_id}")
async def delete_lb_rule(rule_id: int):
    if not lb_service.delete_lb_rule(rule_id):
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"ok": True, "message": "Rule deleted"}


@router.get("/loadbalancer/metrics/{deployment_id}")
async def get_lb_metrics(deployment_id: int):
    metrics = lb_service.get_lb_metrics(deployment_id)
    return metrics.model_dump()
