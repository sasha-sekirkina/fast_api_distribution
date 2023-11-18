import logging
from datetime import datetime
from threading import Thread
from time import sleep

from distribution.task import distribute

logger = logging.getLogger("distribution_worker")


class DistributionsWorker(Thread):
    def __init__(self, data_manager):
        from db.manager import DataManager
        self._data_manager: DataManager = data_manager
        self._first_run = True
        super().__init__()
        self.daemon = True

    def run(self):
        while True:
            distributions = self._data_manager.distributions.get_all()
            required_statuses = ["created", "unfinished"]
            if self._first_run:
                required_statuses.append("started")
            for distribution in distributions:
                if distribution["status"] in required_statuses:
                    now = datetime.now()
                    if distribution["start_date"] < now:
                        if distribution["end_date"] > now:
                            distribute.apply_async((distribution["id"],), expires=distribution["end_date"])
                            logger.info(f"Distribution {distribution['id']} worker started")
                        else:
                            self._data_manager.distributions.mark_distribution(distribution["id"])
                            logger.info(f"Distribution {distribution['id']} expired")

            self._first_run = False
            sleep(15)
