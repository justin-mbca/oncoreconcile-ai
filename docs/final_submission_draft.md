# 2026 DFWIT AI & Startup Competition

# OncoReconcile AI

Human-Governed AI for Oncology Entity Reconciliation and Data Quality

Final Submission Draft

## Executive Summary

OncoReconcile AI is a human-governed oncology reconciliation workbench that transforms fragmented cancer type, gene, and variant inputs into trusted, explainable, and auditable canonical oncology concepts.

Modern oncology data originates from molecular diagnostic laboratories, electronic health records, clinical trials, research repositories, vendor biomarker reports, and precision medicine platforms. Unfortunately, diseases, genes, and variants are frequently represented with inconsistent terminology, creating major challenges for research, analytics, interoperability, and AI applications.

OncoReconcile AI addresses this upstream data quality problem by combining deterministic reconciliation, confidence scoring, benchmark validation, provenance tracking, and human review workflows. Rather than replacing domain experts, the platform helps experts work with cleaner, more trustworthy oncology data while preserving uncertainty and auditability.

Guiding principle:

Trusted downstream analytics and AI applications depend on trusted upstream oncology data.

## Why This Matters For AI

Large language models, RAG systems, analytics dashboards, and research pipelines are only as reliable as the data they consume.

If oncology concepts are inconsistently represented:

- retrieval quality decreases
- search accuracy decreases
- cohort identification becomes unreliable
- AI explanations become inconsistent
- hallucination and misclassification risk increases

OncoReconcile AI establishes a trusted oncology data layer before higher-level AI reasoning occurs.

## Problem Statement

Healthcare organizations increasingly integrate data from:

- molecular pathology reports
- NGS testing laboratories
- clinical trial systems
- EHR systems
- vendor biomarker reports
- research databases
- real-world evidence platforms

The same biological concept often appears in multiple formats.

| Original Input | Canonical Concept |
|---|---|
| `HER2` | `ERBB2` |
| `HER-2` | `ERBB2` |
| `p53` | `TP53` |
| `Ex19del` | `EGFR Exon 19 Deletion` |
| `del19` | `EGFR Exon 19 Deletion` |
| `NSCLC` | `Lung Non-Small Cell Carcinoma` |
| `LUAD` | `Lung Adenocarcinoma` |
| `TRK fusion` | `REVIEW_REQUIRED` |
| `unknown_gene` | `CANNOT_RECONCILE` |

These inconsistencies create challenges for:

- cohort identification
- biomarker analytics
- multi-vendor data integration
- clinical research
- real-world evidence generation
- precision oncology
- AI and RAG applications

Poor upstream data quality directly reduces downstream analytics and AI quality.

## Project Vision

Our vision is to build a trusted oncology data foundation.

```text
Messy oncology data
-> disease reconciliation
-> gene reconciliation
-> variant reconciliation
-> confidence assessment
-> human review when needed
-> validated oncology dataset
-> analytics / research / AI
```

The platform focuses on trustworthy normalization before clinical interpretation.

## Final MVP Scope

The final MVP reconciles three oncology entity types:

| Entity | Status |
|---|---|
| Disease / cancer type | Supported |
| Gene | Supported |
| Variant | Supported |

Input fields:

| Field | Requirement |
|---|---|
| `gene` | Required |
| `variant` | Required |
| `cancer_type` | Optional but recommended |
| `case_id` | Optional for tracking and batch workflows |

Example inputs:

- `NSCLC + HER2 + Amplification`
- `LUAD + TP53 + R175H`
- `NSCLC + EGFR + Ex19del`
- `NSCLC + TRK + pan-trk fusion`
- `NSCLC + unknown_gene + unknown_variant`

Each reconciliation result includes:

- original input
- canonical disease
- canonical gene
- canonical variant
- confidence score
- review status
- evidence context
- explanation
- notes
- audit trail

## Core Workflow

```text
User input or CSV upload
-> input cleanup and normalization
-> disease alias reconciliation
-> gene alias reconciliation
-> variant catalog reconciliation
-> ambiguity and conflict checks
-> confidence assessment
-> AUTO_RECONCILE / REVIEW_REQUIRED / CANNOT_RECONCILE
-> evidence and explanation generation
-> human review queue when needed
-> exportable reconciled results
```

## Reconciliation Outcomes

