from leadbot.ai import AIProvider
from leadbot.classifier import LeadClassifier
from leadbot.models import IncomingMessage, WebhookResponse
from leadbot.notifications import LeadNotifier
from leadbot.repository import InteractionRecord, LeadRepository


class MessageProcessor:
    def __init__(
        self,
        ai_provider: AIProvider,
        classifier: LeadClassifier,
        notifier: LeadNotifier,
        repository: LeadRepository,
    ) -> None:
        self.ai_provider = ai_provider
        self.classifier = classifier
        self.notifier = notifier
        self.repository = repository

    async def process(self, inbound: IncomingMessage) -> WebhookResponse:
        analyzed = await self.ai_provider.analyze(inbound.message)
        classification = self.classifier.classify(analyzed)
        reply = self._build_reply(classification.quality)

        await self.repository.save(
            InteractionRecord(
                phone_number=inbound.phone_number,
                inbound_message=inbound.message,
                bot_reply=reply,
                classification=classification,
            )
        )
        await self.notifier.notify_if_high_quality(
            phone_number=inbound.phone_number,
            message=inbound.message,
            confidence=classification.confidence,
            quality=classification.quality,
        )
        return WebhookResponse(reply=reply, classification=classification)

    def _build_reply(self, quality: str) -> str:
        if quality == "high":
            return "Great! A specialist will contact you shortly to complete your purchase."
        return "Thanks for your message! Share your product, budget, and timeline so we can help faster."
