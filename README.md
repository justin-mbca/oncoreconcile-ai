# OncoReconcile AI

## Human-Governed AI Platform for Oncology Data Quality, Harmonization, and Curation

OncoReconcile AI reconciles inconsistent cancer-type, gene, and variant terminology into explainable canonical candidates. It combines deterministic matching, advisory evidence retrieval, confidence scoring, provenance, and governed expert review.

Built for the **DFWIT AI & Startup Competition 2026** by **Team Variant Vanguard**.

## Why It Matters

Oncology data often represents the same concept in different ways:

| Input | Canonical concept |
|---|---|
| NSCLC | Lung Non-Small Cell Carcinoma |
| LUAD | Lung Adenocarcinoma |
| HER2 / HER-2 | ERBB2 |
| HER1 | EGFR |
| p53 | TP53 |
| Ex19del | EGFR Exon 19 Deletion |

These inconsistencies complicate cohort creation, evidence aggregation, analytics, and the preparation of trustworthy AI-ready datasets.

## Current MVP

- Disease, gene, and variant reconciliation
- Exact, alias, and fuzzy matching
- Safe ambiguity preservation
- Three outcomes: `AUTO_RECONCILE`, `REVIEW_REQUIRED`, and `CANNOT_RECONCILE`
- Deterministic explanations, confidence scores, alternatives, and audit trails
- Advisory MyVariant.info, ClinVar, CIViC, and ClinGen Allele Registry retrieval
- Persistent human review queue with stable keys and duplicate prevention
- Review history, agreement metrics, Cohen's kappa, disagreement detection, and adjudication
- PROV-O-inspired provenance export
- JSON-LD knowledge graph prototype
- VRS-ready, Cat-VRS-ready, and VA-Spec-ready export stubs
- Curation metadata and combined curation report

External evidence never creates a high-confidence automatic decision by itself. Uncertain or externally supported candidates remain subject to human review.

## Validation Status

| Metric | Value |
|---|---|
| Backend Tests | 43 passed |
| Benchmark Cases | 191 |
| Frontend Build | Passed |
| MyVariant Integration | Implemented |
| ClinVar Integration | Implemented |
| CIViC Integration | Implemented |
| ClinGen Allele Registry Integration | Implemented |
| Knowledge Graph Export | Implemented prototype |
| Reviewer Agreement Metrics | Implemented |
| Adjudication Workflow | Implemented |

Verified on June 20, 2026.

## Safety and Scope

OncoReconcile AI is a human-governed data harmonization prototype. It does not provide clinical interpretation, treatment recommendations, or autonomous clinical decision support. Standards-related outputs are standards-inspired prototypes or export stubs, not official GA4GH, FHIR, OMOP, or RDF compliance.

## Quick Start

Backend:

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Validation:

```bash
python -m pytest -q
cd frontend && npm run build
```

## Project Resources

- Repository: [github.com/justin-mbca/oncoreconcile-ai](https://github.com/justin-mbca/oncoreconcile-ai)
- [MVP Documentation](docs/mvp.md)
- [Checkpoint 2 Submission](docs/checkpoint2_submission.md)
- [Architecture](docs/architecture.md)
- [Curation Methodology](docs/curation_methodology.md)

## Roadmap

- Expanded benchmark coverage and independent validation
- Evidence quality ranking
- Multi-source evidence agents
- Reviewer copilot
- FHIR Genomics interoperability
- OMOP Oncology interoperability
- Standards-compliant genomic representations
