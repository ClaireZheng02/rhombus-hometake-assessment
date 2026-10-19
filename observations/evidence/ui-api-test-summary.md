
# UI and API Test Evidence

## 1. Test Environment

- Operating System: Windows
- Browser: Microsoft Edge
- Automation Framework: Playwright
- Test Runner: pytest
- Target Workflow: https://rhombusai.com/workflow/5346

Tests were originally executed locally using an
authenticated browser session.

## 2. UI Test Results

Six UI tests passed during the original local runs.

| Test | Original Result |
|---|---|
| Workflow Navigation | PASS |
| S3 Source Configuration | PASS |
| GCS Destination Configuration | PASS |
| AI Custom Builder Controls | PASS |
| Schedule Configuration | PASS |
| Execution History | PASS |

The tests verified workflow visibility,
configuration details, and historical status.

The original execution-history test verified
Execution #18420 with a Success status.

However, the execution history was subsequently
cleared. This historical test result cannot
currently be reproduced against the same record.

These tests do not represent complete end-to-end
automation of pipeline creation and execution.

## 3. API Test Results

Endpoint:
GET https://api.rhombusai.com/api/accounts/users/credits

### Positive Test

- Authenticated request
- HTTP status: 200
- Response format: JSON
- Observed fields:
  - balance
  - tier_info
  - topup_packages

Result: PASS

### Negative Test

- Unauthenticated request
- HTTP status: 401
- Access rejected as expected

Result: PASS

## 4. Evidence Limitations

This document summarises results observed during
earlier local test executions.

It is not a newly generated pytest execution log.

The original authenticated session is intentionally
excluded from the GitHub repository for security.

The API tests cover an account-related endpoint,
not a dedicated ETL execution API.

The original UI/API results should not be interpreted
as confirmation that all tests still pass against
the current application state.
