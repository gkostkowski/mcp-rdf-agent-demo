from datetime import datetime, timedelta

from pydantic import BaseModel, field_validator

from library_demo.models.overdue_loan import OverdueLoan


class OverdueLoansResult(BaseModel):
    library_name: str
    as_of: datetime
    items: list[OverdueLoan]

    @field_validator("as_of")
    @classmethod
    def require_utc_datetime(cls, value: datetime) -> datetime:
        if value.utcoffset() != timedelta(0):
            raise ValueError("datetime must be timezone-aware UTC")
        return value
