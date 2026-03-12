from sqlalchemy.orm import Session

from app.domains.payments.models import Payment
from app.shared.base_repository import BaseRepository
from app.shared.enums import PaymentStatus


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, db: Session):
        super().__init__(Payment, db)

    def get_by_client(
        self, client_id: int, *, skip: int = 0, limit: int = 100
    ) -> list[Payment]:
        return (
            self.db.query(Payment)
            .filter(Payment.client_id == client_id)
            .order_by(Payment.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_stripe_intent(self, intent_id: str) -> Payment | None:
        return (
            self.db.query(Payment)
            .filter(Payment.stripe_payment_intent_id == intent_id)
            .first()
        )

    def update_status(self, payment_id: int, status: PaymentStatus) -> Payment | None:
        return self.update(payment_id, {"status": status})
