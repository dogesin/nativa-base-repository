from app.core.config import settings

PREFIX = settings.API_V1_PREFIX


def test_create_client(client):
    resp = client.post(f"{PREFIX}/clients/", json={
        "name": "Acme Corp",
        "email": "acme@example.com",
        "phone": "+5211234567",
        "company": "Acme",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "acme@example.com"
    assert data["stripe_customer_id"] is not None


def test_create_client_duplicate_email(client):
    payload = {"name": "A", "email": "dup@example.com"}
    client.post(f"{PREFIX}/clients/", json=payload)
    resp = client.post(f"{PREFIX}/clients/", json=payload)
    assert resp.status_code == 409


def test_list_clients(client):
    client.post(f"{PREFIX}/clients/", json={"name": "A", "email": "a@example.com"})
    client.post(f"{PREFIX}/clients/", json={"name": "B", "email": "b@example.com"})
    resp = client.get(f"{PREFIX}/clients/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_client(client):
    create = client.post(f"{PREFIX}/clients/", json={"name": "C", "email": "c@example.com"})
    cid = create.json()["id"]
    resp = client.get(f"{PREFIX}/clients/{cid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == cid


def test_update_client(client):
    create = client.post(f"{PREFIX}/clients/", json={"name": "D", "email": "d@example.com"})
    cid = create.json()["id"]
    resp = client.patch(f"{PREFIX}/clients/{cid}", json={"name": "Updated"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated"


def test_delete_client(client):
    create = client.post(f"{PREFIX}/clients/", json={"name": "E", "email": "e@example.com"})
    cid = create.json()["id"]
    resp = client.delete(f"{PREFIX}/clients/{cid}")
    assert resp.status_code == 204
    assert client.get(f"{PREFIX}/clients/{cid}").status_code == 404
