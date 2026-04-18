import asyncio
import json
from urllib import request

from leadbot.models import OutgoingMessage

MAX_MESSAGE_PREVIEW_LENGTH = 200


class WhatsAppGateway:
    async def send_message(self, message: OutgoingMessage) -> None:
        raise NotImplementedError


class InMemoryWhatsAppGateway(WhatsAppGateway):
    def __init__(self) -> None:
        self.sent_messages: list[OutgoingMessage] = []

    async def send_message(self, message: OutgoingMessage) -> None:
        self.sent_messages.append(message)


class WebhookWhatsAppGateway(WhatsAppGateway):
    def __init__(self, api_url: str, api_token: str) -> None:
        self.api_url = api_url
        self.api_token = api_token

    async def send_message(self, message: OutgoingMessage) -> None:
        payload = json.dumps({"to": message.to, "body": message.body}).encode("utf-8")
        req = request.Request(
            self.api_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}",
            },
            method="POST",
        )
        await asyncio.to_thread(self._send_sync, req)

    def _send_sync(self, req: request.Request) -> None:
        with request.urlopen(req, timeout=10) as response:
            response.read()


class LeadNotifier:
    def __init__(self, gateway: WhatsAppGateway, admin_phone: str) -> None:
        self.gateway = gateway
        self.admin_phone = admin_phone

    async def notify_if_high_quality(self, phone_number: str, message: str, confidence: float, quality: str) -> None:
        if quality != "high" or not self.admin_phone:
            return
        body = (
            "🔥 High-quality lead detected\n"
            f"Prospect: {phone_number}\n"
            f"Confidence: {confidence}\n"
            f"Context: {message[:MAX_MESSAGE_PREVIEW_LENGTH]}"
        )
        await self.gateway.send_message(OutgoingMessage(to=self.admin_phone, body=body))
