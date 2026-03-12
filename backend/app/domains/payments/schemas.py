from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.shared.enums import Currency, PaymentStatus


class PaymentCreate(BaseModel):
    amount: int
    currency: Currency = Currency.USD
    description: str | None = None


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    amount: int
    currency: Currency
    status: PaymentStatus
    stripe_payment_intent_id: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime


class WebhookEvent(BaseModel):
    """Stripe sends this shape in the event payload."""
    type: str
    data: dict
