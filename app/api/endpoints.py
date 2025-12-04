from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.services.airtable import AirtableService
from app import schemas, models
from app.database import get_db
from app.models import SyncResponse, AirtableRecordResponse

router = APIRouter(tags=["sync"])
logger = logging.getLogger(__name__)

@router.post("/sync/{table_name}", response_model=SyncResponse)
async def sync_table(table_name: str, db: Session = Depends(get_db)):
    """Sync data from Airtable table to local database"""
    try:
        service = AirtableService()
        result = await service.sync_table(table_name)
        
        # Store in database (simplified - you'll need to implement this)
        saved_count = 0
        for record in result["records"]:
           
            existing = db.query(schemas.AirtableRecord).filter(
                schemas.AirtableRecord.record_id == record["id"]
            ).first()
            
            if not existing:
                db_record = schemas.AirtableRecord(
                    table_name=table_name,
                    record_id=record["id"],
                    data=record.get("fields", {})  # CHANGE THIS
                    )
                db.add(db_record)
                saved_count += 1
        
        db.commit()
        
        return SyncResponse(
            status="success",
            synced_count=saved_count,
            message=f"Synced {saved_count} records from '{table_name}'",
            table_name=table_name
        )
        
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/records", response_model=List[AirtableRecordResponse])
async def get_records(
    table_name: Optional[str] = Query(None, description="Filter by table name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),

    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: Optional[str] = Query(None, description="Sort order: asc or desc"),

    db: Session = Depends(get_db)
):
    # Real default values if function is called internally
    sort_by = sort_by or "id"
    sort_order = sort_order or "desc"

    query = db.query(schemas.AirtableRecord)

    if table_name:
        query = query.filter(schemas.AirtableRecord.table_name == table_name)

    sort_col = getattr(schemas.AirtableRecord, sort_by, None)
    if sort_col is not None:
        query = query.order_by(sort_col.desc() if sort_order.lower() == "desc" else sort_col.asc())

    records = query.offset(skip).limit(limit).all()

    return [AirtableRecordResponse.from_orm(record) for record in records]

@router.get("/records/{record_id}")
async def get_record(record_id: str, db: Session = Depends(get_db)):
    """Get a specific record by ID"""
    record = db.query(schemas.AirtableRecord).filter(
        schemas.AirtableRecord.record_id == record_id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return AirtableRecordResponse.from_orm(record)


# -------------------------------
# Explicit endpoints for People & Tasks
# -------------------------------
@router.get("/people", response_model=List[AirtableRecordResponse])
async def get_people(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return await get_records(
        table_name="people",
        skip=skip,
        limit=limit,
        sort_by="id",
        sort_order="desc",
        db=db
    )


@router.get("/tasks", response_model=List[AirtableRecordResponse])
async def get_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return await get_records(
        table_name="tasks",
        skip=skip,
        limit=limit,
        sort_by="id",
        sort_order="desc",
        db=db
    )
