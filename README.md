# OncoReconcile AI

## Human-Governed Oncology Reconciliation Workbench

OncoReconcile AI transforms messy oncology entities into trusted canonical oncology concepts with evidence, explainability, confidence scoring, and human review recommendations.

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
- Evidence context
- AI-generated explanation
- Confidence scoring
- Review recommendation
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
Evidence Retrieval
↓
AI Explanation
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
