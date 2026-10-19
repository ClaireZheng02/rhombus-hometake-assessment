# Rhombus AI — LLM Observability & Quality Assurance Assessment

## 1. Executive Summary

This project evaluates the reliability, data quality, and observability of an AI-assisted ETL pipeline built using Rhombus AI.

The pipeline processes order data from AWS S3, applies deduplication and AI-generated cleaning logic, and exports the results to Google Cloud Storage (GCS).

The assessment combines seven drift scenarios, automated data validation, Playwright UI testing, and API testing to investigate how the system behaves under changing data conditions.

**Key findings:**

- A successful pipeline execution does not necessarily guarantee correct output data.
- Combined schema changes led to an incorrect AI-generated field mapping, corrupting region values in 18 records.
- A price-unit change caused output prices to increase by a factor of 100.
- A date-format change resulted in incorrect day/month interpretation in 18 of 20 records.
- Automated Python validation detected these data-quality issues.

A total of **24 automated test cases** were executed successfully across data validation, UI testing, and API testing. However, the scope and limitations of each test category are distinguished throughout this report.

The central finding is that **execution-level observability should be complemented by semantic data-quality validation, particularly when transformations rely on AI-generated code.**

## 2. System Architecture

### 2.1 Pipeline Overview

The ETL pipeline consists of the following stages:

**AWS S3 → Data Input → Remove Duplicates → Custom AI-Generated Cleaning → GCS Output**

| Component | Purpose |
|---|---|
| AWS S3 | Stores the source CSV dataset |
| Rhombus AI Data Input | Retrieves the input data |
| Remove Duplicates | Removes duplicate order records |
| Custom Cleaning | Applies AI-generated Python data-cleaning logic |
| Google Cloud Storage | Stores the processed CSV output |

**Workflow:** https://rhombusai.com/workflow/5346

**Source S3 bucket:** `rhombus-ai-etl-test-20261016-01`

**Output GCS bucket:** `rhombus-etl-output-20261016-01`

### 2.2 Baseline Dataset

The original dataset contains 24 records and 7 columns.

The baseline cleaning process removes duplicate and invalid records, standardises selected fields, and produces 20 records with 7 columns.

The expected output was independently validated using Python and Pandas.

## 3. Quality Assurance Strategy

The testing approach was designed around four quality dimensions.

| Dimension | Testing Approach | Primary Risk |
|---|---|---|
| Data correctness | Pandas and pytest | Incorrect or incomplete output |
| Schema and semantic robustness | Controlled drift scenarios | Silent data corruption |
| UI reliability | Playwright and Edge | Incorrect or inaccessible workflow configuration |
| API behaviour | Authenticated and unauthenticated requests | Unexpected responses or insufficient access control |

Two complementary testing methods were used.

**Behavioural testing:** Introduce controlled changes to the input dataset and observe how the pipeline responds.

**Automated validation:** Use independent Python assertions to compare actual outputs with expected data-quality rules.

This distinction is important because a pipeline may complete successfully while producing incorrect business values.

## 4. Drift Testing

Seven drift scenarios were investigated: five schema changes and two semantic changes.

### 4.1 Schema Drift Test Matrix

| Scenario | Test Objective | Observed Result |
|---|---|---|
| Column Removal | Evaluate behaviour when a required field is missing | Executed; detailed outcome requires further documentation |
| Column Renaming | Evaluate adaptation to renamed fields | Executed; detailed outcome requires further documentation |
| Data Type Change | Evaluate handling of unexpected numeric values | Two invalid price records were excluded; output contained 18 records |
| Additional Column | Evaluate handling of an unexpected field | The new field was not retained; output remained at 7 columns |
| Combined Schema Changes | Evaluate multiple structural changes simultaneously | Incorrect field mapping corrupted region values in 18 records |

The first two scenarios are retained in the test inventory, but their detailed outcomes are not presented as independently verified findings without supporting records.

### 4.2 Semantic Drift Test Matrix

| Scenario | Expected Behaviour | Observed Result |
|---|---|---|
| USD to Cents | Preserve the intended monetary value despite changes in representation | Output prices increased by 100× |
| Date Format Change | Preserve the intended calendar dates | Day/month interpretation changed in 18 of 20 records |

Both semantic drift scenarios were subsequently checked using automated Python tests.

## 5. Critical Findings

### Finding 1 — Incorrect AI-Generated Field Mapping

**Scenario:** Combined Schema Drift

