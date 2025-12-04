from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from app.api.endpoints import router as api_router
from app.api.webhooks import router as webhook_router
from app.database import engine, Base
from app.config import settings
from app.logger import setup_logging

setup_logging()

# Create tables
Base.metadata.create_all(bind=engine)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Airtable Integration Service")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created/verified")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down service")

app = FastAPI(
    title="Airtable Integration Service",
    description="Sync Airtable data to local database with webhook support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(webhook_router, prefix="/webhooks")

@app.get("/")
async def root():
    return {
        "service": "Airtable Integration Service",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "sync": "/api/v1/sync/{table_name}",
            "records": "/api/v1/records",
            "webhook": "/webhooks/airtable"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "airtable-integration",
        "timestamp": "2024-01-15T10:30:00Z"  # You'd use datetime.utcnow() in real code
    }