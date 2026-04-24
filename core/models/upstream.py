from typing import Literal, List
from pydantic import BaseModel


class Backend(BaseModel):
    address: str
    weight: int
    status: Literal["up", "down"]


class Upstream(BaseModel):
    id: int
    name: str
    method: Literal["round_robin", "least_conn", "ip_hash"]
    backends: List[Backend]
