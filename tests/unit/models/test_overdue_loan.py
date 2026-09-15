from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from library_demo.models.overdue_loan import OverdueLoan
from library_demo.models.overdue_loans_result import OverdueLoansResult


UTC_DATETIME = datetime(2026, 9, 1, 12, tzinfo=timezone.utc)
NAIVE_DATETIME = datetime(2026, 9, 1, 12)
NON_UTC_DATETIME = datetime(2026, 9, 1, 12, tzinfo=timezone(timedelta(hours=2)))


def test_overdue_loan_accepts_utc_due_at() -> None:
    loan = OverdueLoan(
        loan_id="loan-1",
        book_copy_id="copy-1",
        book_title="The Left Hand of Darkness",
        borrower_id="account-1",
        borrower_name="Ursula K. Le Guin",
        due_at=UTC_DATETIME,
    )

    assert loan.due_at == UTC_DATETIME


def test_overdue_loan_rejects_naive_due_at() -> None:
    with pytest.raises(ValidationError):
        OverdueLoan(
            loan_id="loan-1",
            book_copy_id="copy-1",
            book_title="The Left Hand of Darkness",
            borrower_id="account-1",
            borrower_name="Ursula K. Le Guin",
            due_at=NAIVE_DATETIME,
        )


def test_overdue_loan_rejects_non_utc_due_at() -> None:
    with pytest.raises(ValidationError):
        OverdueLoan(
            loan_id="loan-1",
            book_copy_id="copy-1",
            book_title="The Left Hand of Darkness",
            borrower_id="account-1",
            borrower_name="Ursula K. Le Guin",
            due_at=NON_UTC_DATETIME,
        )


def test_overdue_loans_result_rejects_naive_as_of() -> None:
    with pytest.raises(ValidationError):
        OverdueLoansResult(
            library_name="Central Library",
            as_of=NAIVE_DATETIME,
            items=[],
        )


def test_overdue_loans_result_rejects_non_utc_as_of() -> None:
    with pytest.raises(ValidationError):
        OverdueLoansResult(
            library_name="Central Library",
            as_of=NON_UTC_DATETIME,
            items=[],
        )


def test_overdue_loans_result_rejects_invalid_nested_item() -> None:
    with pytest.raises(ValidationError):
        OverdueLoansResult(
            library_name="Central Library",
            as_of=UTC_DATETIME,
            items=[
                {
                    "loan_id": "loan-1",
                    "book_copy_id": "copy-1",
                    "book_title": "The Left Hand of Darkness",
                    "borrower_id": "account-1",
                    "borrower_name": "Ursula K. Le Guin",
                    "due_at": NAIVE_DATETIME,
                }
            ],
        )


def test_overdue_loans_result_accepts_empty_items() -> None:
    result = OverdueLoansResult(
        library_name="Central Library",
        as_of=UTC_DATETIME,
        items=[],
    )

    assert result.items == []
