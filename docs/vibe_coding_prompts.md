# Vibe Coding Prompts For Checkpoint 2 / Final MVP

Use these prompts when a team member wants to build quickly with Codex, ChatGPT, or another coding assistant.

Important guardrails for every prompt:

- Do not change fixed input data unless explicitly asked.
- Keep `data/disease_aliases.json`, `data/gene_aliases.json`, `data/gene_variant_catalog.csv`, `data/disease_gene_catalog.csv`, and `data/benchmark_cases.csv` stable.
- Preserve deterministic reconciliation behavior.
- Run backend tests after backend changes:

```bash
cd backend
PYTHONPATH=. pytest -q
```

- Do not add LLM fallback, authentication, database persistence, cloud deployment, Kubernetes, FHIR, or OMOP unless explicitly assigned.

## Prompt 1: Backend Response Contract

```text
You are working in the OncoReconcile AI repo.

Goal: improve the backend reconciliation response contract for Checkpoint 2.

Read:
- backend/app/models.py
- backend/app/reconcile.py
- backend/tests/test_reconcile.py
- docs/checkpoint2_reconciliation_tasks.md

Implement Workstream 1 only:
- add a structured decision object to reconciliation responses
- include matched_by values such as disease_alias, gene_alias, variant_catalog, review_required_rule, cannot_reconcile_rule
- include decision_reason
- include requires_review_reason when review_status is REVIEW_REQUIRED
- include catalog metadata when a variant catalog row is used
- update tests

Constraints:
- do not change fixed data files
- do not change frontend yet
- preserve current benchmark behavior
- keep logic deterministic

Verification:
- run cd backend && PYTHONPATH=. pytest -q

Return:
- files changed
- tests run
- any remaining risks
```

## Prompt 2: Batch API Hardening

```text
You are working in the OncoReconcile AI repo.

Goal: harden POST /reconcile/batch for CSV workflows.

Read:
- backend/app/main.py
- backend/app/models.py
- backend/app/reconcile.py
- backend/tests/test_reconcile.py
- docs/checkpoint2_reconciliation_tasks.md

Implement Workstream 2 only:
- preserve case_id for each row
- add row-level error handling for invalid records
- do not fail the entire batch when one row is invalid
- add invalid_records to batch summary
- ensure summary counts equal total submitted rows
- add tests for valid, invalid, empty, and duplicate row cases

Constraints:
- do not change fixed data files
- do not implement frontend
- keep response easy for CSV upload UI to consume

Verification:
- run cd backend && PYTHONPATH=. pytest -q

Return:
- files changed
- example batch response
- tests run
```

## Prompt 3: Benchmark Evaluation Script

```text
You are working in the OncoReconcile AI repo.

Goal: create a benchmark evaluation script for final submission evidence.

Read:
- data/benchmark_cases.csv
- backend/app/reconcile.py
- backend/app/models.py
- backend/tests/test_reconcile.py

Implement Workstream 3:
- create scripts/evaluate_benchmark.py
- load data/benchmark_cases.csv
- run each row through reconcile_record()
- print total cases
- print disease accuracy
- print gene accuracy
- print variant accuracy
- print review status accuracy
- print exact full-row accuracy
- print failed cases with expected vs actual
- optionally write data/benchmark_results.csv

Constraints:
- do not change benchmark_cases.csv
- do not change reconciliation logic unless a clear bug is found

Verification:
- run python scripts/evaluate_benchmark.py
- run cd backend && PYTHONPATH=. pytest -q

Return:
- sample output
- files changed
```

## Prompt 4: Demo Dataset

```text
You are working in the OncoReconcile AI repo.

Goal: create a small demo CSV for final presentation.

Read:
- data/benchmark_cases.csv
- data/gene_variant_catalog.csv
- docs/checkpoint2_reconciliation_tasks.md

Implement Workstream 10:
- create data/demo_cases.csv
- include 30-50 records
- columns must be case_id,cancer_type,gene,variant
- include AUTO_RECONCILE, REVIEW_REQUIRED, and CANNOT_RECONCILE cases
- include common examples like HER2 amplification, EGFR Ex19del, TP53 R175H, TRK fusion, unknown_gene

Then verify each row by calling reconcile_record() or /reconcile/batch.

Constraints:
- do not change fixed data files
- demo file should be simple and presentation-friendly

Return:
- status count summary
- any rows that do not behave as expected
```

