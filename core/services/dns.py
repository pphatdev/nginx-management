from typing import List, Optional, Dict
from datetime import datetime
from core.models import DNSRecord, DNSRecordCreate, DNSRecordUpdate, ServerName, ServerNameCreate, ServerNameUpdate

# In-memory storage
_dns_records: Dict[int, DNSRecord] = {}
_server_names: Dict[int, ServerName] = {}
_dns_counter = 1
_server_name_counter = 1


# DNS Records functions
def create_dns_record(data: DNSRecordCreate) -> DNSRecord:
    global _dns_counter
    record = DNSRecord(
        id=_dns_counter,
        domain=data.domain,
        record_type=data.record_type,
        name=data.name,
        value=data.value,
        ttl=data.ttl,
        status="active",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    _dns_records[_dns_counter] = record
    _dns_counter += 1
    return record


def get_dns_record(record_id: int) -> Optional[DNSRecord]:
    return _dns_records.get(record_id)


def get_all_dns_records() -> List[DNSRecord]:
    return list(_dns_records.values())


def update_dns_record(record_id: int, data: DNSRecordUpdate) -> Optional[DNSRecord]:
    record = _dns_records.get(record_id)
    if not record:
        return None
    
    update_data = data.model_dump(exclude_unset=True)
    updated = record.model_copy(update={
        **update_data,
        "updated_at": datetime.now()
    })
    _dns_records[record_id] = updated
    return updated


def delete_dns_record(record_id: int) -> bool:
    if record_id in _dns_records:
        del _dns_records[record_id]
        return True
    return False


# Server Names functions
def create_server_name(data: ServerNameCreate) -> ServerName:
    global _server_name_counter
    server_name = ServerName(
        id=_server_name_counter,
        domain=data.domain,
        server_ip=data.server_ip,
        custom_name=data.custom_name,
        status="configured",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    _server_names[_server_name_counter] = server_name
    _server_name_counter += 1
    return server_name


def get_server_name(name_id: int) -> Optional[ServerName]:
    return _server_names.get(name_id)


def get_all_server_names() -> List[ServerName]:
    return list(_server_names.values())


def update_server_name(name_id: int, data: ServerNameUpdate) -> Optional[ServerName]:
    server_name = _server_names.get(name_id)
    if not server_name:
        return None
    
    update_data = data.model_dump(exclude_unset=True)
    updated = server_name.model_copy(update={
        **update_data,
        "updated_at": datetime.now()
    })
    _server_names[name_id] = updated
    return updated


def delete_server_name(name_id: int) -> bool:
    if name_id in _server_names:
        del _server_names[name_id]
        return True
    return False
