# API Contract

This document defines how frontend, backend, and AI modules communicate.

Do not change this contract without team discussion.

---

## Endpoint

```text
POST /reconcile
```

---

## Single Record Request

```json
{
  "case_id": "case_001",
  "cancer_type": "NSCLC",
  "gene": "HER2",
  "variant": "Amplification"
}
```

---

## Single Record Response

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
    },
    {
      "source": "Seed Knowledge Base",
      "type": "variant_context",
      "description": "Amplification was interpreted in the context of ERBB2."
    }
  ],
  "explanation": "HER2 was reconciled to ERBB2 because HER2 is a recognized alias. Amplification was mapped to ERBB2 Amplification using the gene context.",
  "confidence": "HIGH",
  "review_status": "AUTO_RECONCILE",
  "notes": []
}
```

---

## Batch Request

```json
{
  "records": [
    {
      "case_id": "case_001",
      "cancer_type": "NSCLC",
      "gene": "HER2",
      "variant": "Amplification"
    },
    {
      "case_id": "case_002",
      "cancer_type": "LUAD",
      "gene": "p53",
      "variant": "R175H"
    }
  ]
}
```

---

## Batch Response

```json
{
  "results": [
    {
      "case_id": "case_001",
      "canonical": {
        "cancer_type": "Non-Small Cell Lung Cancer",
        "gene": "ERBB2",
        "variant": "ERBB2 Amplification"
      },
      "confidence": "HIGH",
      "review_status": "AUTO_RECONCILE"
    }
  ],
  "summary": {
    "total_records": 2,
    "auto_reconcile": 1,
    "review_required": 1,
    "cannot_reconcile": 0
  }
}
```

---

## Allowed Confidence Values

```text
HIGH
MEDIUM
LOW
```

---

## Allowed Review Status Values

```text
AUTO_RECONCILE
REVIEW_REQUIRED
CANNOT_RECONCILE
```

---

## Error Response

```json
{
  "error": "Invalid input",
  "details": "gene and variant are required"
}
```
