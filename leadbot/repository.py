import asyncio
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

from leadbot.models import LeadClassification


@dataclass(slots=True)
class InteractionRecord:
    phone_number: str
    inbound_message: str
    bot_reply: str
    classification: LeadClassification


class LeadRepository:
    def __init__(self, database_url: str) -> None:
        if not database_url.startswith("sqlite:///"):
            raise ValueError("Only sqlite:/// URLs are supported")
        self.database_path = database_url.removeprefix("sqlite:///")

    async def init(self) -> None:
        await asyncio.to_thread(self._init_sync)

    def _init_sync(self) -> None:
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT NOT NULL,
                    inbound_message TEXT NOT NULL,
                    bot_reply TEXT NOT NULL,
                    lead_quality TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    async def save(self, record: InteractionRecord) -> None:
        await asyncio.to_thread(self._save_sync, record)

    def _save_sync(self, record: InteractionRecord) -> None:
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                INSERT INTO interactions (
                    phone_number,
                    inbound_message,
                    bot_reply,
                    lead_quality,
                    confidence,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record.phone_number,
                    record.inbound_message,
                    record.bot_reply,
                    record.classification.quality,
                    record.classification.confidence,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()
