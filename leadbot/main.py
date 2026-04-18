from contextlib import asynccontextmanager

from fastapi import FastAPI

from leadbot.ai import build_ai_provider
from leadbot.classifier import LeadClassifier
from leadbot.config import Settings, load_product_catalog, load_settings
from leadbot.models import IncomingMessage, WebhookResponse
from leadbot.notifications import InMemoryWhatsAppGateway, LeadNotifier, WhatsAppGateway, WebhookWhatsAppGateway
from leadbot.repository import LeadRepository
from leadbot.services import MessageProcessor


def _build_gateway(settings: Settings) -> WhatsAppGateway:
    if settings.whatsapp_api_url:
        return WebhookWhatsAppGateway(
            api_url=settings.whatsapp_api_url,
            api_token=settings.whatsapp_api_token,
        )
    return InMemoryWhatsAppGateway()


def create_app() -> FastAPI:
    settings = load_settings()
    gateway = _build_gateway(settings)
    repository = LeadRepository(settings.database_url)
    classifier = LeadClassifier(load_product_catalog(settings.product_catalog_path))
    processor = MessageProcessor(
        ai_provider=build_ai_provider(settings),
        classifier=classifier,
        notifier=LeadNotifier(gateway=gateway, admin_phone=settings.admin_phone),
        repository=repository,
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        await repository.init()
        yield

    app = FastAPI(title="LeadBot", lifespan=lifespan)

    @app.post("/webhook", response_model=WebhookResponse)
    async def webhook(payload: IncomingMessage) -> WebhookResponse:
        return await processor.process(payload)

    app.state.gateway = gateway
    app.state.repository = repository
    app.state.processor = processor
    app.state.settings = settings
    return app


app = create_app()
