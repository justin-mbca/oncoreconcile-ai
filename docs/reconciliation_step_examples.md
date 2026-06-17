# Reconciliation Step Examples

Upload `data/reconciliation_step_examples.csv` from the frontend CSV Batch Upload page to exercise the main reconciliation branches.

The upload endpoint only requires `case_id,cancer_type,gene,variant`; the extra columns document what each row is meant to demonstrate.

| Case ID | Input | Demonstrates | Expected Status |
| --- | --- | --- | --- |
| `step_001` | `NSCLC`, `HER2`, `amp` | Exact disease alias, gene alias, catalog variant, external evidence | `AUTO_RECONCILE` |
| `step_002` | `Breast Cancer`, `HER2`, `HER2+` | Disease alias normalization to `Breast Invasive Carcinoma` | `AUTO_RECONCILE` |
| `step_003` | `NSCLC`, `CD340`, `HER2 amp` | Gene alias normalization from `CD340` to `ERBB2` | `AUTO_RECONCILE` |
| `step_004` | `NSCLC`, `EGFR`, `Ex19del` | Variant catalog normalization plus ClinVar, CIViC, and OncoKB evidence | `AUTO_RECONCILE` |
| `step_005` | `NSCLC`, `TRK`, `pan-trk fusion` | Ambiguous gene review path plus LLM suggestion hook | `REVIEW_REQUIRED` |
| `step_006` | `NSCLC`, `EGFR`, `Exon20ins` | Catalog row explicitly marked review required | `REVIEW_REQUIRED` |
| `step_007` | `NSCLC`, `unknown_gene`, `G12C` | Unknown gene cannot be trusted, so variant is not mapped | `CANNOT_RECONCILE` |
| `step_008` | `Melanoma`, `BRAF`, `V600E` | Disease-specific catalog variant plus external evidence | `AUTO_RECONCILE` |
| `step_009` | `NSCLC`, `KRAS`, `mutation` | Generic mutation is recognized but needs a more specific alteration | `REVIEW_REQUIRED` |
| `step_010` | `NSCLC`, `FAKE_GENE_XYZ`, `FAKE_VARIANT_XYZ` | No trusted gene or variant match | `CANNOT_RECONCILE` |

## Optional Fuzzy Examples

Fuzzy matching is implemented in `backend/app/reconcile.py`, but it only runs when `rapidfuzz` is installed and importable. The dependency is listed in `backend/requirements.txt`.

Examples to try after installing backend requirements:

```csv
case_id,cancer_type,gene,variant
fuzzy_001,non-small cell lung carcinom,EGFR,Ex19del
fuzzy_002,NSCLC,ERBB-2,amp
fuzzy_003,NSCLC,EGFR,Exon 19 deletin
```

If `rapidfuzz` is not available, those rows may route to partial review or cannot-reconcile instead of fuzzy matching.
