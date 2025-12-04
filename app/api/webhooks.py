from fastapi import APIRouter, Request, HTTPException, Header, Depends
import hashlib
import hmac
import json
import logging
from sqlalchemy.orm import Session


from app.database import get_db
import app.schemas as schemas
from app.config import settings
from app.models import WebhookRequest


router = APIRouter(tags=["webhooks"])
logger = logging.getLogger(__name__)

@router.post("/airtable-webhook")
async def airtable_webhook(
    request: WebhookRequest,
    db: Session = Depends(get_db),
    x_airtable_webhook_signature: str = Header(None),
    x_airtable_webhook_timestamp: str = Header(None)
):
    """Receive webhooks from Airtable"""
    try:
        # Get raw body
        body = await request.body()
        payload = await request.json()
        
        # Validate signature if secret is set
        if settings.WEBHOOK_SECRET:
            if not x_airtable_webhook_signature or not x_airtable_webhook_timestamp:
                raise HTTPException(status_code=400, detail="Missing signature headers")
            
            is_valid = validate_signature(
                body,
                x_airtable_webhook_signature,
                x_airtable_webhook_timestamp,
                settings.WEBHOOK_SECRET
            )
            
            if not is_valid:
                raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Store webhook event
        webhook_event = schemas.WebhookEvent(
            event_id=f"{x_airtable_webhook_timestamp}_{hashlib.md5(body).hexdigest()[:8]}",
            event_type=payload.get("base", {}).get("id", "unknown"),
            payload=payload
        )
        
        db.add(webhook_event)
        db.commit()
        
        logger.info(f"Received webhook: {webhook_event.event_type}")
        
        # Here you could process the webhook to update your local data
        # For now, just log it
        process_airtable_changes(payload, db)
        return {"status": "received"}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Webhook error: {repr(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def process_airtable_changes(payload: dict, db: Session):
    """
    Take Airtable webhook payload and update local AirtableRecord table.
    Idempotent: does not duplicate on repeated webhook triggers.
    """

    changed = payload.get("changedTablesById", {})
    for table_id, changes in changed.items():

        # Handle ADDED RECORDS
        for rec in changes.get("addedRecords", []):
            record_id = rec["id"]
            fields = rec.get("current", {})

            existing = db.query(schemas.AirtableRecord).filter(
                schemas.AirtableRecord.record_id == record_id
            ).first()

            if not existing:
                new_record = schemas.AirtableRecord(
                    table_name=table_id,
                    record_id=record_id,
                    data=fields
                )
                db.add(new_record)

        # Handle UPDATED RECORDS
        for rec in changes.get("updatedRecords", []):
            record_id = rec["id"]
            fields = rec.get("current", {})

            existing = db.query(schemas.AirtableRecord).filter(
                schemas.AirtableRecord.record_id == record_id
            ).first()

            if existing and existing.data != fields:
                existing.data = fields

        # Handle DELETED RECORDS
        for record_id in changes.get("deletedRecords", []):
            existing = db.query(schemas.AirtableRecord).filter(
                schemas.AirtableRecord.record_id == record_id
            ).first()

            if existing:
                db.delete(existing)

    db.commit()

def validate_signature(
    body: bytes,
    signature: str,
    timestamp: str,
    secret: str
) -> bool:
    """Validate Airtable webhook signature"""
    message = timestamp.encode() + body
    expected_signature = hmac.new(
        secret.encode(),
        message,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)