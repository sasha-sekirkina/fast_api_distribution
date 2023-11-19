import datetime
from typing import Dict, List, Type

from sqlalchemy.orm import sessionmaker, Query

from db.models import Base, engine, Distribution, Client, Message
from services.validation import NewDistribution, NewClient, UpdateClient, UpdateDistribution


class DataManager:
    def __init__(self):
        Base.metadata.create_all(engine)
        self.session_maker = sessionmaker(engine)
        self.distributions = DistributionsManager(self)
        self.clients = ClientsManager(self)

    def get_stat(self, detailed: bool = False) -> Dict:
        stat = {}
        with self.session_maker() as session:
            distributions = [vars(dist) for dist in session.query(Distribution).all()]
            stat["total_dist_cnt"] = len(distributions)
            stat["distributions"] = []
            for distribution in distributions:
                result = self.distributions.get_stat(distribution["id"], detailed)
                if result is not False:
                    stat["distributions"].append(result)
            return stat


class DistributionsManager:
    def __init__(self, parent: DataManager):
        self.parent = parent
        self.session_maker = parent.session_maker

    def get_by_id(self, dist_id: int) -> Type[Distribution] | None:
        with self.session_maker() as session:
            return session.get(Distribution, dist_id)

    def get_all(self) -> List:
        with self.session_maker() as session:
            return [vars(dist) for dist in session.query(Distribution).all()]

    def add(self, distribution: NewDistribution):
        with self.session_maker() as session:
            session.add(Distribution(
                start_date=distribution.start_date,
                end_date=distribution.end_date,
                filter_mobile_operator=distribution.filter_mobile_operator,
                filter_tag=distribution.filter_tag,
                text=distribution.text,
                name=distribution.name
            ))
            session.commit()

    def update(self, dist_id, updated_params: UpdateDistribution) -> bool:
        with self.session_maker() as session:
            distribution = session.get(Distribution, dist_id)
            if distribution is None or distribution.status not in ["created", "unfinished"]:
                return False
            if updated_params.name is not None:
                distribution.name = updated_params.name
            if updated_params.start_date is not None:
                distribution.start_date = updated_params.start_date
            if updated_params.end_date is not None:
                distribution.end_date = updated_params.end_date
            if updated_params.filter_tag is not None:
                distribution.filter_tag = updated_params.filter_tag
            if updated_params.filter_mobile_operator is not None:
                distribution.filter_mobile_operator = updated_params.filter_mobile_operator
            if updated_params.text is not None:
                distribution.text = updated_params.text
            session.commit()
        return True

    def delete(self, dist_id: int) -> bool:
        with self.session_maker() as session:
            dist = session.get(Distribution, dist_id)
            if dist is None:
                return False
            session.delete(dist)
            session.commit()
        return True

    def get_stat(self, dist_id: int, detailed=False) -> Dict | bool:
        stat = {}
        with self.session_maker() as session:
            distribution: Distribution | None = session.get(Distribution, dist_id)
            if distribution is None:
                return False
            stat["distribution"] = distribution
            total_messages = [vars(message) for message in session.query(Message).filter(
                Message.distribution_id == dist_id)]
            stat["messages_cnt"] = {}
            stat["messages_cnt"]["total"] = len(total_messages)
            stat["messages_cnt"]["created"] = len(list(filter(
                lambda message: message["status"] == "created", total_messages)))
            stat["messages_cnt"]["sent"] = len(list(filter(lambda message: message["status"] == "sent", total_messages)))
            if detailed:
                stat["messages"] = {}
                stat["messages"]["created"] = list(filter(
                    lambda message: message["status"] == "created", total_messages))
                for message in stat["messages"]["created"]:
                    message["client"] = self.parent.clients.get_by_id(message["client_id"])
                stat["messages"]["sent"] = list(filter(lambda message: message["status"] == "sent", total_messages))
                for message in stat["messages"]["sent"]:
                    message["client"] = self.parent.clients.get_by_id(message["client_id"])
        return stat

    def manage_status(self, dist_id: int) -> str | None:
        with self.session_maker() as session:
            distribution: Distribution | None = session.get(Distribution, dist_id)
            if distribution is None:
                return distribution
            if distribution.status in ["finished", "created"]:
                return distribution.status
            messages = self.get_messages(distribution.id)
            new_status = "finished"
            for message in messages:
                if message.status == "created":
                    new_status = "unfinished"
            distribution.status = new_status
            session.commit()
            return new_status

    def create_messages(self, dist_id: int):
        with self.session_maker() as session:
            distribution: Distribution | None = session.get(Distribution, dist_id)
            if distribution is None:
                return
            if distribution.filter_tag != "all" and distribution.filter_mobile_operator != "000":
                clients = session.query(Client).where((Client.tag == distribution.filter_tag) & (
                    Client.mobile_operator == distribution.filter_mobile_operator))
            elif distribution.filter_tag != "all":
                clients = session.query(Client).where(Client.tag == distribution.filter_tag)
            elif distribution.filter_mobile_operator != "000":
                clients = session.query(Client).where(Client.mobile_operator == distribution.filter_mobile_operator)
            else:
                clients = session.query(Client).all()
            for client in clients:
                session.add(Message(distribution_id=distribution.id, client_id=client.id))
            distribution.status = "started"
            session.commit()

    def get_messages(self, dist_id: int) -> Query:
        with self.session_maker() as session:
            messages = session.query(Message).where(Message.distribution_id == dist_id)
            return messages

    def mark_message_sent(self, message_id):
        with self.session_maker() as session:
            message = session.get(Message, message_id)
            message.status = "sent"
            message.sending_time = datetime.datetime.now()
            session.commit()

    def mark_distribution_expired(self, distribution_id: int):
        with self.session_maker() as session:
            distribution = self.get_by_id(distribution_id)
            if distribution is not None:
                distribution.status = "expired"
                session.commit()


class ClientsManager:
    def __init__(self, parent):
        self.session_maker = parent.session_maker

    def get_by_id(self, client_id: int) -> Client:
        with self.session_maker() as session:
            return session.get(Client, client_id)

    def add(self, client: NewClient):
        with self.session_maker() as session:
            session.add(Client(
                phone_number=client.phone_number,
                mobile_operator=client.mobile_operator,
                time_zone=client.time_zone,
                tag=client.tag
            ))
            session.commit()

    def get_all(self) -> List[Dict]:
        with self.session_maker() as session:
            return [vars(client) for client in session.query(Client).all()]

    def update(self, client_id: int, updated_params: UpdateClient):
        with self.session_maker() as session:
            client = session.get(Client, client_id)
            if client is None:
                return False
            if updated_params.phone_number is not None:
                client.phone_number = updated_params.phone_number
            if updated_params.mobile_operator is not None:
                client.mobile_operator = updated_params.mobile_operator
            if updated_params.tag is not None:
                client.tag = updated_params.tag
            if updated_params.time_zone is not None:
                client.time_zone = updated_params.time_zone
            session.commit()
        return True

    def delete(self, client_id: int):
        with self.session_maker() as session:
            cli = session.get(Client, client_id)
            if cli is None:
                return False
            session.delete(cli)
            session.commit()
        return True
