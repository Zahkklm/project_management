# Project Gap Analysis: Requirements vs Implementation

## Summary Table

| Requirement                                    | Status         | Notes/Action Needed                                  |
|------------------------------------------------|----------------|------------------------------------------------------|
| Core CRUD/API endpoints                        | Implemented    | Review for completeness and edge cases               |
| S3+Lambda (image resize, file size calc)       | Not confirmed  | Implement or document                                |
| Email invite with hashed token                 | Not implemented| Implement endpoint and email logic                   |
| DB normalization/denormalization               | Not confirmed  | Document or implement                                |
| DB creation without ORM                        | Not confirmed  | Document or implement                                |
| JWT for all business logic (1hr expiry)        | Partially done | Confirm coverage and expiry                          |
| Pydantic validation for all data               | Partially done | Confirm for all endpoints                            |
| CI/CD for package creation (tox/poetry)        | Not confirmed  | Add tox support, package publishing if needed        |
| Test coverage (S3/Lambda, edge cases)          | Not confirmed  | Add/expand tests                                     |
| Proper HTTP status codes, JSON responses       | Partially done | Review and confirm                                   |
| Owner/participant access logic                 | Implemented    | Review for edge cases                                |

---

## Next Steps
- Implement missing endpoints/features (email invite, S3/Lambda logic, DB normalization/denormalization, etc.).
- Review and expand test coverage.
- Confirm JWT, Pydantic, and error handling coverage.
- Add tox support and package publishing if required.
- Review all endpoints for proper status codes and JSON responses.

---

*Generated from `case_requirements.txt` and current codebase analysis.*
