# Business rules

Rules and assumptions not captured in the UML conceptual model.

1. A `BookCopy` remains assigned to the same `Library` and is not transferred between Libraries.
2. A Borrower may have multiple concurrent Loans at a Library, but their number must not exceed that Library's `maxConcurrentLoans` value.
3. Completed Loans are retained as historical records and are not deleted after the BookCopy is returned.
4. A Borrower may have at most one `LibraryMembership` for a given Library.
5. `LibraryMembership` history is not versioned. For a given Borrower–Library pair, the same membership record is retained and updated rather than replaced with a new one.
6. Former Borrowers are retained in the system.
7. A Loan is overdue when its `dueAt` time has passed and `returnedAt` is not set.
8. A Loan must use a `LibraryMembership` issued by the same Library that holds the loaned `BookCopy`.
9. The `LibraryMembership` used for a Loan must be valid when the Loan begins.
10. A `BookCopy` may have at most one open Loan at a time. An open Loan is a Loan whose `returnedAt` value is not set.
11. Library borrowing-policy values are treated as time-invariant. Their history is not represented.
12. A Library's `name` is globally unique and identifies the Library.
13. `BookCopyAvailabilityStatus` is derived from the BookCopy's operational status and Loans: it is AVAILABLE when the operational status is IN_CIRCULATION and there is no open Loan, ON_LOAN when an open Loan exists, and UNAVAILABLE otherwise.
14. A late fee is calculated only for overdue Loans whose returnedAt value is not set. For returned BookCopies, any applicable late fee is assumed to have been paid when the BookCopy was returned.
15. A late fee is charged only for complete 24-hour periods after the Loan becomes overdue. Each completed 24-hour period counts as one chargeable day.
    
