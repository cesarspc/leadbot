import asyncio
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from leadbot.main import create_app
from leadbot.models import IncomingMessage


class WebhookFlowTests(unittest.TestCase):
    PRODUCT_CATALOG = Path(__file__).resolve().parents[1] / "config" / "products.json"

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        os.environ["DATABASE_URL"] = f"sqlite:///{self.db_path}"
        os.environ["ADMIN_PHONE"] = "5511999999999"
        os.environ["AI_PROVIDER"] = "heuristic"
        os.environ["PRODUCT_CATALOG_PATH"] = str(self.PRODUCT_CATALOG)
        os.environ.pop("WHATSAPP_API_URL", None)
        os.environ.pop("WHATSAPP_API_TOKEN", None)
        self.app = create_app()
        asyncio.run(self.app.state.repository.init())

    def tearDown(self) -> None:
        self.temp_dir.cleanup()
        for key in ["DATABASE_URL", "ADMIN_PHONE", "AI_PROVIDER", "PRODUCT_CATALOG_PATH", "WHATSAPP_API_URL", "WHATSAPP_API_TOKEN"]:
            os.environ.pop(key, None)

    def _load_interactions(self) -> list[tuple]:
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute(
                """
                SELECT phone_number, inbound_message, lead_quality, confidence
                FROM interactions
                ORDER BY id ASC
                """
            ).fetchall()

    def test_high_quality_message_notifies_admin(self) -> None:
        inbound = IncomingMessage(phone_number="5511988887777", message="I want to buy a Smart TV 55 today, budget is 3500")

        response = asyncio.run(self.app.state.processor.process(inbound))

        self.assertEqual(response.classification.quality, "high")
        self.assertGreaterEqual(response.classification.confidence, 0.75)
        self.assertEqual(len(self.app.state.gateway.sent_messages), 1)
        self.assertIn("5511988887777", self.app.state.gateway.sent_messages[0].body)
        self.assertEqual(
            self._load_interactions(),
            [("5511988887777", "I want to buy a Smart TV 55 today, budget is 3500", "high", response.classification.confidence)],
        )

    def test_low_quality_message_does_not_notify_admin(self) -> None:
        inbound = IncomingMessage(phone_number="5511977776666", message="Hello, good morning")

        response = asyncio.run(self.app.state.processor.process(inbound))

        self.assertEqual(response.classification.quality, "low")
        self.assertEqual(len(self.app.state.gateway.sent_messages), 0)
        self.assertEqual(
            self._load_interactions(),
            [("5511977776666", "Hello, good morning", "low", response.classification.confidence)],
        )


if __name__ == "__main__":
    unittest.main()
