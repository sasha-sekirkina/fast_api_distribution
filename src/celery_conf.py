from celery import Celery

celery = Celery(
    "distribute",
    broker="redis://localhost:6379",
    accept_content=['pickle'],
    task_serializer='pickle'
)
