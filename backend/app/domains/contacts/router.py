from fastapi import APIRouter, Depends, status

from app.domains.contacts.dependencies import get_contact_service
from app.domains.contacts.schemas import ContactCreate, ContactRead, ContactUpdate
from app.domains.contacts.service import ContactService

router = APIRouter(prefix="/clients/{client_id}/contacts", tags=["Contacts"])


@router.get("/", response_model=list[ContactRead])
def list_contacts(
    client_id: int,
    skip: int = 0,
    limit: int = 100,
    service: ContactService = Depends(get_contact_service),
):

    return service.list_contacts(client_id, skip=skip, limit=limit)


@router.post("/", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
def create_contact(
    client_id: int,
    data: ContactCreate,
    service: ContactService = Depends(get_contact_service),
):
    return service.create_contact(client_id, data)


@router.get("/{contact_id}", response_model=ContactRead)
def get_contact(
    contact_id: int,
    service: ContactService = Depends(get_contact_service),
):
    return service.get_contact(contact_id)


@router.patch("/{contact_id}", response_model=ContactRead)
def update_contact(
    contact_id: int,
    data: ContactUpdate,
    service: ContactService = Depends(get_contact_service),
):
    return service.update_contact(contact_id, data)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: int,
    service: ContactService = Depends(get_contact_service),
):
    service.delete_contact(contact_id)
