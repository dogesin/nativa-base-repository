from fastapi import APIRouter, Depends, status

from app.domains.clients.dependencies import get_client_service
from app.domains.clients.schemas import ClientCreate, ClientRead, ClientUpdate
from app.domains.clients.service import ClientService

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.get("/", response_model=list[ClientRead])
def list_clients(
    skip: int = 0,
    limit: int = 100,
    service: ClientService = Depends(get_client_service),
):
    return service.list_clients(skip=skip, limit=limit)


@router.get("/{client_id}", response_model=ClientRead)
def get_client(
    client_id: int,
    service: ClientService = Depends(get_client_service),
):
    return service.get_client(client_id)


@router.post("/", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(
    data: ClientCreate,
    service: ClientService = Depends(get_client_service),
):
    return service.create_client(data)


@router.patch("/{client_id}", response_model=ClientRead)
def update_client(
    client_id: int,
    data: ClientUpdate,
    service: ClientService = Depends(get_client_service),
):
    return service.update_client(client_id, data)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: int,
    service: ClientService = Depends(get_client_service),
):
    service.delete_client(client_id)
