# Library S dataset

A synthetic **S-size** dataset for the Library demo semantic model. It is intended for integration, SPARQL, API, and agent-query tests rather than performance benchmarking.

## Size

| Entity type | Count |
|---|---:|
| Libraries | 4 |
| Addresses | 4 |
| Books | 10 |
| Authors | 9 |
| Book copies | 100 |
| Borrowers | 15 |
| Admins | 0 (intentionally omitted) |
| Library memberships | 19 |
| Loans | 100 |

Every person in the dataset is either an **Author** or a **Borrower**, never both. No Admin instances are included in this dataset.

## Distribution and cases covered

- **Book copies per book:** `30, 20, 15, 10, 8, 6, 5, 3, 2, 1`. The distribution is deliberately uneven.
- **Book copies per library:** `45, 30, 17, 8`.
- **Loans per borrower:** `28, 18, 12, 10, 8, 6, 5, 4, 3, 2, 2, 1, 1, 0, 0`. Two borrowers have no loan history.
- **Memberships:** 12 borrowers have one membership, 2 have two, and 1 has three. Three secondary memberships are expired.
- **Book identity:** two pairs of books share a title; one pair represents different editions and one pair represents unrelated books with the same title.
- **Authorship:** 6 books have one author, 2 have two authors, 1 has three authors, and 1 has no identified author. Some authors wrote more than one book.
- **Copy history:** 30 copies were never borrowed, 45 have one loan, 20 have two loans, and 5 have three loans.
- **Loan lifecycle:** 55 returned on time, 25 returned late, 12 open and not overdue, and 8 open and overdue, evaluated against the dataset reference date **2026-09-15**.
- **Operational status:** 88 `IN_CIRCULATION`, 5 `WITHDRAWN`, 4 `DAMAGED`, 3 `LOST`.
- **Derived availability:** 68 `AVAILABLE`, 20 `ON_LOAN`, 12 `UNAVAILABLE`. The availability values are materialized in the dataset for convenient querying.
- **Library consistency:** every loan uses a membership issued by the same library that holds the loaned copy.
- **Temporal consistency:** returned loans satisfy `borrowedAt < dueAt` and `returnedAt >= borrowedAt`; open loans omit `returnedAt`.

## Files expected alongside the dataset

The dataset uses terms from the latest Library ontology and refers to the controlled-value IRIs defined in `library_concept_schemes.ttl`, such as `lib:AVAILABLE`, `lib:ON_LOAN`, `lib:IN_CIRCULATION`, and `lib:WITHDRAWN`.