**Expected behaviour**

The pipeline should preserve the semantic meaning of existing fields when the input schema changes. Ambiguous mappings should be identified rather than silently applied.

**Observed behaviour**

During the combined schema-change scenario, an AI-assisted code modification incorrectly mapped `customer_segment` to `region`.

As a result, the `region` field contained incorrect values in 18 output records, despite the pipeline reporting a successful execution.

**Why this matters**

The output retained a usable structure, which made the problem less obvious than an execution failure.

Downstream reports or analytics could therefore process corrupted regional information without immediately detecting the error.

**Recommended improvement**

Introduce field-level mapping validation and regression testing before accepting AI-generated code modifications.

Critical business fields should be checked against explicit schema contracts and allowed values.

### Finding 2 — Monetary Unit Misinterpretation

**Scenario:** Semantic Drift — USD to Cents

**Expected behaviour**

Changing the input representation from dollars to cents should not change the actual monetary value represented by each record.

**Observed behaviour**

Output prices were 100 times the baseline values.

The pipeline processed the numeric values without preserving the intended unit semantics.

**Why this matters**

The values remained numerically valid, meaning ordinary type checks and positive-value assertions could not independently identify the error.

**Recommended improvement**

Introduce unit-aware validation and monitoring of price distributions.

Unexpected changes in price magnitude should trigger a warning or require further verification.

### Finding 3 — Incorrect Date Interpretation

**Scenario:** Semantic Drift — Date Format Change

**Expected behaviour**

Dates should retain their intended meaning when the source representation changes.

**Observed behaviour**

A date-format change resulted in incorrect day/month interpretation in 18 of 20 output records.

Automated validation confirmed the day/month swap pattern.

**Why this matters**

Incorrectly parsed dates may remain syntactically valid, making them difficult to detect through schema validation alone.

**Recommended improvement**

Use explicit date-format specifications and validate parsed dates against known source values and business expectations.

## 6. Automated QA Results

### 6.1 Data Validation — 16 Tests

Automated tests were developed using Python, Pandas, and pytest.

| Test Group | Number of Tests | Result |
|---|---:|---|
| Baseline Data Quality | 5 | Passed |
| Row-Level Reconciliation | 2 | Passed |
| Price Semantic Drift | 2 | Passed |
| Date Semantic Drift | 3 | Passed |
| Historical Output Consistency | 4 | Passed |
| **Total** | **16** | **16 Passed** |

The complete data-validation suite was rerun successfully in GitHub Codespaces.

The semantic drift tests are detection tests. Their successful execution demonstrates that the specified anomalies were identified, not that the pipeline handled those changes correctly.

### 6.2 UI Automation — 6 Tests

Playwright with Microsoft Edge was used to test:

1. Workflow visibility and navigation.
2. AWS S3 data-source configuration.
3. GCS output-destination configuration.
4. AI Custom Builder controls.
5. Schedule configuration.
6. Historical execution status.

All six tests passed during the original Windows-based test execution.

These tests primarily validate workflow configuration and interface behaviour. They do not automate pipeline creation, execution, and output verification as one complete end-to-end journey.

The historical execution test may no longer pass because the previously available execution records were cleared.

### 6.3 API Testing — 2 Tests

**Endpoint:** `GET /api/accounts/users/credits`

**Positive test**

An authenticated application request returned HTTP 200 and a non-empty JSON response containing the fields:

- `balance`
- `tier_info`
- `topup_packages`

**Negative test**

An unauthenticated request returned HTTP 401, demonstrating that the endpoint rejected the unauthenticated request.

**Result: 2 tests passed during the original local execution.**

These tests cover a supporting account API rather than an ETL-specific execution endpoint.

## 7. Observability Assessment

### 7.1 Execution Success vs Data Correctness

The most important observation from the drift experiments is that pipeline success does not necessarily indicate data correctness.

In several scenarios, the pipeline completed while producing semantically incorrect values.

This reveals a gap between two distinct forms of observability:

**Operational observability** monitors whether a pipeline runs, completes, or fails.

**Data-quality observability** monitors whether the output remains accurate, meaningful, and consistent with business expectations.

Both are necessary for reliable AI-assisted ETL systems.

### 7.2 Risks Associated with AI-Generated Transformations

AI-generated cleaning code can help adapt pipelines to changing input structures.

However, an automatically generated modification may also introduce new errors, particularly when the relationship between fields is ambiguous.

