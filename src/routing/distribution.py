from typing import List, Dict

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from depends import data_manager
from services.validation import NewDistribution, UpdateDistribution

router = APIRouter(prefix="/distribution", tags=["distribution"])


@router.get('/get/{dist_id}', responses={404: {"message": "Not found"}})
def get_distribution(dist_id: int):
    distribution = data_manager.distributions.get_by_id(dist_id)
    if distribution is not None:
        return distribution
    raise HTTPException(status_code=404, detail="Not found")


@router.get('/get_all', response_model=List)
def get_distributions():
    distributions = data_manager.distributions.get_all()
    if distributions is not None:
        return jsonable_encoder(distributions)
    return []


@router.post('/add')
def add_distribution(distribution: NewDistribution):
    data_manager.distributions.add(distribution)
    return "OK"


@router.put('/update/{dist_id}', responses={404: {"message": "Not found"}})
def update_distribution(dist_id: int, updated_fields: UpdateDistribution):
    result = data_manager.distributions.update(dist_id, updated_fields)
    if result is False:
        raise HTTPException(status_code=403,
                            detail="Distribution not found or distribution already started or finished")
    return "OK"


@router.delete('/delete/{dist_id}', responses={404: {"message": "Not found"}})
def delete_distribution(dist_id):
    result = data_manager.distributions.delete(dist_id)
    if result is False:
        raise HTTPException(status_code=403, detail="Distribution not found")
    return "OK"
