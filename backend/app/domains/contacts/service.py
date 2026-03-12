from app.core.exceptions import NotFoundError
from app.domains.clients.repository import ClientRepository
from app.domains.contacts.models import Contact
from app.domains.contacts.repository import ContactRepository
from app.domains.contacts.schemas import ContactCreate, ContactUpdate


class ContactService:
    def __init__(self, repo: ContactRepository, client_repo: ClientRepository):
        self.repo = repo
        self.client_repo = client_repo

    def _ensure_client_exists(self, client_id: int) -> None:
        if not self.client_repo.get_by_id(client_id):
            raise NotFoundError(f"Client {client_id} not found")

    def list_contacts(self, client_id: int, skip: int = 0, limit: int = 100) -> list[Contact]:
        self._ensure_client_exists(client_id)
        return self.repo.get_by_client(client_id, skip=skip, limit=limit)

    def get_contact(self, contact_id: int) -> Contact:
        contact = self.repo.get_by_id(contact_id)
        if not contact:
            raise NotFoundError(f"Contact {contact_id} not found")
        return contact

    def create_contact(self, client_id: int, data: ContactCreate) -> Contact:
        self._ensure_client_exists(client_id)
        return self.repo.create({**data.model_dump(), "client_id": client_id})

    def update_contact(self, contact_id: int, data: ContactUpdate) -> Contact:
        contact = self.repo.get_by_id(contact_id)
        if not contact:
            raise NotFoundError(f"Contact {contact_id} not found")

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return contact

        updated = self.repo.update(contact_id, update_data)
        return updated  # type: ignore[return-value]

    def delete_contact(self, contact_id: int) -> None:
        if not self.repo.delete(contact_id):
            raise NotFoundError(f"Contact {contact_id} not found")
