from typing import Dict, List, Any, Union

from sqlalchemy.orm import sessionmaker, Session

from db.models import Base, engine, Distribution, Client, Message
from services.validation import NewDistribution, NewClient, UpdateClient, UpdateDistribution


class DataManager:
    def __init__(self):
        Base.metadata.create_all(engine)
        self.session_maker = sessionmaker(engine)
        self.distributions = DistributionsManager(self.session_maker)
        self.clients = ClientsManager(self.session_maker)

    def get_stat(self) -> Dict:
        # todo refactor
        stat = {}
        with self.session_maker() as session:
            distributions = [vars(dist) for dist in session.query(Distribution).all()]
            stat["total_dist_cnt"] = len(distributions)
            stat["distributions"] = []
            for distribution in distributions:
                result = self.distributions.get_stat(distribution["id"])
                if result is not False:
                    stat["distributions"].append(result)
            return stat


class DistributionsManager:
    def __init__(self, session_maker):
        self.session_maker = session_maker

    def get_by_id(self, dist_id: int) -> Distribution:
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
                text=distribution.text
            ))
            session.commit()

    def update(self, dist_id, updated_params: UpdateDistribution) -> bool:
        with self.session_maker() as session:
            distribution = session.get(Distribution, dist_id)
            if distribution is None:
                return False
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
                print("dist is None")
                return False
            session.delete(dist)
            session.commit()
        return True

    def get_stat(self, dist_id: int, detailed=False) -> Union[Dict, bool]:
        # todo refactor
        stat = {}
        with self.session_maker() as session:
            distribution: Distribution = session.get(Distribution, dist_id)
            if distribution is None:
                return False
            stat["distribution"] = distribution
            total_messages = [vars(message) for message in session.query(Message).filter(
                Message.distribution_id == dist_id)]
            stat["total_messages_cnt"] = len(total_messages)
            stat["created_messages_cnt"] = len(list(filter(
                lambda message: message["status"] == "created", total_messages)))
            stat["sent_messages_cnt"] = len(list(filter(lambda message: message["status"] == "sent", total_messages)))
            if detailed:
                stat["messages"] = {}
                stat["messages"]["created"] = list(filter(
                    lambda message: message["status"] == "created", total_messages))
                stat["messages"]["sent"] = list(filter(lambda message: message["status"] == "sent", total_messages))
        return stat

    def mark_started(self, dist_id: int):
        with self.session_maker() as session:
            distribution: Distribution = session.get(Distribution, dist_id)
            distribution.status = "started"
            session.commit()

    def mark_finished(self, dist_id: int):
        with self.session_maker() as session:
            distribution: Distribution = session.get(Distribution, dist_id)
            distribution.status = "finished"
            session.commit()

    def create_messages(self, dist_id: int):
        with self.session_maker() as session:
            distribution: Distribution = session.get(Distribution, dist_id)
            if distribution.status == "created":
                clients = session.query(Client).all()
                for client in clients:
                    session.add(Message(distribution=distribution.id, client=client.id))
            distribution.status = "started"
            session.commit()


class ClientsManager:
    def __init__(self, session_maker):
        self.session_maker = session_maker

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
                print("cli is none")
                return False
            session.delete()
            session.commit()
        return True


data_manager = DataManager()
