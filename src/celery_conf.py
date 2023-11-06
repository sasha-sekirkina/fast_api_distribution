from celery import Celery

from configs import REDIS_HOST, REDIS_PORT

celery = Celery(
    "distribute",
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}",
    accept_content=['pickle'],
    task_serializer='pickle'
)
