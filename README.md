# OncoReconcile AI

## Human-Governed Oncology Reconciliation Workbench

OncoReconcile AI transforms messy oncology entities into canonical oncology candidates with evidence, explainability, confidence scoring, and human-governed review.

This project is being developed for the DFWIT AI & Startup Competition by Team Variant Vanguard.

---

## One-Sentence MVP

OncoReconcile AI is a human-governed oncology reconciliation workbench that transforms messy cancer types, genes, and variants into trusted canonical oncology concepts with evidence, explainability, confidence scoring, and review recommendations.

---

## Problem

Real-world oncology data often uses inconsistent names for the same concept.

Examples:

| Messy Input | Canonical Concept |
|---|---|
| NSCLC | Non-Small Cell Lung Cancer |
| LUAD | Lung Adenocarcinoma |
| HER2 / HER-2 | ERBB2 |
| p53 | TP53 |
| EGFR Ex19del | EGFR Exon 19 Deletion |
| HER2 Amplification | ERBB2 Amplification |

These inconsistencies make it difficult to support:

- Data harmonization
- Cohort creation
- Evidence aggregation
- Multi-vendor data integration
- Population analytics
- AI-ready oncology datasets

---

## MVP Scope

### In Scope

- CSV upload
- Manual JSON/API input
- Cancer type reconciliation
- Gene reconciliation
- Variant reconciliation
- Local and live external evidence context
- Deterministic explanation with an optional review-only LLM suggestion
- Confidence scoring
- Persistent human review queue
- Curator approve, reject, edit, note, and reopen actions
- Benchmark validation dashboard
- Result table
- CSV/JSON output

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

---

## MVP Workflow

```text
Input
↓
Cancer Type Reconciliation
↓
Gene Reconciliation
↓
Variant Reconciliation
↓
Canonical Oncology Concept
↓
Local Evidence Retrieval
↓
Adaptive MyVariant.info Evidence Retrieval (when needed)
↓
Deterministic Explanation
↓
Confidence Recommendation
↓
Review Recommendation
↓
Human Review Queue
↓
Output
```

---

## Output Status Categories

Every input record should end in one of three states:

| Status | Meaning |
|---|---|
| AUTO_RECONCILE | High-confidence match |
| REVIEW_REQUIRED | Ambiguous or medium-confidence match |
| CANNOT_RECONCILE | No reliable match found |

---

## Evidence And Governance

The MVP uses two evidence layers:

- **Local evidence:** alias dictionaries, disease-gene context, curated variant catalog, local CIViC candidate rows, and curated external-reference mappings.
- **Live external evidence:** advisory MyVariant.info lookup for unresolved or review-required gene/variant inputs.

Live external evidence:

- supports human review only
- never directly produces `AUTO_RECONCILE`
- includes source, retrieval mode, timestamp, external ID, and source URL when available
- fails gracefully with an error evidence record when the API is unavailable

Review-required responses are persisted in:

```text
data/review_queue.json
```

The same input uses a stable review key when no `case_id` is supplied, preventing duplicate queue records. Approve, reject, edit, reviewer notes, and reopen decisions are also persisted.

Approved reviews do not automatically modify `data/gene_variant_catalog.csv`. A disabled `promote_candidate_to_catalog()` roadmap stub makes catalog promotion an explicit future governance action.

Standards language:

- The evidence and audit model is **VA-Spec-inspired**, not VA-Spec compliant.
- The ambiguity-preservation layer is **Cat-VRS-inspired**, not an official Cat-VRS implementation.

---

## Live Evidence Example

```bash
curl -X POST http://127.0.0.1:8000/reconcile \
  -H "Content-Type: application/json" \
  -d '{"cancer_type":"NSCLC","gene":"EGFR","variant":"C797S"}'
```

Expected status: `REVIEW_REQUIRED`.

If MyVariant.info is available, the response includes evidence with:

```text
retrieval_mode: live_myvariant_api
```

If it is unavailable, reconciliation still succeeds and records:

```text
retrieval_mode: live_myvariant_api_error
```

---

## Repository Structure

```text
oncoreconcile-ai/
├── contracts/              # Shared API input/output contracts
├── data/                   # Benchmark cases and alias dictionaries
├── backend/                # FastAPI backend skeleton
├── frontend/               # React frontend skeleton
├── docs/                   # MVP, architecture, weekly plan, decisions
├── demo/                   # Demo script and screenshots
└── .github/                # Issue templates, PR template, CI
```

---

## Quick Start: Backend

Use Python 3.10, 3.11, or 3.12 for the backend. Avoid Python 3.14 with the
current pinned dependencies because `pydantic-core==2.20.1` does not support it.

```bash
cd backend
python3.10 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
PYTHONPATH=. python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If `python3.10` is not installed, `python3.11` or `python3.12` are also fine.
The key is to create the virtual environment with one of those versions.

Open:

```text
http://127.0.0.1:8000/docs
```

Test:

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

Troubleshooting:

If install fails with `pydantic-core` / `PyO3` and a message like
`Python interpreter version (3.14) is newer than PyO3's maximum supported version`,
delete the backend virtual environment and recreate it with Python 3.10-3.12:

```bash
cd backend
deactivate 2>/dev/null || true
rm -rf .venv
python3.10 -m venv .venv
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

---

## Team Working Rule

AI can generate code, but humans own:

- API contracts
- MVP scope
- integration
- review logic
- demo quality

Before coding, read:

1. `docs/mvp.md`
2. `contracts/api_contract.md`
3. `docs/weekly_plan.md`
4. `docs/onboarding.md`

---

## This Week's Goal

Build one working vertical slice:

```text
CSV/manual input
↓
Backend reconciliation
↓
Result table
```

One working record is better than five disconnected components.
