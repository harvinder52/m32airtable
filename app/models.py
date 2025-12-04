from pydantic import BaseModel
from typing import Optional, Any, Dict, List
from datetime import datetime

class SyncResponse(BaseModel):
    status: str
    synced_count: int
    message: str
    table_name: Optional[str] = None

class AirtableRecordResponse(BaseModel):
    id: int
    table_name: str
    record_id: str
    data: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True  # For SQLAlchemy compatibility

class WebhookRequest(BaseModel):
    event: str
    timestamp: datetime
    payload: Dict[str, Any]

    