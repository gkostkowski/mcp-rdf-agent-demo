from datetime import datetime, timedelta

from pydantic import BaseModel, field_validator


class BorrowerLoan(BaseModel):
    loan_id: str
    book_copy_id: str
    book_title: str
    library_name: str
    borrowed_at: datetime
    due_at: datetime
    returned_at: datetime | None

    @field_validator("borrowed_at", "due_at", "returned_at")
    @classmethod
    def require_utc_datetime(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.utcoffset() != timedelta(0):
            raise ValueError("datetime must be timezone-aware UTC")
        return value
