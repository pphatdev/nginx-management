from typing import Literal
from pydantic import BaseModel


class Server(BaseModel):
    id: int
    name: str
    port: int
    ssl: bool
    status: Literal["active", "inactive"]
    upstream: str
