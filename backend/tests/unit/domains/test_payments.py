from app.core.config import settings

PREFIX = settings.API_V1_PREFIX


def _create_client(client):
    resp = client.post(f"{PREFIX}/clients/", json={
        "name": "Payer", "email": "payer@example.com"
    })
    return resp.json()["id"]


def test_create_payment(client):
    cid = _create_client(client)
    resp = client.post(f"{PREFIX}/clients/{cid}/payments", json={
        "amount": 5000,
        "currency": "usd",
        "description": "Monthly subscription",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["amount"] == 5000
    assert data["status"] == "pending"
    assert data["stripe_payment_intent_id"] is not None


def test_list_payments(client):
    cid = _create_client(client)
    client.post(f"{PREFIX}/clients/{cid}/payments", json={"amount": 1000})
    client.post(f"{PREFIX}/clients/{cid}/payments", json={"amount": 2000})
    resp = client.get(f"{PREFIX}/clients/{cid}/payments")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_payment(client):
    cid = _create_client(client)
    create = client.post(f"{PREFIX}/clients/{cid}/payments", json={"amount": 3000})
    pid = create.json()["id"]
    resp = client.get(f"{PREFIX}/payments/{pid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == pid


def test_payment_for_nonexistent_client(client):
    resp = client.post(f"{PREFIX}/clients/9999/payments", json={"amount": 500})
    assert resp.status_code == 404