| Review Status | Meaning | Example |
|---|---|---|
| `AUTO_RECONCILE` | High-confidence deterministic normalization | `NSCLC + HER2 + Amplification` |
| `REVIEW_REQUIRED` | Ambiguous or generic terminology needs expert review | `TRK + fusion` |
| `CANNOT_RECONCILE` | Input cannot be safely normalized | `unknown_gene + unknown_variant` |

Example `AUTO_RECONCILE`:

```text
Input:
NSCLC / HER2 / Amplification

Output:
Lung Non-Small Cell Carcinoma / ERBB2 / ERBB2 Amplification
```

Example `REVIEW_REQUIRED`:

```text
Input:
NSCLC / TRK / fusion

Reason:
Generic TRK wording is insufficient to safely select NTRK1, NTRK2, or NTRK3.
```

Example `CANNOT_RECONCILE`:

```text
Input:
NSCLC / unknown_gene / unknown_variant

Reason:
The gene and variant cannot be safely normalized using the current curated data layer.
```

## Human-Governed AI Philosophy

OncoReconcile AI uses AI conservatively.

Deterministic rules handle known mappings. Human experts handle uncertainty. The system intentionally avoids autonomous clinical decision-making.

Core principles:

- do not force uncertain mappings
- preserve ambiguity
- maintain provenance
- support human review
- separate reconciliation from interpretation

## Fixed Curated Data Layer

For final delivery, the input data layer is fixed and version-controlled.

Active data files:

| File | Purpose |
|---|---|
| `data/disease_aliases.json` | Maps disease aliases to canonical disease names |
| `data/gene_aliases.json` | Maps gene aliases to canonical HGNC-style symbols or review sentinel values |
| `data/gene_variant_catalog.csv` | Curated gene-variant catalog with aliases, source, status, and notes |
| `data/disease_gene_catalog.csv` | Curated disease-to-gene support file |
| `data/benchmark_cases.csv` | Generated benchmark cases used for validation |

Supporting raw candidate files:

| File | Purpose |
|---|---|
| `data/raw/raw_gene_alias_candidates.json` | Downloaded gene alias candidates for review |
| `data/raw/civic_variant_candidates.csv` | Downloaded CIViC candidate variant evidence for review |

The fixed data layer replaces earlier Checkpoint 1 files such as `variant_aliases.json`, `review_required_terms.json`, `cannot_reconcile_terms.json`, and `nsclc_benchmark.csv`.

Example curated mappings:

| Type | Input | Output |
|---|---|---|
| Disease alias | `NSCLC` | `Lung Non-Small Cell Carcinoma` |
| Disease alias | `LUAD` | `Lung Adenocarcinoma` |
| Gene alias | `HER2` | `ERBB2` |
| Gene alias | `HER-2` | `ERBB2` |
| Gene alias | `p53` | `TP53` |
| Variant catalog | `Ex19del` | `EGFR Exon 19 Deletion` |
| Variant catalog | `copy gain` | `ERBB2 Copy Number Gain` |

## Reconciliation Engine

The final MVP uses a deterministic, safety-first reconciliation engine.

Implemented baseline:

- disease alias lookup
- gene alias lookup
- review-required sentinel handling
- cannot-reconcile sentinel handling
- variant catalog lookup using gene context
- confidence assignment
- review status assignment
- evidence, notes, explanation, and audit trail generation
- single-record API
- basic batch API
- benchmark-driven tests

Planned final workflow enhancements:

- input cleanup and normalized lookup keys
- variant suffix cleanup, such as `G12C mutation` to `G12C`
- generic variant handling for terms such as `positive`, `fusion`, `amp`, and `mutation`
- gene extraction from variant text, such as `KRAS G12C`
- gene/variant conflict detection
- disease-gene compatibility checks using `disease_gene_catalog.csv`
- conservative disease fuzzy matching only
- structured review-required reason codes

Safety guardrails:

- do not force uncertain mappings
- do not broadly fuzzy-match gene symbols
- do not broadly fuzzy-match variant strings
- do not generate treatment recommendations
- do not use LLM fallback for autonomous clinical interpretation

## Benchmark Validation Framework

A major differentiator of OncoReconcile AI is benchmark-driven validation.

Current benchmark:

