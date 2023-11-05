from datetime import datetime
from typing import List, Optional

import pytz
from pydantic import BaseModel, field_validator, Field


class ClientValidation(BaseModel):
    phone_number: int
    mobile_operator: int
    tag: str
    time_zone: str

    @field_validator("phone_number")
    def validate_phone_num(cls, value):
        if len(str(value)) == 11 and str(value).startswith("7") and str(value).isalnum():
            return value
        raise ValueError("phone number validation failed")

    @field_validator("mobile_operator")
    def validate_mobile_operator(cls, value):
        if len(str(value)) == 3 and str(value).isalnum():
            return value
        raise ValueError("mobile operator validation failed")

    @field_validator("time_zone")
    def validate_time_zone(cls, _, value):
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
        raise ValueError("mobile operator validation failed")

