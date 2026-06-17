# MVP Definition

## Project Name

OncoReconcile AI

## MVP Name

Human-Governed Oncology Reconciliation Workbench

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
- AI explanation
- Confidence
- Review status

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
| Fuzzy string match on cancer type free-text only (score ≥ 85) | RapidFuzz — cancer type only | MEDIUM |
| Semantic similarity match via biomedical embedding model | ML/embedding (e.g. BioBERT, PubMedBERT) | MEDIUM |
| LLM-inferred suggestion for hard/unmatched cases | LLM fallback (deferred — Hao, Jun 30+) | LOW |
| No match from any method | — | LOW |

> **Note:** Fuzzy matching is restricted to cancer type free-text only. Gene symbols (e.g. EGFR, KRAS) and variant notation (e.g. p.E746_A750del) must use exact alias dictionary lookup — fuzzy matching on these is unreliable and clinically unsafe.

---

## Review Recommendation Rules for MVP

| Confidence | Source method | Review Status |
|---|---|---|
| HIGH | Exact alias dictionary match | AUTO_RECONCILE |
| MEDIUM | Fuzzy cancer type match or ML/embedding similarity | REVIEW_REQUIRED |
| LOW | LLM suggestion or weak/partial evidence | REVIEW_REQUIRED |
| LOW | No match from any method | CANNOT_RECONCILE |

> **Human governance rule:** MEDIUM and LOW results are never auto-accepted. A clinician or data analyst must confirm before the canonical output is trusted.

---

## Standards Alignment

The MVP uses a simplified Canonical Oncology Concept Object.

Future versions may align with:

- HGNC
- HGVS
- ClinVar
- CIViC
- GA4GH VRS
- CAT-VRS
- FHIR Genomics
- OMOP Oncology extensions

CAT-VRS is important for future standards alignment, but it is not required for the first working MVP implementation.

---

## MVP Success Criteria

By the end of the MVP phase, the team should demonstrate:

1. Upload or submit oncology records.
2. Reconcile cancer type, gene, and variant.
3. Show canonical concepts.
4. Show evidence and explanation.
5. Show confidence and review status.
6. Download or display final results.
7. Demonstrate at least 20 NSCLC benchmark cases.
