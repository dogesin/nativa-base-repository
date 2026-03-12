import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.core.dependencies import get_db
from app.db.base import Base, import_all_models
from app.infrastructure.stripe.client import StripeClient
from app.main import app

SQLITE_URL = "sqlite://"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class FakeStripeClient(StripeClient):
    """Stripe stub that returns predictable data without hitting the API."""

    def __init__(self) -> None:
        pass  # skip real init

    def create_customer(self, *, email: str, name: str) -> dict:
        return {"id": f"cus_fake_{email}"}

    def create_payment_intent(self, *, amount: int, currency: str, customer_id: str, metadata: dict | None = None) -> dict:
        return {"id": f"pi_fake_{amount}"}

    def retrieve_payment_intent(self, payment_intent_id: str) -> dict:
        return {"id": payment_intent_id, "status": "succeeded"}

    def refund_payment_intent(self, payment_intent_id: str) -> dict:
        return {"id": f"re_fake_{payment_intent_id}"}


@pytest.fixture(autouse=True)
def setup_db():
    import_all_models()
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db):
    def _override_db():
        yield db

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[StripeClient] = FakeStripeClient
    yield TestClient(app)
    app.dependency_overrides.clear()
