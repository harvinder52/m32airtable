from sqlalchemy import Column, Integer, String, JSON, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class AirtableRecord(Base):
    __tablename__ = "airtable_records"
    
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, index=True)  # e.g., "Contacts", "Deals"
    record_id = Column(String, unique=True, index=True)  # Airtable's record ID
    data = Column(JSON)  # Full record data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True)
    event_type = Column(String, index=True)
    payload = Column(JSON)
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Integer, default=0)  # 0 = not processed, 1 = processed