- file: `data/benchmark_cases.csv`
- total cases: 156
- categories:
  - `AUTO_RECONCILE`
  - `REVIEW_REQUIRED`
  - `CANNOT_RECONCILE`

Coverage areas:

- disease normalization
- gene normalization
- variant normalization
- ambiguous terminology
- unsupported terminology

Validation goals:

- disease accuracy
- gene accuracy
- variant accuracy
- review status accuracy
- exact full-row accuracy
- failed-case reporting

Current backend tests validate the fixed benchmark behavior.

Final submission should include a benchmark evaluation report generated by:

```bash
python scripts/evaluate_benchmark.py
```

## Human Review Workflow

OncoReconcile AI is designed to support expert review, not replace it.

```text
AUTO_RECONCILE
-> accepted as high-confidence deterministic match

REVIEW_REQUIRED
-> review queue
-> approve / modify / mark cannot reconcile / add reviewer note

CANNOT_RECONCILE
-> manual investigation or exclusion from downstream analysis
```

The review workflow preserves:

- original input
- system recommendation
- confidence score
- evidence context
- explanation
- audit trail
- reviewer decision
- reviewer note

## Explainability And Auditability

Every reconciliation decision should be traceable.

Audit trail captures:

- original input
- disease lookup attempt
- gene lookup attempt
- variant catalog lookup attempt
- evidence found
- confidence calculation
- final review status
- explanation generation
- unresolved fields

Evidence context may include:

- local curated alias dictionary
- curated gene-variant catalog
- raw candidate source references such as CIViC
- review-required or cannot-reconcile rules

Entity reconciliation and clinical interpretation are intentionally separated. Evidence is used as supporting context only.

## Technical Architecture

```text
React frontend
  - manual single-record input
  - CSV upload
  - batch results table
  - status filters
  - review queue
  - export

FastAPI backend
  - POST /reconcile
  - POST /reconcile/batch
  - deterministic reconciliation engine
  - evidence and audit trail generation

Curated data layer
  - disease_aliases.json
  - gene_aliases.json
  - gene_variant_catalog.csv
  - disease_gene_catalog.csv
  - benchmark_cases.csv
```

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, CSS |
| Backend | FastAPI, Python |
| Data layer | JSON and CSV |
| Validation | Pytest, benchmark CSV |
| Future persistence | PostgreSQL or similar database |

Future AI-oriented components may include embeddings, semantic retrieval, RAG, and reviewer assistance, but these are intentionally deferred until deterministic reconciliation and human review workflows are stable.

## API Surface

Core endpoints:

| Endpoint | Purpose |
|---|---|
| `GET /` | API health and project metadata |
| `POST /reconcile` | Reconcile one oncology record |
| `POST /reconcile/batch` | Reconcile multiple oncology records |

Example request:

```json
{
  "case_id": "demo_001",
  "cancer_type": "NSCLC",
  "gene": "HER2",
  "variant": "Amplification"
}
```

Example response fields:

```json
{
  "case_id": "demo_001",
  "canonical": {
    "cancer_type": "Lung Non-Small Cell Carcinoma",
    "gene": "ERBB2",
    "variant": "ERBB2 Amplification"
  },
  "confidence": "HIGH",
  "review_status": "AUTO_RECONCILE",
  "evidence": [],
  "explanation": "...",
  "notes": [],
  "audit_trail": []
}
```

## Frontend Workflow

Final MVP frontend should support:

- manual single-record reconciliation
- example records for the three core outcomes
- CSV upload
- batch result summary
- filterable results table
- expanded evidence and audit rows
- review-required queue
- reviewer decisions and notes
- CSV/JSON export

Recommended table columns:

- case ID
- input disease
- input gene
- input variant
- canonical disease
- canonical gene
- canonical variant
- confidence
- review status
- decision reason

## Demo Flow

Final demo should show:

1. Start backend.
2. Start frontend.
3. Reconcile a single `AUTO_RECONCILE` example.
4. Reconcile a `REVIEW_REQUIRED` example.
5. Reconcile a `CANNOT_RECONCILE` example.
6. Upload a CSV batch.
7. Show summary counts.
8. Filter to `REVIEW_REQUIRED`.
9. Open one record and inspect evidence, notes, and audit trail.
10. Add a reviewer decision or note.
11. Export reconciled results.
12. Run benchmark evaluation.

## Business Impact

Potential users include:

