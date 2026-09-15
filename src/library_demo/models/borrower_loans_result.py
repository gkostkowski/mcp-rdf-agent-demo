from pydantic import BaseModel

from library_demo.models.borrower_loan import BorrowerLoan


class BorrowerLoansResult(BaseModel):
    borrower_id: str
    items: list[BorrowerLoan]