## Prompt 5: Frontend CSV Upload

```text
You are working in the OncoReconcile AI repo.

Goal: add CSV upload for batch reconciliation.

Read:
- frontend/src/main.jsx
- frontend/src/style.css
- backend/app/main.py
- docs/checkpoint2_reconciliation_tasks.md

Implement Workstream 4 only:
- add CSV upload control
- accept columns case_id,cancer_type,gene,variant
- parse CSV in the frontend
- validate required columns
- send rows to POST /reconcile/batch
- display upload errors before submitting
- show batch summary
- render one result row per input

Constraints:
- do not add a new UI framework
- current frontend uses React, Vite, and CSS
- keep UI clear and demo-friendly
- do not change backend unless absolutely required

Verification:
- run npm run build in frontend
- if possible, start backend/frontend and test data/demo_cases.csv

Return:
- local URL if dev server runs
- files changed
- any manual test steps
```

## Prompt 6: Metrics Dashboard

```text
You are working in the OncoReconcile AI repo.

Goal: add a simple judge-friendly metrics dashboard above batch results.

Read:
- frontend/src/main.jsx
- frontend/src/style.css
- docs/checkpoint2_reconciliation_tasks.md

Implement Workstream 11:
- show dashboard cards for uploaded records, AUTO_RECONCILE, REVIEW_REQUIRED, CANNOT_RECONCILE, invalid rows
- use consistent colors with status badges
- update counts after batch reconciliation
- keep it simple and readable for a live demo

Constraints:
- do not add chart libraries unless already installed
- no backend changes unless required
- avoid decorative overdesign

Verification:
- run npm run build
- manually test with data/demo_cases.csv if dev server is available

Return:
- files changed
- screenshot/test notes if available
```

## Prompt 7: Results Table And Filters

```text
You are working in the OncoReconcile AI repo.

Goal: improve the batch results table for review workflow.

Read:
- frontend/src/main.jsx
- frontend/src/style.css
- docs/checkpoint2_reconciliation_tasks.md

Implement Workstream 5:
- add columns for input disease/gene/variant
- add columns for canonical disease/gene/variant
- add confidence and review status badges
- add decision reason if backend provides it; otherwise use explanation
- add filters for all, AUTO_RECONCILE, REVIEW_REQUIRED, CANNOT_RECONCILE, invalid rows
- add row expansion for evidence, notes, and audit trail

Constraints:
- do not introduce a table library unless necessary
- keep table readable for 30-100 rows
- preserve existing manual single-record form

Verification:
- run npm run build
- test with data/demo_cases.csv if available

Return:
- files changed
- manual test notes
```

## Prompt 8: Human Review Queue

```text
You are working in the OncoReconcile AI repo.

Goal: add a lightweight human review queue for REVIEW_REQUIRED rows.

Read:
- frontend/src/main.jsx
- frontend/src/style.css
- docs/checkpoint2_reconciliation_tasks.md

Implement Workstream 6:
- add a review-only view filtered to REVIEW_REQUIRED rows
- allow reviewer actions:
  - approve suggested canonical values
  - modify canonical gene
  - modify canonical variant
  - mark cannot reconcile
  - add reviewer note
- store reviewer decisions in frontend state
- preserve original system recommendation

Constraints:
- no backend persistence for now
- no authentication
- no database
- keep workflow demo-ready and simple

Verification:
- run npm run build
- manually review at least one REVIEW_REQUIRED demo row

Return:
- files changed
- how reviewer decisions are represented in state
```

## Prompt 9: CSV Export

```text
You are working in the OncoReconcile AI repo.

Goal: add CSV export for reconciled and reviewed results.

Read:
- frontend/src/main.jsx
- frontend/src/style.css
- docs/checkpoint2_reconciliation_tasks.md

Implement Workstream 7, CSV export only:
- export original input values
- export canonical output values
- export confidence
- export review status
- export explanation or decision reason
- export reviewer action and reviewer note if available

Constraints:
- CSV export is required
- JSON export is nice-to-have but can be skipped
- no backend persistence

Verification:
- run npm run build
- manually export data/demo_cases.csv results and inspect downloaded CSV

Return:
- files changed
- exported columns
```