- cancer centers
- molecular diagnostics laboratories
- healthcare systems
- research organizations
- pharmaceutical companies
- real-world evidence platforms
- healthcare AI startups

Potential benefits:

- reduced manual reconciliation effort
- improved oncology data quality
- faster cohort creation
- better interoperability
- improved AI and retrieval performance
- increased auditability and governance

## Competitive Advantages

OncoReconcile AI is differentiated by:

1. human-governed workflow design
2. explicit uncertainty handling
3. benchmark-driven validation
4. explainability and auditability
5. oncology-focused data model
6. deterministic safety-first reconciliation
7. standards-ready roadmap
8. trust-first product philosophy

## Current Status Toward Final MVP

| Area | Status |
|---|---|
| MVP definition | Implemented |
| Fixed data layer | Implemented |
| Single-record reconciliation | Implemented |
| Basic batch endpoint | Implemented |
| Benchmark-driven backend tests | Implemented |
| Manual frontend input | Implemented |
| Evidence display | Partially implemented |
| Expanded deterministic reconciliation steps | Planned for final MVP |
| CSV upload | Planned for final MVP |
| Review queue | Planned for final MVP |
| Export | Planned for final MVP |
| Benchmark evaluation script | Planned for final MVP |
| Persistent database | Deferred |
| LLM fallback | Deferred |
| Production deployment | Deferred unless time allows |

## Scope Guardrails

In final MVP:

- deterministic reconciliation
- fixed curated data layer
- benchmark validation
- batch processing
- human review workflow
- exportable audit-friendly outputs

Deferred beyond final MVP:

- treatment recommendations
- autonomous clinical interpretation
- LLM-based reconciliation
- production-grade deployment
- advanced analytics dashboard
- knowledge graph integration
- standards-native export to GA4GH VRS, CAT-VRS, OMOP, or FHIR

## Standards Alignment Roadmap

Future interoperability support may include:

- HGVS
- GA4GH VRS
- CAT-VRS
- VA-Spec
- HL7 FHIR
- mCODE
- OMOP

The platform complements these standards rather than replacing them. It provides an explainable reconciliation workflow that can later map into standards-based representations.

## Expert Validation Summary

Checkpoint 1 feedback from healthcare interoperability, cancer genomics, molecular diagnostics, clinical informatics, and AI evaluation experts shaped the product direction.

Key learnings:

- preserve uncertainty
- do not force mappings
- separate reconciliation from clinical interpretation
- capture provenance early
- build evaluation frameworks from the beginning
- move toward expert-reviewed gold-standard datasets

## Future Gold Standard Roadmap

```text
Current curated benchmark
-> multiple reviewers
-> disagreement tracking
-> adjudication workflow
-> gold-standard dataset
-> formal evaluation framework
```

Goal:

Create an expert-reviewed oncology gold standard for future evaluation.

## Repository And Demo

Repository:

```text
https://github.com/oncoreconcile-ai/oncoreconcile-ai
```

Primary branch for current curated-data workflow:

```text
vanguard_justin_curated_data
```

Demo video:

```text
[INSERT FINAL DEMO VIDEO LINK]
```

## Quick Start

Backend:

```bash
cd backend
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Backend docs:

```text
http://127.0.0.1:8000/docs
```

Frontend:

```text
http://localhost:5173
```

Tests:

```bash
cd backend
PYTHONPATH=. pytest -q
```

## Final Success Criteria

By final delivery, OncoReconcile AI should demonstrate:

- fixed input data documented and frozen
- deterministic reconciliation across disease, gene, and variant inputs
- 156-case benchmark validation
- single-record and batch reconciliation
- review-required routing for ambiguous terminology
- cannot-reconcile routing for unsupported terminology
- evidence, explanation, notes, and audit trail visibility
- CSV upload workflow
- human review workflow
- CSV/JSON export
- repeatable demo instructions

## Closing Statement

OncoReconcile AI is not a treatment recommendation system.

It is not an autonomous clinical AI.

It is a trusted oncology data quality platform.

By combining explainability, auditability, benchmark validation, provenance tracking, and human review, OncoReconcile AI creates a trustworthy foundation for future oncology analytics, research, interoperability, and AI applications.

Our goal is simple:

Help experts work with cleaner, safer, and more trustworthy oncology data before downstream analytics and AI reasoning begins.
