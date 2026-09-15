from datetime import datetime, timedelta

from pydantic import BaseModel, field_validator


class OverdueLoan(BaseModel):
    loan_id: str
    book_copy_id: str
    book_title: str
    borrower_id: str
    borrower_name: str
    due_at: datetime

    @field_validator("due_at")
    @classmethod
    def require_utc_datetime(cls, value: datetime) -> datetime:
        if value.utcoffset() != timedelta(0):
            raise ValueError("datetime must be timezone-aware UTC")
        return value
