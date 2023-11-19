from datetime import datetime

import pytz
import requests
from celery import states
from celery.exceptions import Ignore
from celery.utils.log import get_task_logger

from celery_conf import celery
from configs import URL, TOKEN
from depends import data_manager


logger = get_task_logger("distribute")


@celery.task(bind=True, retry_backoff=True)
def distribute(self, distribution_id: int = None):
    if distribution_id is None:
        return
    distribution = data_manager.distributions.get_by_id(distribution_id)
    if distribution is None:
        self.update_state(
            state=states.FAILURE,
            meta=f"Distribution with id {distribution_id} not found."
        )
        raise Ignore()
    if distribution.status == "created":
        data_manager.messages.create_distribution_messages(distribution.id)
    messages_to_send = data_manager.messages.get_distribution_messages(distribution.id)
    for message in messages_to_send:
        if message.status != "sent":
            client = data_manager.clients.get_by_id(message.client_id)
            # todo sending message base on client timezone
            # timezone = pytz.timezone(client.time_zone)
            # if (distribution.start_date.replace(tzinfo=timezone) <= datetime.now(timezone)
            #         <= distribution.end_date.replace(tzinfo=timezone)):
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
                logger.info(
                    f"Message sent id={message.id}, phone={client.phone_number}, text={distribution.text}")
                data_manager.messages.mark_message_sent(message.id)
    status = data_manager.manage_status(distribution.id)
    # if status != "finished":
    #     self.update_state(
    #         state=states.FAILURE,
    #         meta=f"Distribution with id {distribution_id} not finished, status={status}"
    #     )
    #     raise Ignore()
