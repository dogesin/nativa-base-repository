from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.domains.clients.repository import ClientRepository
from app.domains.contacts.repository import ContactRepository
from app.domains.contacts.service import ContactService


def get_contact_repository(db: Session = Depends(get_db)) -> ContactRepository:
    return ContactRepository(db)


def get_client_repository(db: Session = Depends(get_db)) -> ClientRepository:
    return ClientRepository(db)


def get_contact_service(
    repo: ContactRepository = Depends(get_contact_repository),
    client_repo: ClientRepository = Depends(get_client_repository),
) -> ContactService:
    return ContactService(repo, client_repo)
