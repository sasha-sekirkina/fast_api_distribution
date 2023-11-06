from datetime import datetime
from typing import List

import pytz
import requests
from celery import Celery
from celery.utils.log import get_task_logger

from configs import TOKEN, URL
from db.models import Distribution, Message
from db.manager import data_manager

celery = Celery("distribute", broker="redis://localhost:6379", accept_content=['pickle'])

logger = get_task_logger(__name__)


@celery.task(serializer='pickle')
def distribute(distribution: Distribution):
    if distribution.status == "created":
        data_manager.distributions.create_messages(distribution.id)
    messages_to_send: List[Message] = data_manager.distributions.get_messages(distribution.id)
    for message in messages_to_send:
        if message.status != "sent":
            client = data_manager.clients.get_by_id(message.client_id)
            timezone = pytz.timezone(client.timezone)
            now = datetime.now(timezone)
            if distribution.time_start <= now.time() <= distribution.time_end:
                header = {
                    "Authorization": f"Bearer {TOKEN}",
                    "Content-Type": "application/json",
                }
                data = {
                    "id": message.id,
                    "phone": client.phone_number,
                    "text": distribution.text,
                }
                try:
                    requests.post(url=URL + str(data["id"]), headers=header, json=data)
                except requests.exceptions.RequestException as exc:
                    logger.warning(f"Sending message {message.id} failed: {exc}")
                else:
                    logger.info(f"Message sent id={message.id}, phone={client.phone_number}, text={distribution.text}")
                    data_manager.distributions.mark_message_sent(message.id)
    data_manager.distributions.manage_status(distribution.id)
