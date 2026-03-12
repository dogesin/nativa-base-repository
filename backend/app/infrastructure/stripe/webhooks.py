import stripe as stripe_lib

from app.core.config import settings
from app.infrastructure.stripe.exceptions import InvalidWebhookSignatureError


def verify_webhook(payload: bytes, sig_header: str) -> dict:
    try:
        event = stripe_lib.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        return event  # type: ignore[return-value]
    except (ValueError, stripe_lib.SignatureVerificationError) as exc:
        raise InvalidWebhookSignatureError() from exc
