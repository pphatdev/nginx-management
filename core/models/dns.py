from typing import Literal, Optional
from pydantic import BaseModel
from datetime import datetime


class DNSRecord(BaseModel):
    id: int
    domain: str
    record_type: Literal["A", "AAAA", "CNAME", "MX", "TXT", "NS"]
    name: str
    value: str
    ttl: int
    status: Literal["active", "inactive"]
    created_at: datetime
    updated_at: datetime


class DNSRecordCreate(BaseModel):
    domain: str
    record_type: Literal["A", "AAAA", "CNAME", "MX", "TXT", "NS"]
    name: str
    value: str
    ttl: int = 3600


class DNSRecordUpdate(BaseModel):
    value: Optional[str] = None
    ttl: Optional[int] = None
    status: Optional[Literal["active", "inactive"]] = None


class ServerName(BaseModel):
    id: int
    domain: str
    server_ip: str
    custom_name: str
    status: Literal["configured", "pending", "failed"]
    created_at: datetime
    updated_at: datetime


class ServerNameCreate(BaseModel):
    domain: str
    server_ip: str
    custom_name: str


class ServerNameUpdate(BaseModel):
    custom_name: Optional[str] = None
    status: Optional[Literal["configured", "pending", "failed"]] = None
