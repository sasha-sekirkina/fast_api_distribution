from datetime import datetime
from typing import Optional

import pytz
from pydantic import BaseModel, field_validator, Field


class NewClient(BaseModel):
    phone_number: int = Field(ge=70000000000, lt=80000000000)
    mobile_operator: str = "000"
    tag: Optional[str] = None
    time_zone: str

    @field_validator("mobile_operator")
    def validate_mobile_operator(cls, value):
        if len(value) == 3 and value.isalnum() or value is None:
            return value
        raise ValueError("Mobile operator validation failed")

    @field_validator("time_zone")
    def validate_time_zone(cls, value):
        if value in pytz.all_timezones:
            return value
        raise ValueError("Time zone validation failed")


class UpdateClient(BaseModel):
    phone_number: Optional[int] = None
    mobile_operator: Optional[str] = "000"
    tag: Optional[str] = None
    time_zone: Optional[str] = None

    @field_validator("phone_number")
    def validate_phone_number(cls, value):
        if 70000000000 <= value <= 80000000000:
            return value
        raise ValueError("Phone number validation failed")

    @field_validator("mobile_operator")
    def validate_mobile_operator(cls, value):
        if len(value) == 3 and value.isalnum() or value is None:
            return value
        raise ValueError("Mobile operator validation failed")

    @field_validator("time_zone")
    def validate_time_zone(cls, value):
        if value in pytz.all_timezones:
            return value
        raise ValueError("Time zone validation failed")


class NewDistribution(BaseModel):
    start_date: datetime
    end_date: datetime
    text: str
    filter_mobile_operator: str = "000"
    filter_tag: str = "all"

    @field_validator("filter_mobile_operator")
    def validate_mobile_operator(cls, value):
        if len(value) == 3 and value.isalnum() or value is None:
            return value
        raise ValueError("Mobile operator validation failed")


class UpdateDistribution(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    text: Optional[str] = None
    filter_mobile_operator: Optional[str] = None
    filter_tag: Optional[str] = None

    @field_validator("filter_mobile_operator")
    def validate_mobile_operator(cls, value):
        if len(value) == 3 and value.isalnum() or value is None:
            return value
        raise ValueError("Mobile operator validation failed")
