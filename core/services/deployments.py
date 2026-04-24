from typing import List, Optional, Dict, Any
from datetime import datetime
from core.models import Deployment, DeploymentCreate, DeploymentUpdate, DeploymentConfig

# In-memory storage for deployments (replace with database in production)
_deployments: Dict[int, Deployment] = {}
_deployment_counter = 1


def create_deployment(data: DeploymentCreate) -> Deployment:
    global _deployment_counter
    deployment = Deployment(
        id=_deployment_counter,
        name=data.name,
        project_type=data.project_type,
        service_type=data.service_type,
        domain=data.domain,
        status="active",
        config=data.config,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    _deployments[_deployment_counter] = deployment
    _deployment_counter += 1
    return deployment


def get_deployment(deployment_id: int) -> Optional[Deployment]:
    return _deployments.get(deployment_id)


def get_all_deployments() -> List[Deployment]:
    return list(_deployments.values())


def update_deployment(deployment_id: int, data: DeploymentUpdate) -> Optional[Deployment]:
    deployment = _deployments.get(deployment_id)
    if not deployment:
        return None
    
    update_data = data.model_dump(exclude_unset=True)
    updated = deployment.model_copy(update={
        **update_data,
        "updated_at": datetime.now()
    })
    _deployments[deployment_id] = updated
    return updated


def delete_deployment(deployment_id: int) -> bool:
    if deployment_id in _deployments:
        del _deployments[deployment_id]
        return True
    return False