## Prompt 10: Explainability Polish

```text
You are working in the OncoReconcile AI repo.

Goal: make explanation text more specific and useful.

Read:
- backend/app/explain.py
- backend/app/reconcile.py
- backend/tests/test_reconcile.py
- docs/checkpoint2_reconciliation_tasks.md

Implement Workstream 8:
- use evidence types directly
- create clear templates for disease alias, gene alias, variant catalog, ambiguous gene, generic variant, cannot reconcile
- avoid vague wording like "one or more entities"
- add tests for AUTO_RECONCILE, REVIEW_REQUIRED, and CANNOT_RECONCILE explanation text

Constraints:
- explanations must be deterministic
- no external API calls
- no LLM calls
- do not change fixed data files

Verification:
- run cd backend && PYTHONPATH=. pytest -q

Return:
- before/after explanation examples
- files changed
```

## Prompt 11: Competition Metrics Script

```text
You are working in the OncoReconcile AI repo.

Goal: create judge-friendly final competition metrics.

Read:
- scripts/evaluate_benchmark.py if it exists
- data/benchmark_cases.csv
- backend/app/reconcile.py
- docs/checkpoint2_reconciliation_tasks.md

Implement Workstream 12:
- create scripts/generate_competition_metrics.py
- print benchmark cases count
- print disease accuracy
- print gene accuracy
- print variant accuracy
- print review status accuracy
- print review escalation accuracy
- print exact full-row accuracy
- write optional data/competition_metrics.json
- make output copy-paste friendly for slides

Constraints:
- do not inflate metrics
- if a metric is less than 100%, show the real value
- failed cases should be inspectable

Verification:
- run python scripts/generate_competition_metrics.py
- run cd backend && PYTHONPATH=. pytest -q

Return:
- sample output
- files changed
```

## Prompt 12: Business Case Document

```text
You are working in the OncoReconcile AI repo.

Goal: create the business value document for final competition submission.

Read:
- docs/final_submission_draft.md
- docs/checkpoint2_reconciliation_tasks.md

Implement Workstream 13:
- create docs/business_case.md
- describe target users
- describe benefits
- describe future revenue paths
- explain why human-governed reconciliation matters
- keep claims focused on data quality, not treatment recommendations

Target users:
- cancer centers
- molecular diagnostics labs
- healthcare systems
- research organizations
- pharmaceutical companies
- real-world evidence platforms
- healthcare AI startups

Return:
- created file path
- 5 bullet summary for pitch slides
```

## Prompt 13: Final Demo Script

```text
You are working in the OncoReconcile AI repo.

Goal: create a clear final demo script for a 5-7 minute judge presentation.

Read:
- docs/final_submission_draft.md
- docs/checkpoint2_reconciliation_tasks.md
- data/demo_cases.csv if it exists

Implement Workstream 14:
- create docs/final_demo_script.md
- structure the demo by minute:
  - minute 1: problem
  - minute 2: architecture
  - minute 3: upload CSV
  - minute 4: review queue
  - minute 5: export results
  - minute 6: benchmark validation
  - minute 7: business value and roadmap
- include exact commands to start backend and frontend
- include exact demo inputs
- include fallback talking points if live demo fails

Return:
- created file path
- short rehearsal checklist
```

## Prompt 14: Final MVP Polish Pass

```text
You are working in the OncoReconcile AI repo.

Goal: do a final MVP polish pass without expanding scope.

Read:
- docs/final_submission_draft.md
- docs/checkpoint2_reconciliation_tasks.md
- README.md
- README_data_scripts.md
- backend/app/main.py
- frontend/src/main.jsx

Check:
- docs reference current data files only
- quick start commands work
- frontend examples match backend behavior
- final demo flow is documented
- tests pass
- no claims about treatment recommendations or autonomous clinical AI

Do not:
- add new major features
- add LLM fallback
- add database persistence
- add auth
- add cloud deployment

Verification:
- cd backend && PYTHONPATH=. pytest -q
- cd frontend && npm run build

Return:
- concise release readiness checklist
- blockers, if any
```
