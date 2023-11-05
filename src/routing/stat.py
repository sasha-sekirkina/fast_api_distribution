from fastapi import APIRouter

from db.manager import data_manager

router = APIRouter(prefix="/stat", tags=["stat"])


@router.get('/get_stat')
def get_stat():
    return data_manager.get_stat()


@router.get('/get_distribution_stat/{dist_id}')
def get_distribution_stat(dist_id: int):
    return data_manager.distributions.get_stat(dist_id)
