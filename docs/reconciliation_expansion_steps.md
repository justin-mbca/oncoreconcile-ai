# Reconciliation Expansion Steps

## Purpose

Now that the input data files are fixed, additional coverage should come from deterministic reconciliation steps rather than uncontrolled data changes.

Goal:

Improve coverage for realistic oncology inputs while preserving safe behavior:

- high-confidence matches can `AUTO_RECONCILE`
- ambiguous records go to `REVIEW_REQUIRED`
- unsupported records go to `CANNOT_RECONCILE`

## Current Engine Baseline

Current implemented steps:

1. Disease alias lookup.
2. Gene alias lookup.
3. Gene review-required lookup.
4. Variant catalog lookup using canonical gene context.
5. Cannot-reconcile handling for explicit unsupported terms.
6. Confidence and review status assignment.
7. Evidence, explanation, notes, and audit trail generation.

## Recommended Additional Reconciliation Steps

### Step 1: Input Cleanup And Normalization

Add a preprocessing layer before alias lookup.

Examples:

- trim whitespace
- normalize repeated spaces
- normalize case for lookup only
- normalize hyphen and underscore variants
- normalize punctuation around variant strings

Example inputs to support:

- ` her2 `
- `HER 2`
- `HER_2`
- `exon-19 deletion`
- `EGFR: L858R`
- `KRAS G12C mutation`

Expected behavior:

- If cleanup produces an exact catalog or alias match, continue to normal reconciliation.
- Preserve original input in the API response and audit trail.

Acceptance criteria:

- Original input is never overwritten.
- Normalized lookup key is visible in audit trail or decision metadata.
- Existing benchmark tests still pass.

### Step 2: Gene Symbol Extraction From Variant Text

Many user inputs put the gene inside the variant field.

Examples:

- gene: `EGFR`, variant: `EGFR Ex19del`
- gene: `KRAS`, variant: `KRAS G12C mutation`
- gene: empty or unknown, variant: `BRAF V600E`

Recommended behavior:

- If variant text includes a known gene and the gene field agrees, use it as supporting evidence.
- If variant text includes a known gene and the gene field is missing, infer gene with `REVIEW_REQUIRED` unless confidence rules allow auto-reconcile.
- If variant text gene conflicts with input gene, route to `REVIEW_REQUIRED`.

Acceptance criteria:

- `EGFR + EGFR Ex19del` reconciles normally.
- `KRAS + EGFR Ex19del` does not auto-reconcile.
- Conflict is visible in notes and evidence.

### Step 3: Variant Suffix Cleanup

Real inputs often include generic suffixes.

Examples:

- `G12C mutation`
- `V600E mutant`
- `L858R variant`
- `R175H alteration`

Recommended behavior:

- Remove safe generic suffixes only after gene context is known.
- Try catalog lookup with the cleaned variant.
- If the cleaned term maps to a specific catalog row, preserve the cleanup step in audit trail.

Acceptance criteria:

- `KRAS + G12C mutation` maps to `KRAS G12C`.
- `BRAF + V600E mutant` maps to `BRAF V600E`.
- Generic `mutation` alone still routes to `REVIEW_REQUIRED`.

### Step 4: Disease-Gene Compatibility Check

Use `data/disease_gene_catalog.csv` to check whether a gene is expected in a disease scope.

Recommended behavior:

- If disease and gene are both recognized and compatible, add supporting evidence.
- If disease and gene are both recognized but not listed as compatible, do not automatically fail.
- Instead, lower confidence or route to `REVIEW_REQUIRED` depending on final matching strength.

Acceptance criteria:

- Compatible disease-gene pairs show evidence.
- Unexpected disease-gene pairs are flagged for review.
- Catalog absence does not create false `CANNOT_RECONCILE` by itself.

### Step 5: Generic Variant Ambiguity Rules

Handle generic terms safely.

Examples:

- `positive`
- `detected`
- `abnormal`
- `mutation`
- `alteration`
- `fusion`
- `amp`

Recommended behavior:

- If the term is generic but gene context makes it specific in the catalog, allow catalog match.
- If the term remains generic after gene context, route to `REVIEW_REQUIRED`.
- Never map generic terms across genes without gene context.

Acceptance criteria:

- `ALK + fusion` can map to `ALK Fusion`.
- `TRK + fusion` routes to `REVIEW_REQUIRED`.
- `unknown_gene + G12C` routes to `CANNOT_RECONCILE`, not `KRAS G12C`.

### Step 6: Conflict Detection

Add explicit conflict detection before final status assignment.

Conflict examples:

- input gene maps to `KRAS`, but variant text says `EGFR Ex19del`
- input disease says `Breast Cancer`, but catalog row is scoped to NSCLC
- alias maps to one gene but variant catalog maps to another gene

Recommended behavior:

- Route conflicts to `REVIEW_REQUIRED`.
- Add conflict details to notes and audit trail.

Acceptance criteria:

- Conflicting gene/variant records never `AUTO_RECONCILE`.
- Conflict explanation names both sides of the conflict.

### Step 7: Fuzzy Matching For Disease Only

Disease strings often vary more than gene symbols.

Recommended behavior:

- Add conservative fuzzy matching for disease terms only.
- Use a high similarity threshold.
- Keep fuzzy disease matches at `MEDIUM` confidence unless gene and variant are exact.

Examples:

- `non small cell lung carcinoma`
- `non-small-cell lung cancer`
- `lung adenoca`

Acceptance criteria:

- Common disease spelling variants resolve.
- Fuzzy disease match is visible in evidence.
- Fuzzy disease match alone does not cause `AUTO_RECONCILE`.

### Step 8: Review-Required Reason Codes

Make review reasons structured.

Suggested reason codes:

- `AMBIGUOUS_GENE`
- `GENERIC_VARIANT`
- `GENE_VARIANT_CONFLICT`
- `DISEASE_GENE_UNEXPECTED`
- `LOW_CONFIDENCE_MATCH`
- `UNSUPPORTED_TERM`

Acceptance criteria:

- Every `REVIEW_REQUIRED` result has at least one reason code.
- Frontend can filter review queue by reason code.

## Suggested Build Order

1. Input cleanup and normalized lookup keys.
2. Variant suffix cleanup.
3. Generic variant ambiguity rules.
4. Gene symbol extraction from variant text.
5. Conflict detection.
6. Disease-gene compatibility check.
7. Conservative disease fuzzy matching.
8. Structured review reason codes.

## Do Not Add Yet

Avoid these until deterministic workflow is stable:

- LLM fallback
- automatic treatment interpretation
- broad fuzzy matching for gene symbols
- broad fuzzy matching for variants
- external API calls during reconciliation

These can increase coverage but also increase the risk of unsafe mappings.

## Checkpoint 2 Definition Of Done For Reconciliation Coverage

- [ ] Existing 156-case benchmark remains green.
- [ ] Added tests for realistic messy inputs.
- [ ] No generic or conflicting input auto-reconciles incorrectly.
- [ ] Every review-required case has a clear reason.
- [ ] Frontend can display why a record needs review.