The incorrect `customer_segment` to `region` mapping illustrates this risk.

AI-generated modifications should therefore be treated as changes requiring validation, not as inherently correct repairs.

### 7.3 Recommended Monitoring Improvements

The following controls are proposed as future improvements; they were not implemented as live production monitoring features in this assessment.

| Monitoring Area | Proposed Control |
|---|---|
| Schema changes | Detect missing, renamed, and newly introduced fields |
| Field mappings | Validate mappings against explicit business rules |
| Numerical values | Monitor distributions and expected units |
| Date fields | Validate formatting and semantic interpretation |
| AI-generated code | Track code changes and run regression tests |
| Pipeline execution | Link execution status with output-quality checks |
| Traceability | Preserve input versions, code versions, execution IDs, and output artifacts |

A useful next step would be to place automated semantic validation immediately after the cleaning transformation and before downstream data consumption.

## 8. Reproducibility

### 8.1 Repository Structure

| Directory | Contents |
|---|---|
| `data-validation/` | Python data-quality and drift-validation tests |
| `datasets/` | Original, baseline, drift, and comparison CSV files |
| `ui-tests/` | Playwright UI test implementations |
| `api-tests/` | API positive and negative tests |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Exclusions for local and sensitive files |

### 8.2 Environment Setup

Create and activate a Python virtual environment.

On Linux or GitHub Codespaces:

`python -m venv .venv`

`source .venv/bin/activate`

Install the dependencies:

`python -m pip install -r requirements.txt`

### 8.3 Run Data Validation

Run the complete offline data-validation suite from the repository root:

`python -m pytest data-validation -v`

This suite uses saved CSV datasets and does not require access to the live Rhombus AI workflow.

### 8.4 UI and API Test Requirements

The UI and authenticated API tests were originally executed on Windows using Microsoft Edge.

Authenticated tests require a valid Playwright session state at:

`.auth/state.json`

This file contains sensitive authentication information and is intentionally excluded from Git.

Reviewers must establish their own authorised session before rerunning authenticated tests.

Some tests additionally depend on the current application configuration and availability of historical execution records.

### 8.5 Test Evidence

The repository includes the saved datasets and Python test implementations used for offline validation.

Supporting screenshots and execution evidence should be added to `observations/evidence/` where available.

Historical screenshots should be distinguished from current test results, especially when the underlying application state has changed.

## 9. Limitations

The following limitations should be considered when interpreting the results.

**Historical execution records**

Execution history was no longer available during the final review, preventing independent verification of the configurations used for two historical outputs.

**Determinism**

Four automated comparisons confirmed that the two saved output datasets were identical and matched the baseline.

However, because identical input and pipeline configurations could not be independently established, execution-level determinism remains unverified.

**UI automation coverage**

The UI tests focus on navigation, configuration visibility, and historical execution information rather than complete end-to-end pipeline automation.

**API coverage**

API tests verify authenticated and unauthenticated behaviour for one accessible account endpoint. They do not establish comprehensive ETL API coverage.

**Drift-test evidence**

Some historical drift observations have stronger saved output evidence than others. Outcomes without sufficient supporting evidence are not presented as fully verified findings.

**LLM-specific telemetry**

The assessment examines the reliability of AI-generated transformation code but does not measure model-level metrics such as token usage, prompt versions, inference latency, or model response quality over repeated generations.

## 10. Engineering Recommendations

Based on the observed failures, three improvements should be prioritised.

**Priority 1 — Semantic validation after AI-generated transformations**

Validate critical mappings, monetary units, date interpretation, and business rules before accepting processed output.

**Priority 2 — Regression testing for AI-generated code changes**

Compare outputs before and after generated code modifications, using representative baseline datasets and known edge cases.

**Priority 3 — Stronger execution traceability**

Preserve execution identifiers, input versions, generated code versions, and output artifacts to support failure investigation and reproducibility.

Together, these improvements would help detect silent data-quality failures that cannot be identified through execution status alone.

## 11. Conclusion

This assessment demonstrates the importance of combining functional testing, data-quality validation, and observability when evaluating AI-assisted ETL workflows.

The most significant risks were not pipeline crashes, but successful executions that produced incorrect business values.

The automated tests provided repeatable evidence for the observed price, date, and output-consistency behaviours, while UI and API tests contributed additional coverage of application functionality and access control.

The key engineering lesson is that **reliable AI-assisted data pipelines require validation of what the system produces, not only whether it completes successfully.**