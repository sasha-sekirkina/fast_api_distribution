from datetime import datetime
from typing import Dict

import pytz
import requests
from celery.utils.log import get_task_logger

from celery_conf import celery
from configs import TOKEN, URL
from depends import data_manager

logger = get_task_logger(__name__)


@celery.task(bind=True, retry_backoff=True)
def distribute(self, distribution: Dict):
    if distribution["status"] == "created":
        data_manager.distributions.create_messages(distribution["id"])
    messages_to_send = data_manager.distributions.get_messages(distribution["id"])
    for message in messages_to_send:
        if message.status != "sent":
            client = data_manager.clients.get_by_id(message.client_id)
            timezone = pytz.timezone(client.time_zone)
            now = datetime.now(timezone)
            if distribution["start_date"] <= now.time() <= distribution["end_date"]:
                header = {
                    "Authorization": f"Bearer {TOKEN}",
                    "Content-Type": "application/json",
                }
                data = {
                    "id": message.id,
                    "phone": client.phone_number,
                    "text": distribution["text"],
                }
                try:
                    requests.post(url=URL + str(data["id"]), headers=header, json=data)
                except requests.exceptions.RequestException as exc:
                    logger.warning(f"Sending message {message.id} failed: {exc}")
                else:
                    logger.info(f"Message sent id={message.id}, phone={client.phone_number}, text={distribution['text']}")
                    data_manager.distributions.mark_message_sent(message.id)
    status = data_manager.distributions.manage_status(distribution["id"])
    if status == "started":
        self.retry()
