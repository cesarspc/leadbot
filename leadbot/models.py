from typing import Literal

from pydantic import BaseModel, Field


class IncomingMessage(BaseModel):
    phone_number: str = Field(..., min_length=5)
    message: str = Field(..., min_length=1)


class LeadClassification(BaseModel):
    quality: Literal["high", "low"]
    confidence: float
    reason: str


class OutgoingMessage(BaseModel):
    to: str
    body: str


class WebhookResponse(BaseModel):
    reply: str
    classification: LeadClassification
