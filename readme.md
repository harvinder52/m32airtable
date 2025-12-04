# Airtable Integration Service

A FastAPI service that syncs Airtable data to a local database with webhook support.

## Features
- Sync Airtable tables to local SQLite database
- Handle pagination and rate limiting
- Webhook endpoint for real-time updates
- REST API to query synced data
- Exponential backoff retry logic

## Setup

1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate