from typing import List, Optional, Dict, Any
from datetime import datetime
import random
from core.models import (
    LoadBalancerConfig, LoadBalancerConfigCreate, LoadBalancerConfigUpdate,
    LoadBalancerRule, LoadBalancerRuleCreate, LoadBalancerRuleUpdate,
    LoadBalancerMetrics, LoadBalancerInstance
)

# In-memory storage
_lb_configs: Dict[int, LoadBalancerConfig] = {}
_lb_rules: Dict[int, LoadBalancerRule] = {}
_config_counter = 1
_rule_counter = 1


# Load Balancer Config functions
def create_lb_config(data: LoadBalancerConfigCreate) -> LoadBalancerConfig:
    global _config_counter
    config = LoadBalancerConfig(
        id=_config_counter,
        deployment_id=data.deployment_id,
        algorithm=data.algorithm,
        enabled=True,
        rules=[],
        session_persistence=data.session_persistence,
        session_timeout=data.session_timeout,
        health_check_enabled=data.health_check_enabled,
        health_check_interval=data.health_check_interval,
        health_check_path=data.health_check_path,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    _lb_configs[_config_counter] = config
    _config_counter += 1
    return config


def get_lb_config(config_id: int) -> Optional[LoadBalancerConfig]:
    return _lb_configs.get(config_id)


def get_lb_config_by_deployment(deployment_id: int) -> Optional[LoadBalancerConfig]:
    for config in _lb_configs.values():
        if config.deployment_id == deployment_id:
            return config
    return None


def update_lb_config(config_id: int, data: LoadBalancerConfigUpdate) -> Optional[LoadBalancerConfig]:
    config = _lb_configs.get(config_id)
    if not config:
        return None
    
    update_data = data.model_dump(exclude_unset=True)
    updated = config.model_copy(update={
        **update_data,
        "updated_at": datetime.now()
    })
    _lb_configs[config_id] = updated
    return updated


def update_lb_config_by_deployment(deployment_id: int, data: LoadBalancerConfigUpdate) -> Optional[LoadBalancerConfig]:
    config = get_lb_config_by_deployment(deployment_id)
    if not config:
        return None
    return update_lb_config(config.id, data)


# Load Balancer Rule functions
def create_lb_rule(config_id: int, data: LoadBalancerRuleCreate) -> LoadBalancerRule:
    global _rule_counter
    rule = LoadBalancerRule(
        id=_rule_counter,
        name=data.name,
        condition=data.condition,
        action=data.action,
        enabled=True,
        order=data.order
    )
    _lb_rules[_rule_counter] = rule
    
    # Add rule to config
    config = _lb_configs.get(config_id)
    if config:
        config.rules.append(rule)
    
    _rule_counter += 1
    return rule


def get_lb_rule(rule_id: int) -> Optional[LoadBalancerRule]:
    return _lb_rules.get(rule_id)


def get_rules_by_deployment(deployment_id: int) -> List[LoadBalancerRule]:
    config = get_lb_config_by_deployment(deployment_id)
    if not config:
        return []
    return config.rules


def update_lb_rule(rule_id: int, data: LoadBalancerRuleUpdate) -> Optional[LoadBalancerRule]:
    rule = _lb_rules.get(rule_id)
    if not rule:
        return None
    
    update_data = data.model_dump(exclude_unset=True)
    updated = rule.model_copy(update=update_data)
    _lb_rules[rule_id] = updated
    return updated


def delete_lb_rule(rule_id: int) -> bool:
    rule = _lb_rules.get(rule_id)
    if not rule:
        return False
    
    # Remove from configs
    for config in _lb_configs.values():
        config.rules = [r for r in config.rules if r.id != rule_id]
    
    del _lb_rules[rule_id]
    return True


# Load Balancer Metrics (simulated)
def get_lb_metrics(deployment_id: int) -> LoadBalancerMetrics:
    instances = [
        LoadBalancerInstance(
            address="192.168.1.10",
            port=3000,
            weight=1,
            status=random.choice(["up", "up", "up", "down"]),
            active_connections=random.randint(10, 100),
            total_requests=random.randint(1000, 10000)
        ),
        LoadBalancerInstance(
            address="192.168.1.11",
            port=3000,
            weight=1,
            status=random.choice(["up", "up", "up", "down"]),
            active_connections=random.randint(10, 100),
            total_requests=random.randint(1000, 10000)
        ),
        LoadBalancerInstance(
            address="192.168.1.12",
            port=3000,
            weight=1,
            status="up",
            active_connections=random.randint(10, 100),
            total_requests=random.randint(1000, 10000)
        ),
    ]
    
    total_requests = sum(i.total_requests for i in instances)
    active_connections = sum(i.active_connections for i in instances)
    
    return LoadBalancerMetrics(
        deployment_id=deployment_id,
        total_requests=total_requests,
        requests_per_sec=round(total_requests / 60, 2),
        active_connections=active_connections,
        connection_errors=random.randint(0, 50),
        average_response_time_ms=round(random.uniform(50, 300), 2),
        instances=instances,
        last_updated=datetime.now()
    )
