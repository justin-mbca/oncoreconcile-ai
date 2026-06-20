# OncoReconcile AI

## DFWIT AI & Startup Competition 2026 – Checkpoint 2 Submission

### Team Variant Vanguard

**Team Members**

- Justin (Lead)
- [NAME]
- [NAME]

**Project Repository**

[https://github.com/justin-mbca/oncoreconcile-ai](https://github.com/justin-mbca/oncoreconcile-ai)

**Demo URL**

[INSERT DEMO URL]

---

## Executive Summary

OncoReconcile AI is a human-governed platform for oncology data harmonization and curation.

The platform reconciles disease, gene, and variant entities from heterogeneous oncology datasets and supports evidence-based, explainable, and reviewable harmonization workflows. Rather than forcing uncertain mappings, it preserves ambiguity, surfaces advisory evidence, records provenance, measures reviewer agreement, and routes unresolved cases through expert review.

The current MVP combines:

- Disease, gene, and variant harmonization
- Alias and fuzzy matching
- Ambiguity preservation
- Multi-source evidence retrieval
- Explainability and confidence scoring
- Persistent human review
- Reviewer agreement metrics
- Adjudication workflows
- Provenance tracking
- JSON-LD knowledge graph export
- Benchmark validation

## Problem Statement

Modern oncology data originates from molecular laboratories, EHR systems, clinical trials, research datasets, commercial genomic vendors, and precision-oncology programs. The same biological concept frequently appears under different names.

| Original | Canonical |
|---|---|
| HER2 | ERBB2 |
| HER1 | EGFR |
| p53 | TP53 |
| NSCLC | Lung Non-Small Cell Carcinoma |
| LUAD | Lung Adenocarcinoma |
| Ex19del | EGFR Exon 19 Deletion |

These inconsistencies reduce data quality and create challenges for analytics, cohort construction, integration, and trustworthy AI.

## Proposed Solution

OncoReconcile AI provides:

- Disease reconciliation
- Gene reconciliation
- Variant reconciliation
- Evidence discovery
- Confidence scoring
- Explainable decisions
- Human-governed review workflows

The platform preserves ambiguity and routes uncertain cases for expert review rather than forcing potentially incorrect mappings.

## Current MVP Workflow

```text
Input: cancer type, gene, variant
  ↓
Disease reconciliation
  ↓
Gene reconciliation
  ↓
Variant reconciliation
  ↓
Local evidence and ambiguity checks
  ↓
Adaptive external evidence retrieval
  ↓
Confidence assessment
  ↓
AUTO_RECONCILE | REVIEW_REQUIRED | CANNOT_RECONCILE
  ↓
Human review queue
  ↓
Reviewer agreement metrics
  ↓
Adjudication workflow
  ↓
Governed output and prototype exports
```

## Current Progress

### Core Harmonization

Implemented:

- Disease reconciliation
- Gene reconciliation
- Variant reconciliation
- Alias matching
- Fuzzy matching
- Ambiguity preservation

### External Evidence Retrieval

Implemented:

- MyVariant.info
- ClinVar
- CIViC
- ClinGen Allele Registry
- Aggregated external-evidence routing
- Graceful source-specific failure records

External evidence supports review workflows and candidate discovery. It does not automatically convert a candidate into a high-confidence reconciliation.

### Human Governance

Implemented:

- Persistent human review queue
- Stable review keys
- Duplicate prevention
- Approve, reject, edit, and reopen workflows
- Curator notes and timestamps
- Explicit disabled catalog-promotion stub

The MVP does not automatically modify its curated catalog.

### Reviewer Agreement & Adjudication

Implemented:

- Multi-reviewer history
- Agreement percentage calculation
- Cohen's kappa calculation
- Disagreement detection
- Senior-curator adjudication workflow

### Curation and Exports

Implemented:

- Curation metadata in reconciliation output
- Human-governance and catalog-candidate flags
- Combined curation report endpoint
- PROV-O-inspired provenance export
- JSON-LD knowledge graph prototype
- Canonical disease, gene, variant, and evidence nodes
- VRS-ready, Cat-VRS-ready, and VA-Spec-ready export stubs

These are standards-inspired prototypes and stubs, not official standards compliance.

## Validation

Verified on June 20, 2026:

- **43 backend tests passed**
- **191 benchmark cases**
- **Frontend production build successful**
- External retrieval success and error paths verified
- Persistent review workflow verified
- Stable keys and duplicate prevention verified
- Reviewer agreement workflow verified
- Adjudication workflow verified
- Provenance and knowledge graph exports verified

The benchmark is internally curated and does not represent independent clinical validation.

## Screenshots

Screenshots will be placed in `docs/images/` without breaking this document while assets are pending.

### Single Record Reconciliation

[INSERT SCREENSHOT: `docs/images/single_reconciliation.png`]

### Review Queue

[INSERT SCREENSHOT: `docs/images/review_queue.png`]

### Reviewer Agreement Metrics

[INSERT SCREENSHOT: `docs/images/reviewer_agreement.png`]

### Knowledge Graph Export

[INSERT SCREENSHOT: `docs/images/knowledge_graph_export.png`]

## Challenges Encountered

- Harmonizing heterogeneous oncology terminology
- Balancing automation with human review
- Handling ambiguous concepts safely
- Designing explainable workflows
- Supporting governance and provenance
- Integrating multiple advisory evidence sources

## Lessons Learned

- Data quality is foundational to trustworthy AI.
- Ambiguity preservation is safer than forced normalization.
- Human governance remains essential.
- Evidence improves reviewer context but does not replace judgment.
- Provenance matters for auditability.

## Business Opportunity

Potential users include:

- Cancer centers
- Molecular laboratories
- Clinical research organizations
- Biopharmaceutical companies
- Precision-oncology programs
- Genomic knowledgebases

Potential value includes:

- Reduced manual curation effort
- Faster cohort creation
- Improved data consistency
- Better interoperability
- More reliable AI-ready datasets
- Improved governance and auditability

## Current Project Status

The Checkpoint 2 MVP is implemented and verified as a human-governed competition prototype.

Completed:

- Core reconciliation engine
- Advisory external evidence retrieval
- Human review workflow
- Reviewer agreement metrics
- Adjudication workflow
- Curation metadata
- Provenance tracking
- Knowledge graph export prototype
- Benchmark framework

Remaining:

- Demo hardening
- Screenshots
- Expanded benchmark coverage
- Competition presentation
- Competition video

## Project Resources

- Repository: [github.com/justin-mbca/oncoreconcile-ai](https://github.com/justin-mbca/oncoreconcile-ai)
- [MVP Documentation](mvp.md)
- [Architecture](architecture.md)
- Demo: [INSERT DEMO LINK]
- Video: [INSERT VIDEO LINK IF AVAILABLE]
- Presentation: [INSERT SLIDES LINK IF AVAILABLE]

## Safety and Claims Boundary

OncoReconcile AI does not provide clinical interpretation, treatment recommendations, or autonomous clinical decision support. FHIR, OMOP, and fully standards-compliant genomic representations remain future interoperability work.
