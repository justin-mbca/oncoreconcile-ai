# MVP Definition

## Project Name

OncoReconcile AI

## MVP Name

Human-Governed AI-Assisted Curation and Harmonization Platform for Oncology

---

## MVP Goal

Transform messy oncology entities into trusted canonical oncology concepts.

The MVP focuses on:

- Cancer type
- Gene
- Variant

The system does not make treatment recommendations or clinical decisions.

---

## User Problem

Oncology data teams receive data from many systems and vendors. The same disease, gene, or variant may appear in different forms.

Examples:

- NSCLC vs Non-Small Cell Lung Cancer
- LUAD vs Lung Adenocarcinoma
- HER2 vs HER-2 vs ERBB2
- p53 vs TP53
- EGFR Ex19del vs EGFR Exon 19 Deletion

This creates friction in:

- Data harmonization
- Evidence aggregation
- Cohort creation
- Research analytics
- Multi-vendor integration

---

## Target Users

Initial MVP users:

- Oncology data engineers
- Clinical genomics data analysts
- Molecular pathology informatics teams
- Translational research teams

Future users may include:

- Molecular pathologists
- Clinical laboratory teams
- Precision oncology platform teams

---

## Inputs

Required:

- `gene`
- `variant`

Optional:

- `cancer_type`
- `case_id`
- `patient_id`

Example:

```json
{
  "case_id": "case_001",
  "cancer_type": "NSCLC",
  "gene": "HER2",
  "variant": "Amplification"
}
```

---

## Outputs

Each input record returns:

- Original input
- Canonical cancer type
- Canonical gene
- Canonical variant
- Evidence context
- Deterministic explanation with an optional review-only AI suggestion
- Confidence
- Review status
- AI-assisted curation metadata
- Provenance-ready metadata
- Standards-ready export availability

Example:

```json
{
  "case_id": "case_001",
  "input": {
    "cancer_type": "NSCLC",
    "gene": "HER2",
    "variant": "Amplification"
  },
  "canonical": {
    "cancer_type": "Non-Small Cell Lung Cancer",
    "gene": "ERBB2",
    "variant": "ERBB2 Amplification"
  },
  "evidence": [
    {
      "source": "HGNC",
      "type": "gene_alias",
      "description": "HER2 is a recognized alias of ERBB2."
    }
  ],
  "explanation": "HER2 was reconciled to ERBB2 because HER2 is a recognized alias. Amplification was interpreted in the context of ERBB2.",
  "confidence": "HIGH",
  "review_status": "AUTO_RECONCILE"
}
```

---

## Confidence Rules for MVP

| Condition | Method | Confidence |
|---|---|---|
| Exact dictionary or alias match (gene, variant, cancer type) | Alias dictionary lookup | HIGH |
| Fuzzy string match after exact lookup fails | RapidFuzz with entity-specific safeguards | MEDIUM |
| Candidate evidence from local or live sources | Advisory evidence lookup | MEDIUM |
| LLM suggestion for review-required cases | Optional review-only provider hook | LOW |
| No match from any method | — | LOW |

> **Safety note:** Exact alias and catalog matching run before fuzzy matching.
> Precise protein hotspot notation such as `R132C` is not fuzzy-substituted to
> another amino-acid change such as `R132H`; unresolved precise variants are
> routed to candidate evidence discovery and human review.

---

## Review Recommendation Rules for MVP

| Confidence | Source method | Review Status |
|---|---|---|
| HIGH | Exact alias dictionary match | AUTO_RECONCILE |
| MEDIUM | Fuzzy match, ambiguity, or candidate evidence | REVIEW_REQUIRED |
| LOW | LLM suggestion or weak/partial evidence | REVIEW_REQUIRED |
| LOW | No match from any method | CANNOT_RECONCILE |

> **Human governance rule:** MEDIUM and LOW results are never auto-accepted. A clinician or data analyst must confirm before the canonical output is trusted.

---

## GA4GH AI Work Stream Alignment

OncoReconcile AI aligns most closely with the GA4GH AI Work Stream directions
of AI-Assisted Curation and AI Governance & Trust.

The MVP demonstrates:

- Variant harmonization
- Disease, gene, and variant curation
- Evidence aggregation
- PROV-O-inspired provenance tracking
- Human-governed review
- Benchmark-driven validation

Implemented prototype exports include:

- PROV-O-inspired provenance records
- VRS-ready representation stubs
- Cat-VRS-ready ambiguity stubs
- VA-Spec-ready evidence and provenance stubs

The project is standards-inspired and does not claim official GA4GH, VRS,
Cat-VRS, VA-Spec, or PROV-O compliance.

### Near-Term Standards Roadmap

- Expanded provenance-chain visualization
- Knowledge graph export prototype
- Versioned curator-controlled catalog promotion

### Future Standards Roadmap

- Official GA4GH VRS object generation
- Cat-VRS serialization
- VA-Spec-compatible export
- Biolink and SSSOM mappings
- FHIR Genomics export
- OMOP Oncology export

---

## MVP Success Criteria

By the end of the MVP phase, the team should demonstrate:

1. Upload or submit oncology records.
2. Reconcile cancer type, gene, and variant.
3. Show canonical concepts.
4. Show evidence and explanation.
5. Show confidence and review status.
6. Download or display final results.
7. Demonstrate the 161-case benchmark and external-evidence review scenarios.
