# OncoReconcile AI

## Human-Governed AI Platform for Oncology Data Quality, Harmonization, and Curation

## 1. Executive Summary

OncoReconcile AI is a human-governed platform for reconciling inconsistent oncology terminology. The MVP converts cancer-type, gene, and variant inputs into canonical candidates with evidence, confidence, explanations, provenance, and explicit review recommendations.

The system favors safe uncertainty over forced normalization. Ambiguous or externally supported candidates are routed to expert review rather than treated as autonomous clinical conclusions.

## 2. Problem Statement

Oncology data arrives from laboratories, EHR systems, clinical trials, research datasets, and genomic vendors. The same concept may be represented by aliases, abbreviations, punctuation differences, misspellings, or underspecified variant descriptions.

Examples include:

| Original | Canonical |
|---|---|
| HER2 | ERBB2 |
| HER1 | EGFR |
| p53 | TP53 |
| NSCLC | Lung Non-Small Cell Carcinoma |
| LUAD | Lung Adenocarcinoma |
| Ex19del | EGFR Exon 19 Deletion |

Without harmonization, these differences reduce data quality and fragment analytics.

## 3. Why This Matters

Trusted normalization supports:

- More reliable cohort construction
- Cross-vendor data integration
- Consistent evidence aggregation
- Reproducible research analytics
- Auditable curation workflows
- Better inputs for downstream AI systems

OncoReconcile AI addresses data quality. It does not perform clinical interpretation or recommend treatments.

## 4. Proposed Solution

The platform provides:

- Disease, gene, and variant reconciliation
- Exact, alias, and fuzzy matching
- Ambiguity preservation
- Local and external evidence discovery
- Confidence scoring and explanations
- Human review and adjudication
- Provenance and prototype export formats
- Benchmark-driven validation

## 5. MVP Workflow

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
Adaptive external evidence retrieval when needed
  ↓
Confidence assessment and explanation
  ↓
AUTO_RECONCILE | REVIEW_REQUIRED | CANNOT_RECONCILE
  ↓
Persistent human review queue
  ↓
Reviewer agreement and adjudication
  ↓
Governed output and prototype exports
```

## 6. Current MVP Features

Implemented:

- Disease, gene, and variant reconciliation
- Exact dictionary and alias matching
- Fuzzy matching with entity-specific safeguards
- Categorical ambiguity preservation for review-required concepts
- Confidence scores and score breakdowns
- Deterministic explanations
- Alternative candidate presentation
- Response audit trails
- Batch and CSV processing
- Benchmark metrics endpoint and frontend dashboard
- AI-assisted curation metadata
- Optional LLM suggestion hook restricted to `REVIEW_REQUIRED` cases

## 7. Evidence Retrieval

Implemented advisory connectors:

- MyVariant.info
- ClinVar
- CIViC
- ClinGen Allele Registry

The four connectors are aggregated through `lookup_all_external_sources()`. Source-specific results include retrieval mode, timestamp, identifiers, and URLs when available. API errors are converted into evidence records so external failures do not erase the local reconciliation result.

External evidence is advisory. It can route a case to `REVIEW_REQUIRED`, but it does not independently create `AUTO_RECONCILE`.

## 8. Human Governance

Implemented:

- File-backed persistent review queue
- Stable generated review keys
- Duplicate prevention
- Approve, reject, edit, and reopen decisions
- Curator notes and timestamps
- Review history preservation
- Explicit catalog-promotion endpoint

Catalog promotion is intentionally disabled in the MVP. The endpoint returns a clear `not_implemented` response rather than modifying the curated catalog automatically.

## 9. Reviewer Agreement & Adjudication

Implemented:

- Chronological multi-reviewer history
- Comparable-case agreement counts
- Percent agreement
- Cohen's kappa
- Disagreement detection
- `REQUIRED` and `RESOLVED` adjudication states
- Senior-curator adjudication with canonical override support

These are internal prototype governance metrics, not independently validated inter-reviewer reliability findings.

## 10. Knowledge Graph Export

The MVP produces a JSON-LD knowledge graph prototype containing:

- Raw-record nodes
- Canonical disease, gene, and variant nodes
- Evidence records
- Alternatives
- Reconciliation activity and provenance relationships

Additional outputs include a PROV-O-inspired provenance export and VRS-ready, Cat-VRS-ready, and VA-Spec-ready stubs. These outputs demonstrate future integration paths; they are not official standards-compliant representations.

## 11. Validation

Verified on June 20, 2026:

| Validation item | Result |
|---|---|
| Backend tests | 43 passed |
| Benchmark cases | 191 |
| Frontend production build | Passed |
| External connector success/error behavior | Tested |
| Persistent review workflow | Tested |
| Stable keys and duplicate prevention | Tested |
| Agreement and adjudication workflow | Tested |
| Provenance and knowledge graph exports | Tested |

The benchmark includes automatic, review-required, and cannot-reconcile scenarios. It is an internal curated benchmark and is not a substitute for independent clinical validation.

## 12. Business Opportunity

Potential users include cancer centers, molecular laboratories, clinical research organizations, biopharmaceutical companies, precision-oncology programs, and genomic knowledgebase teams.

Potential value:

- Reduced repetitive manual normalization
- Faster cohort preparation
- Improved traceability
- More consistent multi-source datasets
- Safer human-in-the-loop AI preparation
- Better governance and auditability

## 13. Roadmap

Future work:

- Expanded benchmark coverage and independent validation
- Evidence quality ranking
- Multi-source evidence agents
- Reviewer copilot
- FHIR Genomics interoperability
- OMOP Oncology interoperability
- Standards-compliant genomic representations
- Governed, versioned catalog promotion

## 14. Current Project Status

The Checkpoint 2 MVP is implemented and verified as a competition prototype. Core reconciliation, advisory evidence retrieval, review governance, reviewer agreement, adjudication, curation metadata, provenance, and knowledge graph export are operational.

Remaining competition work centers on demo hardening, screenshots, presentation materials, video production, and broader validation—not autonomous clinical decision support.
