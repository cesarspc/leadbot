# leadbot

Lead classifier for ecommerce stores.

## Features
- FastAPI async webhook endpoint (`POST /webhook`) for incoming WhatsApp messages
- Modular components for AI provider, lead classification, persistence, and notifications
- Environment-driven configuration for store data, AI provider/model/API key, and admin phone
- SQLite persistence for all processed interactions and lead classifications
- Admin WhatsApp notification for high-quality leads with confidence and message context

## Configuration
Set environment variables as needed:
- `STORE_NAME`, `BRAND_INFO`, `SUPPORT_CONTACT`
- `AI_PROVIDER`, `AI_API_KEY`, `AI_MODEL`
- `ADMIN_PHONE`
- `DATABASE_URL` (default `sqlite:///leadbot.db`)
- `PRODUCT_CATALOG_PATH` (default `config/products.json`)

## Run
```bash
pip install -r requirements.txt
uvicorn leadbot.main:app --reload
```
