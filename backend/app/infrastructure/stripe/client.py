import stripe as stripe_lib

from app.core.config import settings
from app.infrastructure.stripe.exceptions import CardDeclinedError, StripeError


class StripeClient:
    def __init__(self) -> None:
        stripe_lib.api_key = settings.STRIPE_SECRET_KEY

    def create_customer(self, *, email: str, name: str) -> dict:
        try:
            return stripe_lib.Customer.create(email=email, name=name)  # type: ignore[return-value]
        except stripe_lib.StripeError as exc:
            raise StripeError(detail=str(exc)) from exc

    def create_payment_intent(
        self,
        *,
        amount: int,
        currency: str,
        customer_id: str,
        metadata: dict | None = None,
    ) -> dict:
        try:
            return stripe_lib.PaymentIntent.create(  # type: ignore[return-value]
                amount=amount,
                currency=currency,
                customer=customer_id,
                metadata=metadata or {},
            )
        except stripe_lib.CardError:
            raise CardDeclinedError()
        except stripe_lib.StripeError as exc:
            raise StripeError(detail=str(exc)) from exc

    def retrieve_payment_intent(self, payment_intent_id: str) -> dict:
        try:
            return stripe_lib.PaymentIntent.retrieve(payment_intent_id)  # type: ignore[return-value]
        except stripe_lib.StripeError as exc:
            raise StripeError(detail=str(exc)) from exc

    def refund_payment_intent(self, payment_intent_id: str) -> dict:
        try:
            return stripe_lib.Refund.create(payment_intent=payment_intent_id)  # type: ignore[return-value]
        except stripe_lib.StripeError as exc:
            raise StripeError(detail=str(exc)) from exc
