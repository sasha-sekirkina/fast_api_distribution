from fastapi import APIRouter, HTTPException

from db.manager import data_manager
from services.validation import NewClient, UpdateClient

router = APIRouter(prefix="/client", tags=["client"])


@router.get('/get/{client_id}', responses={404: {"message": "Not found"}})
def get_client(client_id: int):
    client = data_manager.clients.get_by_id(client_id)
    if client is not None:
        return client
    raise HTTPException(status_code=404, detail="Not found")


@router.get('/get_all')
def get_clients():
    clients = data_manager.clients.get_all()
    if clients is not None:
        return clients
    return []


@router.post('/add')
def add_client(client: NewClient):
    data_manager.clients.add(client)
    return {"status": 200, "message": "OK"}


@router.put('/update/{client_id}')
def update_client(client_id: int, updated_fields: UpdateClient):
    result = data_manager.clients.update(client_id, updated_fields)
    if result is False:
        raise HTTPException(status_code=404, detail="Not found")
    return "OK"


@router.delete('/delete/{client_id}')
def delete_client(client_id):
    data_manager.clients.delete(client_id)
    return "OK"
