# OncoReconcile AI

## Human-Governed Oncology Entity Reconciliation Platform

OncoReconcile AI is a human-governed oncology entity reconciliation platform that transforms heterogeneous cancer types, genes, and variants into trusted canonical oncology concepts through explainable reconciliation, evidence discovery, adaptive external knowledge retrieval, confidence scoring, provenance tracking, and expert review workflows.

This project is being developed for the **DFWIT AI & Startup Competition 2026** by **Team Variant Vanguard**.

---

## One-Sentence MVP

OncoReconcile AI transforms messy oncology entities into trusted canonical oncology concepts using deterministic reconciliation, evidence discovery, adaptive external evidence retrieval, confidence scoring, explainability, provenance tracking, and human-governed review.

---

## Problem

Real-world oncology data often uses inconsistent names for the same concept.

### Examples

| Messy Input | Canonical Concept |
|---|---|
| NSCLC | Lung Non-Small Cell Carcinoma |
| LUAD | Lung Adenocarcinoma |
| HER2 / HER-2 | ERBB2 |
| HER1 | EGFR |
| p53 | TP53 |
| EGFR Ex19del | EGFR Exon 19 Deletion |
| HER2 Amplification | ERBB2 Amplification |

These inconsistencies make it difficult to support:

- Data harmonization
- Cohort creation
- Evidence aggregation
- Multi-vendor data integration
- Population analytics
- Precision oncology workflows
- AI-ready oncology datasets

---

## Solution

OncoReconcile AI provides a trusted oncology reconciliation layer that:

- Normalizes disease names
- Normalizes gene names
- Normalizes variant names
- Preserves ambiguity when uncertainty exists
- Discovers supporting evidence
- Retrieves external evidence when needed
- Generates explainable reconciliation decisions
- Maintains provenance and audit trails
- Supports human review and governance
- Enables benchmark-driven validation

Rather than forcing uncertain mappings, the platform routes ambiguous cases to expert review.

---

## MVP Scope

### In Scope

#### Reconciliation

- Cancer type reconciliation
- Gene reconciliation
- Variant reconciliation
- Exact matching
- Alias matching
- Fuzzy matching

#### Explainability

- Deterministic explanations
- Confidence scoring
- Confidence breakdown
- Alternatives considered

#### Evidence

- Local evidence retrieval
- Candidate evidence discovery
- Disease-gene context validation
- Curated variant catalog validation
- Adaptive MyVariant.info evidence retrieval

#### Governance

- Persistent human review queue
- Approve workflow
- Reject workflow
- Edit workflow
- Reviewer notes
- Reopen workflow
- Duplicate review prevention

#### Validation

- Benchmark validation framework
- Benchmark dashboard
- CSV upload
- Manual JSON/API input
- CSV and JSON output

---

### Out of Scope for MVP

- PDF extraction
- OCR
- Therapy recommendation
- Clinical decision support
- Clinical interpretation
- Drug recommendation
- Trial matching
- GraphRAG
- Production-grade knowledge graph
- Autonomous clinical decision-making

---

## MVP Workflow

