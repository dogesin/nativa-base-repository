from app.core.exceptions import ConflictError, NotFoundError
from app.domains.clients.models import Client
from app.domains.clients.repository import ClientRepository
from app.domains.clients.schemas import ClientCreate, ClientUpdate
from app.infrastructure.stripe.client import StripeClient


class ClientService:
    def __init__(self, repo: ClientRepository, stripe: StripeClient):
        self.repo = repo
        self.stripe = stripe

    def list_clients(self, skip: int = 0, limit: int = 100) -> list[Client]:
        return self.repo.get_all(skip=skip, limit=limit)

    def get_client(self, client_id: int) -> Client:
        client = self.repo.get_by_id(client_id)
        if not client:
            raise NotFoundError(f"Client {client_id} not found")
        return client

    def create_client(self, data: ClientCreate) -> Client:
        if self.repo.get_by_email(data.email):
            raise ConflictError(f"Email {data.email} is already registered")

        stripe_customer = self.stripe.create_customer(
            email=data.email,
            name=data.name,
        )

        return self.repo.create({
            **data.model_dump(),
            "stripe_customer_id": stripe_customer["id"],
        })

    def update_client(self, client_id: int, data: ClientUpdate) -> Client:
        client = self.repo.get_by_id(client_id)
        if not client:
            raise NotFoundError(f"Client {client_id} not found")

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return client

        updated = self.repo.update(client_id, update_data)
        return updated  # type: ignore[return-value]

    def delete_client(self, client_id: int) -> None:
        if not self.repo.delete(client_id):
            raise NotFoundError(f"Client {client_id} not found")
