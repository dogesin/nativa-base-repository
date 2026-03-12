from sqlalchemy.orm import Session

from app.domains.contacts.models import Contact
from app.shared.base_repository import BaseRepository


class ContactRepository(BaseRepository[Contact]):
    def __init__(self, db: Session):
        super().__init__(Contact, db)

    def get_by_client(
        self, client_id: int, *, skip: int = 0, limit: int = 100
    ) -> list[Contact]:
        return (
            self.db.query(Contact)
            .filter(Contact.client_id == client_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
