from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from library_demo.models.borrower_loan import BorrowerLoan
from library_demo.models.borrower_loans_result import BorrowerLoansResult


UTC_DATETIME = datetime(2026, 9, 1, 12, tzinfo=timezone.utc)
NAIVE_DATETIME = datetime(2026, 9, 1, 12)
NON_UTC_DATETIME = datetime(2026, 9, 1, 12, tzinfo=timezone(timedelta(hours=2)))


def test_borrower_loan_accepts_utc_datetimes() -> None:
    loan = BorrowerLoan(
        loan_id="loan-1",
        book_copy_id="copy-1",
        book_title="The Left Hand of Darkness",
        library_name="Central Library",
        borrowed_at=UTC_DATETIME,
        due_at=UTC_DATETIME,
        returned_at=UTC_DATETIME,
    )

    assert loan.returned_at == UTC_DATETIME


def test_borrower_loan_rejects_naive_borrowed_at() -> None:
    with pytest.raises(ValidationError):
        BorrowerLoan(
            loan_id="loan-1",
            book_copy_id="copy-1",
            book_title="The Left Hand of Darkness",
            library_name="Central Library",
            borrowed_at=NAIVE_DATETIME,
            due_at=UTC_DATETIME,
            returned_at=None,
        )


def test_borrower_loan_rejects_non_utc_due_at() -> None:
    with pytest.raises(ValidationError):
        BorrowerLoan(
            loan_id="loan-1",
            book_copy_id="copy-1",
            book_title="The Left Hand of Darkness",
            library_name="Central Library",
            borrowed_at=UTC_DATETIME,
            due_at=NON_UTC_DATETIME,
            returned_at=None,
        )


def test_borrower_loan_rejects_naive_returned_at() -> None:
    with pytest.raises(ValidationError):
        BorrowerLoan(
            loan_id="loan-1",
            book_copy_id="copy-1",
            book_title="The Left Hand of Darkness",
            library_name="Central Library",
            borrowed_at=UTC_DATETIME,
            due_at=UTC_DATETIME,
            returned_at=NAIVE_DATETIME,
        )


def test_borrower_loan_rejects_non_utc_returned_at() -> None:
    with pytest.raises(ValidationError):
        BorrowerLoan(
            loan_id="loan-1",
            book_copy_id="copy-1",
            book_title="The Left Hand of Darkness",
            library_name="Central Library",
            borrowed_at=UTC_DATETIME,
            due_at=UTC_DATETIME,
            returned_at=NON_UTC_DATETIME,
        )


def test_borrower_loans_result_rejects_invalid_nested_item() -> None:
    with pytest.raises(ValidationError):
        BorrowerLoansResult(
            borrower_id="account-1",
            items=[
                {
                    "loan_id": "loan-1",
                    "book_copy_id": "copy-1",
                    "book_title": "The Left Hand of Darkness",
                    "library_name": "Central Library",
                    "borrowed_at": UTC_DATETIME,
                    "due_at": NAIVE_DATETIME,
                    "returned_at": None,
                }
            ],
        )


def test_borrower_loans_result_accepts_empty_items() -> None:
    result = BorrowerLoansResult(borrower_id="account-1", items=[])

    assert result.items == []
