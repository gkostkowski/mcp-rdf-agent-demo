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
| Library memberships | 19 |
| Loans | 100 |

Every person in the dataset is either an **Author** or a **Borrower**, never both.

## Distribution and cases covered

- **Book copies per book:** deliberately uneven, with popular and rare books represented.
- **Book copies per library:** deliberately uneven across the four libraries.
- **Loans per borrower:** deliberately uneven; two borrowers have no loan history.
- **Memberships:** 12 borrowers have one membership, 2 have two, and 1 has three. Three secondary memberships are expired.
- **Book identity:** two pairs of books share a title; one pair represents different editions and one pair represents unrelated books with the same title.
- **Authorship:** 6 books have one author, 2 have two authors, 1 has three authors, and 1 has no identified author.
- **Copy history:** 39 copies were never borrowed, 34 have one loan, 16 have two loans, 10 have three loans, and 1 has four loans.
- **Loan lifecycle:** 55 returned on time, 25 returned late, 12 open and not overdue, and 8 open and overdue, evaluated against the dataset reference date **2026-09-15**.
- **Operational status:** 88 `IN_CIRCULATION`, 5 `WITHDRAWN`, 4 `DAMAGED`, 3 `LOST`.
- **Derived availability:** 68 `AVAILABLE`, 20 `ON_LOAN`, 12 `UNAVAILABLE`. Availability values are materialized for convenient querying.
- **Library consistency:** every loan uses a membership issued by the same library that holds the loaned copy.
- **Current-loan variety:** no borrower has two simultaneous open loans for the same `Book`.
- **Temporal consistency:** returned loans satisfy `borrowedAt < dueAt` and `returnedAt >= borrowedAt`; open loans omit `returnedAt`.

## Overdue test cases

The dataset contains **8 overdue open loans** spread across **3 of the 4 libraries**. They use eight different books and cover a broad range of due dates from January 2026 through 14 September 2026:

| Borrower | Library | Title | Due |
|---|---|---|---|
| Alice Adams | Central Library | The Semantic City | 2026-01-31 |
| Ben Baker | Central Library | The Last Index | 2026-03-08 |
| Clara Cole | West Library | Winter Catalogue | 2026-04-12 |
| Daniel Diaz | Central Library | Graphs at Work | 2026-05-22 |
| Farid Farouk | Central Library | Library Systems | 2026-06-18 |
| Jack Jones | North Library | Anonymous Letters | 2026-07-27 |
| Grace Green | West Library | Quiet Shelves | 2026-08-26 |
| Karen Kim | West Library | Ontology by Example | 2026-09-14 |

East Library intentionally has no overdue loans in this dataset.

## Files expected alongside the dataset

The dataset uses terms from the latest Library ontology and refers to the controlled-value IRIs defined in `library_concept_schemes.ttl`, such as `lib:AVAILABLE`, `lib:ON_LOAN`, `lib:IN_CIRCULATION`, and `lib:WITHDRAWN`.
