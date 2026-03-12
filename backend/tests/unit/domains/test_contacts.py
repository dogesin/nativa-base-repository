from app.core.config import settings

PREFIX = settings.API_V1_PREFIX


def _create_client(client):
    resp = client.post(f"{PREFIX}/clients/", json={
        "name": "Host", "email": "host@example.com"
    })
    return resp.json()["id"]


def test_create_contact(client):
    cid = _create_client(client)
    resp = client.post(f"{PREFIX}/clients/{cid}/contacts/", json={
        "first_name": "Ana",
        "last_name": "Lopez",
        "email": "ana@example.com",
        "role": "CTO",
    })
    assert resp.status_code == 201
    assert resp.json()["client_id"] == cid


def test_list_contacts(client):
    cid = _create_client(client)
    client.post(f"{PREFIX}/clients/{cid}/contacts/", json={"first_name": "A", "last_name": "B"})
    client.post(f"{PREFIX}/clients/{cid}/contacts/", json={"first_name": "C", "last_name": "D"})
    resp = client.get(f"{PREFIX}/clients/{cid}/contacts/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_delete_contact(client):
    cid = _create_client(client)
    create = client.post(f"{PREFIX}/clients/{cid}/contacts/", json={"first_name": "X", "last_name": "Y"})
    contact_id = create.json()["id"]
    resp = client.delete(f"{PREFIX}/clients/{cid}/contacts/{contact_id}")
    assert resp.status_code == 204


def test_contacts_for_nonexistent_client(client):
    resp = client.get(f"{PREFIX}/clients/9999/contacts/")
    assert resp.status_code == 404