```text
Input
↓
Text Normalization
↓
Cancer Type Reconciliation
↓
Gene Reconciliation
↓
Variant Reconciliation
↓
Cat-VRS-Inspired Ambiguity Detection
↓
Local Knowledge Validation
↓
Candidate Evidence Discovery
↓
Confidence Scoring
↓
Adaptive External Evidence Retrieval (MyVariant)
↓
Evidence Aggregation
↓
Review Recommendation
↓
Human Review Queue
↓
Audit Trail
↓
Benchmark Validation
↓
Output
````

---

## Current MVP Capabilities

Implemented and verified:

### Reconciliation

* Disease reconciliation
* Gene reconciliation
* Variant reconciliation
* Exact matching
* Alias matching
* Fuzzy matching

### Explainability

* Deterministic explanations
* Confidence scoring
* Confidence breakdown
* Alternatives considered

### Evidence

* Local evidence retrieval
* Candidate evidence discovery
* Disease-gene context validation
* Curated variant catalog validation
* Adaptive MyVariant.info evidence retrieval

### Governance

* Persistent human review queue
* Approve workflow
* Reject workflow
* Edit workflow
* Reviewer notes
* Reopen workflow
* Duplicate review prevention

### Validation

* Benchmark validation framework
* Benchmark dashboard
* CSV upload
* Manual API input
* CSV and JSON output

---

## Output Status Categories

Every input record ends in one of three states.

| Status           | Meaning                                        |
| ---------------- | ---------------------------------------------- |
| AUTO_RECONCILE   | High-confidence reconciliation                 |
| REVIEW_REQUIRED  | Ambiguous or evidence-supported reconciliation |
| CANNOT_RECONCILE | No reliable reconciliation found               |

### AUTO_RECONCILE Example

```text
NSCLC + HER2 + Amplification
↓
ERBB2 Amplification
```

### REVIEW_REQUIRED Examples

```text
NSCLC + TRK + fusion
```

```text
NSCLC + EGFR + C797S
```

### CANNOT_RECONCILE Example

```text
UnknownCancer + RandomGeneXYZ + RandomVariant
```

---

## Evidence and Governance

The MVP uses two evidence layers.

### Local Evidence

* Alias dictionaries
* Disease-gene context catalog
* Curated variant catalog
* Local CIViC candidate rows
* Curated external-reference mappings

### External Evidence

Current implementation:

* MyVariant.info

Future roadmap:

* CIViC API
* ClinVar API
* ClinGen Allele Registry
* NCBI Gene

### Governance Rules

External evidence:

* Supports human review only
* Never directly produces `AUTO_RECONCILE`
* Includes source metadata
* Includes retrieval mode
* Includes timestamp
* Includes external identifiers
* Includes source URLs when available
* Fails gracefully when APIs are unavailable

Review-required cases are persisted in:

```text
data/review_queue.json
```

Review decisions include:

* Approve
* Reject
* Edit
* Reviewer notes
* Reopen

Approved reviews do not automatically modify curated catalogs.

Future catalog promotion remains an explicit governance action.

---

## Live Evidence Example

```bash
curl -X POST http://127.0.0.1:8000/reconcile \
  -H "Content-Type: application/json" \
  -d '{"cancer_type":"NSCLC","gene":"EGFR","variant":"C797S"}'
