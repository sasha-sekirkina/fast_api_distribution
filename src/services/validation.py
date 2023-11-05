from datetime import datetime
from typing import Optional

import pytz
from pydantic import BaseModel, field_validator, Field


class ClientValidation(BaseModel):
    phone_number: int = Field(ge=70000000000, lt=80000000000)
    mobile_operator: int = Field(ge=100, lt=1000)
    tag: Optional[str] = None
    time_zone: str

    @field_validator("mobile_operator")
    def validate_mobile_operator(cls, value):
        if len(str(value)) == 3 and str(value).isalnum():
            return value
        raise ValueError("Mobile operator validation failed")

    @field_validator("time_zone")
    def validate_time_zone(cls, value):
        print(value, value in pytz.all_timezones)
        if value in pytz.all_timezones:
            return value
        raise ValueError("Time zone validation failed")


class DistributionValidation(BaseModel):
    start_date: datetime
    end_date: datetime
    text: str
    filter_mobile_operator: Optional[int] = None
    filter_tag: Optional[str] = None

    @field_validator("filter_mobile_operator")
    def validate_mobile_operator(cls, value):
        if len(str(value)) == 3 and str(value).isalnum() or value is None:
            return value
        raise ValueError("Mobile operator validation failed")

