from celery import Celery

from configs import TOKEN, URL
from db.models import Distribution

celery = Celery("distribute", broker="redis://localhost:6379")


@celery.task
def distribute(distribution: Distribution):
    ...
