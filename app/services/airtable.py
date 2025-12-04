import httpx
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

class AirtableService:
    def __init__(self):
        self.api_key = settings.AIRTABLE_API_KEY
        self.base_id = settings.AIRTABLE_BASE_ID
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}"
        
    @retry(
        retry=retry_if_exception_type(httpx.HTTPError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def get_records(self, table_name: str, offset: str = None) -> Dict[str, Any]:
        """Fetch records from Airtable with retry and pagination"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        params = {}
        if offset:
            params["offset"] = offset
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/{table_name}",
                    headers=headers,
                    params=params
                )
                
                # Rate limit handling
                if response.status_code == 429:
                    logger.warning("Rate limit hit, retrying...")
                    raise httpx.HTTPError("Rate limit exceeded")
                
                response.raise_for_status()

                logger.info(
                    f"Fetched batch: table={table_name}, "
                    f"records={len(response.json().get('records', []))}, "
                    f"offset={offset}"
                )

                return response.json()
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error fetching records from {table_name}: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error fetching records: {e}")
                raise
    
    async def sync_table(self, table_name: str) -> Dict[str, Any]:
        """Fetch all pages and return full dataset"""
        all_records = []
        offset = None
        
        while True:
            data = await self.get_records(table_name, offset)
            records = data.get("records", [])
            all_records.extend(records)
            
            offset = data.get("offset")

            if not offset:
                break
        
        logger.info(
            f"Sync completed: table={table_name}, total_records={len(all_records)}"
        )

        return {
            "table_name": table_name,
            "records": all_records,
            "total_count": len(all_records)
        }
