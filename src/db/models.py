import enum
from datetime import datetime
from typing import Optional

import pytz
from sqlalchemy import create_engine, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, validates, relationship, Mapped, mapped_column

engine = create_engine("sqlite:///distribution.db", echo=True)
Base = declarative_base()


class DistributionStatus(enum.Enum):
    CREATED = "created"
    STARTED = "started"
    FINISHED = "finished"


class Distribution(Base):
    __tablename__ = "distribution"

    id: Mapped[int] = mapped_column(primary_key=True)
    start_date: Mapped[datetime] = mapped_column(DateTime)
    end_date: Mapped[datetime] = mapped_column(DateTime)
    text: Mapped[str] = mapped_column(String)
    filter_mobile_operator: Mapped[Optional[int]] = mapped_column(Integer, default="all")
    filter_tag: Mapped[Optional[str]] = mapped_column(String, default="all")
    status: Mapped[str] = mapped_column(String, default="created")

    messages = relationship("Message", back_populates="distribution")


class Client(Base):
    __tablename__ = "client"

    id: Mapped[int] = mapped_column(primary_key=True)
    phone_number: Mapped[int] = mapped_column(Integer)
    mobile_operator: Mapped[int] = mapped_column(Integer)
    tag: Mapped[str] = mapped_column(String, nullable=True)
    time_zone: Mapped[str] = mapped_column(String)

    messages = relationship("Message", back_populates="client")

    @validates("phone_number")
    def validate_phone_number(self, _, value):
        if len(str(value)) == 11 and str(value).startswith("7") and str(value).isalnum():
            return value
        raise ValueError("Phone number validation failed")

    @validates("mobile_operator")
    def validate_mobile_operator(self, _, value):
        if len(str(value)) == 3 and str(value).isalnum():
            return value
        raise ValueError("Mobile operator validation failed")

    @validates("time_zone")
    def validate_time_zone(self, _, value):
        if value in pytz.all_timezones:
            return value
        raise ValueError("Time zone validation failed")


class Message(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True)
    sending_time: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String, default="created")
    distribution_id: Mapped["Distribution"] = mapped_column(ForeignKey("distribution.id"))
    client_id: Mapped["Client"] = mapped_column(ForeignKey("client.id"))

    distribution: Mapped["Distribution"] = relationship(back_populates="messages")
    client: Mapped["Client"] = relationship(back_populates="messages")
