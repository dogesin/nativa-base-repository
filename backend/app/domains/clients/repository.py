from sqlalchemy.orm import Session

from app.domains.clients.models import Client
from app.shared.base_repository import BaseRepository


class ClientRepository(BaseRepository[Client]):
    def __init__(self, db: Session):
        super().__init__(Client, db)

    def get_by_email(self, email: str) -> Client | None:
        return self.db.query(Client).filter(Client.email == email).first()

    def get_by_stripe_id(self, stripe_customer_id: str) -> Client | None:
        return (
            self.db.query(Client)
            .filter(Client.stripe_customer_id == stripe_customer_id)
            .first()
        )
