from leadbot.models import OutgoingMessage


class WhatsAppGateway:
    async def send_message(self, message: OutgoingMessage) -> None:
        raise NotImplementedError


class InMemoryWhatsAppGateway(WhatsAppGateway):
    def __init__(self) -> None:
        self.sent_messages: list[OutgoingMessage] = []

    async def send_message(self, message: OutgoingMessage) -> None:
        self.sent_messages.append(message)


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
            f"Context: {message[:200]}"
        )
        await self.gateway.send_message(OutgoingMessage(to=self.admin_phone, body=body))
