import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Settings:
    store_name: str
    brand_info: str
    support_contact: str
    admin_phone: str
    ai_provider: str
    ai_api_key: str
    ai_model: str
    database_url: str
    product_catalog_path: str


def load_settings() -> Settings:
    return Settings(
        store_name=os.getenv("STORE_NAME", "LeadBot Store"),
        brand_info=os.getenv("BRAND_INFO", "Online store"),
        support_contact=os.getenv("SUPPORT_CONTACT", "support@example.com"),
        admin_phone=os.getenv("ADMIN_PHONE", ""),
        ai_provider=os.getenv("AI_PROVIDER", "heuristic"),
        ai_api_key=os.getenv("AI_API_KEY", ""),
        ai_model=os.getenv("AI_MODEL", "default"),
        database_url=os.getenv("DATABASE_URL", "sqlite:///leadbot.db"),
        product_catalog_path=os.getenv("PRODUCT_CATALOG_PATH", "config/products.json"),
    )


def load_product_catalog(path: str) -> list[dict]:
    catalog_path = Path(path)
    if not catalog_path.exists():
        return []
    with catalog_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data if isinstance(data, list) else []