```

Expected status:

```text
REVIEW_REQUIRED
```

If MyVariant.info is available, the response may include:

```text
retrieval_mode: live_myvariant_api
```

If MyVariant.info is unavailable, reconciliation still succeeds and records:

```text
retrieval_mode: live_myvariant_api_error
```

The case remains routed to human review.

---

## Explainability

Each reconciliation returns:

* Canonical concepts
* Explanation
* Confidence score
* Confidence breakdown
* Evidence sources
* Alternatives considered
* Review recommendation
* Audit history

The platform prioritizes transparency over automation.

---

## Standards Alignment

### Implemented / Inspired

* HGNC-inspired gene normalization
* HGVS-inspired variant normalization
* ClinVar-inspired evidence references
* ClinGen-inspired curation concepts
* Cat-VRS-inspired ambiguity preservation
* VA-Spec-inspired provenance model
* Adaptive external evidence retrieval

### Future Roadmap

* GA4GH VRS integration
* GA4GH Cat-VRS serialization
* GA4GH VA-Spec-compatible export
* HL7 FHIR Genomics interoperability
* mCODE interoperability
* OMOP Oncology interoperability
* CIViC live API integration
* ClinGen Allele Registry integration

> Important: The MVP is inspired by these standards and concepts but does not claim official compliance or certification.

---

## Verification Status

Current automated verification results:

```text
26 tests passed
161 benchmark cases
Frontend production build successful
Backend API verified
Review workflow verified
External evidence retrieval verified
```

Test coverage includes:

* `AUTO_RECONCILE` guardrails
* `REVIEW_REQUIRED` workflows
* Candidate evidence routing
* MyVariant success and failure handling
* Review queue persistence
* Duplicate prevention
* Approve workflows
* Edit workflows
* Reopen workflows

---

## What Makes OncoReconcile AI Different

Most normalization systems stop after terminology mapping.

OncoReconcile AI extends reconciliation with:

* Human-in-the-loop governance
* Ambiguity preservation
* Candidate evidence discovery
* Adaptive external evidence retrieval
* Provenance tracking
* Auditability
* Catalog expansion workflows
* Benchmark-driven validation
* Standards-aligned architecture

The platform is designed as a trusted oncology data quality foundation for future analytics, interoperability, and AI-assisted workflows.

---

## Repository Structure

```text
oncoreconcile-ai/
├── contracts/              # Shared API input/output contracts
├── data/                   # Benchmark cases, aliases, review queue, evidence references
├── backend/                # FastAPI backend
├── frontend/               # React frontend
├── docs/                   # MVP, architecture, weekly plan, decisions
├── demo/                   # Demo script and screenshots
└── .github/                # Issue templates, PR template, CI
```

---

## Quick Start: Backend

Use Python 3.10, 3.11, or 3.12 for the backend.

Avoid Python 3.14 with the current pinned dependencies because `pydantic-core==2.20.1` does not support it.

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
PYTHONPATH=. python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If `python3.12` is not installed, `python3.10` or `python3.11` are also fine.

Open:

```text
http://127.0.0.1:8000/docs
```

Test the API:

```bash
curl -X POST http://127.0.0.1:8000/reconcile \
  -H "Content-Type: application/json" \
  -d '{"cancer_type":"NSCLC","gene":"HER2","variant":"Amplification"}'
```

Run backend tests without requiring internet:

```bash
cd backend
PYTHONPATH=. python -m pytest -q
```

Expected:

```text
26 passed
```

### Backend Troubleshooting

If install fails with `pydantic-core` / `PyO3` and a message like:

```text
Python interpreter version (3.14) is newer than PyO3's maximum supported version
```

delete the backend virtual environment and recreate it with Python 3.10–3.12:

```bash
cd backend
deactivate 2>/dev/null || true
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
PYTHONPATH=. python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## Quick Start: Frontend

```bash
cd frontend
npm install
npm run dev
```

To build the frontend:

```bash
npm run build
```

---

## Development Workflow

### Run Backend

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Run Frontend

```bash
cd frontend
npm run dev
```

### Run Tests

```bash
cd backend
PYTHONPATH=. python -m pytest -q
```

### Build Frontend

```bash
cd frontend
npm run build
```

---

## Team Working Rule

AI can generate code, but humans own:

* API contracts
* MVP scope
* Integration decisions
* Review logic
* Governance logic
* Benchmark quality
* Demo quality

Before coding, read:

1. `docs/mvp.md`
2. `contracts/api_contract.md`
3. `docs/weekly_plan.md`
4. `docs/onboarding.md`

---

## Current Project Status

Estimated completion:

```text
~95%
```

Remaining work:

* Demo polish
* Additional benchmark coverage
* Presentation materials
* Final competition video
* Documentation refinement

---

## Roadmap

### Before Final Submission

* Polish demo workflow
* Add final screenshots
* Expand benchmark examples
* Improve evidence display
* Finalize presentation deck
* Record demo video

### Future

* CIViC live API integration
* ClinVar API integration
* ClinGen Allele Registry integration
* GA4GH VRS objects
* Cat-VRS serialization
* VA-Spec-compatible export
* HL7 FHIR Genomics interoperability
* OMOP Oncology integration
* LLM-assisted reviewer support

---

## License

Competition prototype and research project.

See repository license for details.

```
