from fastapi import FastAPI

from leadbot.ai import build_ai_provider
from leadbot.classifier import LeadClassifier
from leadbot.config import load_product_catalog, load_settings
from leadbot.models import IncomingMessage, WebhookResponse
from leadbot.notifications import InMemoryWhatsAppGateway, LeadNotifier
from leadbot.repository import LeadRepository
from leadbot.services import MessageProcessor


def create_app() -> FastAPI:
    settings = load_settings()
    gateway = InMemoryWhatsAppGateway()
    repository = LeadRepository(settings.database_url)
    classifier = LeadClassifier(load_product_catalog(settings.product_catalog_path))
    processor = MessageProcessor(
        ai_provider=build_ai_provider(settings),
        classifier=classifier,
        notifier=LeadNotifier(gateway=gateway, admin_phone=settings.admin_phone),
        repository=repository,
    )

    app = FastAPI(title="LeadBot")

    @app.on_event("startup")
    async def startup() -> None:
        await repository.init()

    @app.post("/webhook", response_model=WebhookResponse)
    async def webhook(payload: IncomingMessage) -> WebhookResponse:
        return await processor.process(payload)

    app.state.gateway = gateway
    app.state.repository = repository
    app.state.processor = processor
    app.state.settings = settings
    return app


app = create_app()
