# M32 Backend Integration Project – Airtable

## Overview
This project is a standalone backend microservice built with **FastAPI** that integrates with **Airtable**. It allows syncing records from Airtable to a local database, provides REST endpoints to access those records, and handles webhook events for real-time updates.  

The project mirrors real-world backend integration tasks: authentication, API communication, webhook handling, data persistence, and structured error handling.

---

## Features
- **Airtable API Integration**
  - Fetch records from Airtable tables.
  - Supports pagination and rate-limits with exponential backoff.
  - Idempotent syncing (avoids duplicates).

- **Webhook Handling**
  - Receive webhook events from Airtable when records are added, updated, or deleted.
  - Automatically updates the local database.

- **Local API**
  - REST endpoints to query records:
    - `/sync/{table_name}` – Sync a specific Airtable table.
    - `/records` – Get all records with optional filtering, sorting, and pagination.
    - `/records/{record_id}` – Get a single record by Airtable ID.
    - `/people` and `/tasks` – Explicit endpoints for common tables.

- **Error Handling**
  - Structured logging for sync and webhook processing.
  - Exponential backoff for API calls (via `tenacity`).
  - Proper handling of rate limits and upstream errors.

---

## Tech Stack
- **Python 3.12**
- **FastAPI** – Web framework
- **SQLAlchemy** – ORM for database
- **SQLite** – Local database (`integration.db`)
- **httpx** – Async HTTP client
- **tenacity** – Retry logic for API calls
- **Pydantic** – Data validation and serialization

---

## Project Structure
.
├── app/
│ ├── api/ # FastAPI route handlers (webhooks & records)
│ ├── services/ # Airtable service integration
│ ├── utils/ # Helper utilities (retry, logging)
│ ├── models.py # SQLAlchemy models
│ ├── schemas.py # Pydantic schemas
│ ├── config.py # Environment configuration
│ └── main.py # FastAPI app entrypoint
├── integration.db # SQLite database
├── requirements.txt # Python dependencies
└── README.md # This file

yaml
Copy code

---

## Setup

1. **Clone or download the repo**

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
Install dependencies

bash
Copy code
pip install -r requirements.txt
Environment Variables
Create a .env file in the root directory with:

env
Copy code
AIRTABLE_API_KEY=<your_airtable_api_key>
AIRTABLE_BASE_ID=<your_airtable_base_id>
WEBHOOK_SECRET=<your_webhook_secret>  # optional, for validating webhooks
Run the application

bash
Copy code
uvicorn app.main:app --reload
Swagger Documentation
Visit http://127.0.0.1:8000/docs to explore and test API endpoints.

Usage
Sync Table
bash
Copy code
POST /sync/{table_name}
Fetches all records from Airtable and stores them locally.

Handles pagination and idempotency.

Webhook
bash
Copy code
POST /airtable-webhook
Receives webhook events when Airtable records change.

Updates local database automatically.

JSON body example:

json
Copy code
{
  "event": "update",
  "timestamp": "2025-12-04T11:07:28.526Z",
  "payload": {
    "changedTablesById": {
      "tbl123": {
        "addedRecords": [{"id": "rec1", "current": {"Name": "John"}}],
        "updatedRecords": [{"id": "rec2", "current": {"Status": "Done"}}],
        "deletedRecords": ["rec3"]
      }
    }
  }
}
Query Records
/records?table_name=tasks&skip=0&limit=100&sort_by=created_at&sort_order=desc

/records/{record_id}

/people or /tasks for specific tables

Design Decisions
Async HTTP calls for efficient Airtable API communication.

Tenacity retry with exponential backoff to handle rate-limits.

Idempotent webhook processing to prevent duplicates.

SQLite chosen for simplicity and portability; can be swapped with PostgreSQL in production.

Separation of concerns: API routes, services, models, and utils are modular.

Deployment
Can be deployed on Railway, Render, or similar platforms.

Make sure your app is publicly accessible for Airtable webhooks.

Use .env for credentials in deployment.

Future Improvements
Implement OAuth2 flow for APIs that support it.

Add bidirectional sync (push updates back to Airtable).

Queue-based background sync for large datasets.

Unit and integration tests for core logic.

Dockerize the application.

License
MIT License
