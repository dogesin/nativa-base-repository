from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.domains.clients.repository import ClientRepository
from app.domains.clients.service import ClientService
from app.infrastructure.stripe.client import StripeClient


def get_client_repository(db: Session = Depends(get_db)) -> ClientRepository:
    return ClientRepository(db)


def get_client_service(
    repo: ClientRepository = Depends(get_client_repository),
    stripe: StripeClient = Depends(),
) -> ClientService:
    return ClientService(repo, stripe)
