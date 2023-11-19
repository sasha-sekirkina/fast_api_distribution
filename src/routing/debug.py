from fastapi import APIRouter

from depends import data_manager

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get('/messages', responses={404: {"message": "Not found"}})
def get_messages():
    return data_manager.messages.get_all_messages()

