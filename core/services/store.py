"""
In-memory data store — demo/prototype layer.
Replace with a database-backed repository when ready for persistent storage.
"""
from typing import List, Optional

from core.models.server import Server
from core.models.upstream import Backend, Upstream

_servers: List[Server] = [
    Server(id=1, name="api.example.com",    port=443, ssl=True,  status="active",   upstream="api_pool"),
    Server(id=2, name="www.example.com",    port=80,  ssl=False, status="active",   upstream="web_pool"),
    Server(id=3, name="admin.example.com",  port=443, ssl=True,  status="inactive", upstream="admin_pool"),
    Server(id=4, name="static.example.com", port=80,  ssl=False, status="active",   upstream="static_pool"),
]

_upstreams: List[Upstream] = [
    Upstream(id=1, name="api_pool", method="round_robin", backends=[
        Backend(address="10.0.0.1:8001", weight=1, status="up"),
        Backend(address="10.0.0.2:8001", weight=1, status="up"),
        Backend(address="10.0.0.3:8001", weight=1, status="down"),
    ]),
    Upstream(id=2, name="web_pool", method="least_conn", backends=[
        Backend(address="10.0.1.1:3000", weight=2, status="up"),
        Backend(address="10.0.1.2:3000", weight=1, status="up"),
    ]),
    Upstream(id=3, name="admin_pool", method="ip_hash", backends=[
        Backend(address="10.0.2.1:9000", weight=1, status="up"),
    ]),
    Upstream(id=4, name="static_pool", method="round_robin", backends=[
        Backend(address="10.0.3.1:8080", weight=1, status="up"),
        Backend(address="10.0.3.2:8080", weight=1, status="up"),
    ]),
]


def get_servers() -> List[Server]:
    return _servers


def get_server(server_id: int) -> Optional[Server]:
    return next((s for s in _servers if s.id == server_id), None)


def toggle_server(server_id: int) -> Optional[Server]:
    server = get_server(server_id)
    if server is None:
        return None
    server.status = "inactive" if server.status == "active" else "active"
    return server


def get_upstreams() -> List[Upstream]:
    return _upstreams
