from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.domains.clients.repository import ClientRepository
from app.domains.payments.repository import PaymentRepository
from app.domains.payments.service import PaymentService
from app.infrastructure.stripe.client import StripeClient


def get_payment_repository(db: Session = Depends(get_db)) -> PaymentRepository:
    return PaymentRepository(db)


def get_client_repository(db: Session = Depends(get_db)) -> ClientRepository:
    return ClientRepository(db)


def get_payment_service(
    repo: PaymentRepository = Depends(get_payment_repository),
    client_repo: ClientRepository = Depends(get_client_repository),
    stripe: StripeClient = Depends(),
) -> PaymentService:
    return PaymentService(repo, client_repo, stripe)
