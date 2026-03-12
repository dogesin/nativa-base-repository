from app.core.exceptions import NotFoundError
from app.domains.clients.repository import ClientRepository
from app.domains.payments.models import Payment
from app.domains.payments.repository import PaymentRepository
from app.domains.payments.schemas import PaymentCreate
from app.infrastructure.stripe.client import StripeClient
from app.shared.enums import PaymentStatus


class PaymentService:
    def __init__(
        self,
        repo: PaymentRepository,
        client_repo: ClientRepository,
        stripe: StripeClient,
    ):
        self.repo = repo
        self.client_repo = client_repo
        self.stripe = stripe

    def list_payments(self, client_id: int, skip: int = 0, limit: int = 100) -> list[Payment]:
        client = self.client_repo.get_by_id(client_id)
        if not client:
            raise NotFoundError(f"Client {client_id} not found")
        return self.repo.get_by_client(client_id, skip=skip, limit=limit)

    def get_payment(self, payment_id: int) -> Payment:
        payment = self.repo.get_by_id(payment_id)
        if not payment:
            raise NotFoundError(f"Payment {payment_id} not found")
        return payment

    def create_payment(self, client_id: int, data: PaymentCreate) -> Payment:
        client = self.client_repo.get_by_id(client_id)
        if not client:
            raise NotFoundError(f"Client {client_id} not found")
        if not client.stripe_customer_id:
            raise NotFoundError("Client has no Stripe customer record")

        intent = self.stripe.create_payment_intent(
            amount=data.amount,
            currency=data.currency.value,
            customer_id=client.stripe_customer_id,
            metadata={"client_id": str(client_id)},
        )

        return self.repo.create({
            "client_id": client_id,
            "amount": data.amount,
            "currency": data.currency,
            "description": data.description,
            "stripe_payment_intent_id": intent["id"],
            "status": PaymentStatus.PENDING,
        })

    def handle_webhook_event(self, event: dict) -> None:
        event_type = event.get("type", "")
        intent = event.get("data", {}).get("object", {})
        intent_id = intent.get("id")
        if not intent_id:
            return

        payment = self.repo.get_by_stripe_intent(intent_id)
        if not payment:
            return

        status_map = {
            "payment_intent.succeeded": PaymentStatus.SUCCEEDED,
            "payment_intent.payment_failed": PaymentStatus.FAILED,
            "payment_intent.canceled": PaymentStatus.CANCELED,
        }

        new_status = status_map.get(event_type)
        if new_status:
            self.repo.update_status(payment.id, new_status)
