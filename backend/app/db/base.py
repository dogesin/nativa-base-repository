from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models here so Alembic can detect them.
# This file is the single source of truth for metadata.
def import_all_models() -> None:
    from app.domains.clients import models as _clients  # noqa: F401
    from app.domains.contacts import models as _contacts  # noqa: F401
    from app.domains.payments import models as _payments  # noqa: F401
