from datetime import datetime
from typing import Optional

import pytz
from pydantic import BaseModel, field_validator, Field


class NewClient(BaseModel):
    phone_number: int = Field(ge=70000000000, lt=80000000000)
    mobile_operator: int = Field(ge=100, lt=1000)
    tag: Optional[str] = None
    time_zone: str

    @field_validator("time_zone")
    def validate_time_zone(cls, value):
        print(value, value in pytz.all_timezones)
        if value in pytz.all_timezones:
            return value
        raise ValueError("Time zone validation failed")


class UpdateClient(BaseModel):
    phone_number: Optional[int] = None
    mobile_operator: int = Field(ge=100, lt=1000)
    tag: Optional[str] = None
    time_zone: Optional[str] = None

    @field_validator("phone_number")
    def validate_phone_number(cls, value):
        if 70000000000 <= value <= 80000000000:
            return value
        raise ValueError("Phone number validation failed")

    @field_validator("mobile_operator")
    def validate_mobile_operator(cls, value):
        if 99 <= value <= 1000:
            return value
        raise ValueError("Mobile operator validation failed")

    @field_validator("time_zone")
    def validate_time_zone(cls, value):
        print(value, value in pytz.all_timezones)
        if value in pytz.all_timezones:
            return value
        raise ValueError("Time zone validation failed")


class NewDistribution(BaseModel):
    start_date: datetime
    end_date: datetime
    text: str
    filter_mobile_operator: int = 000
    filter_tag: str = "all"

    @field_validator("filter_mobile_operator")
    def validate_mobile_operator(cls, value):
        if len(str(value)) == 3 and str(value).isalnum() or value is None:
            return value
        raise ValueError("Mobile operator validation failed")


class UpdateDistribution(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    text: Optional[str] = None
    filter_mobile_operator: Optional[int] = None
    filter_tag: Optional[str] = None

    @field_validator("filter_mobile_operator")
    def validate_mobile_operator(cls, value):
        if len(str(value)) == 3 and str(value).isalnum() or value is None:
            return value
        raise ValueError("Mobile operator validation failed")
