# Generated Benchmark Provenance Report

Generated at: 2026-06-03 01:02:23 UTC

## Method

This dataset was generated from scratch using:
- HGNC REST API (gene alias retrieval)
- Manual disease seed list
- Manual variant seed list
- Synthetic ambiguity/negative-test construction

No existing benchmark rows were read by this generator.

## Summary Statistics

- Total Cases: 32
- Easy Cases: 12
- Medium Cases: 12
- Difficult Cases: 8
- Gene Alias Count: 54
- Disease Alias Count: 4
- Variant Alias Count: 26

## Row-level Provenance

| case_id | difficulty | source | curation_note |
|---|---|---|---|
| case_001 | EASY | Manual disease seed;Manual variant seed | Exact symbol + exact canonical variant. |
| case_002 | EASY | Manual disease seed;Manual variant seed | Exact symbol + exact canonical variant. |
| case_003 | EASY | Manual disease seed;Manual variant seed | Exact symbol + exact canonical variant. |
| case_004 | EASY | Manual disease seed;Manual variant seed | Exact symbol + exact canonical variant. |
| case_005 | EASY | Manual disease seed;Manual variant seed | Exact symbol + exact canonical variant. |
| case_006 | EASY | Manual disease seed;Manual variant seed | Exact symbol + exact canonical variant. |
| case_007 | EASY | Manual disease seed;Manual variant seed | Exact symbol + exact canonical variant. |
| case_008 | EASY | Manual disease seed;Manual variant seed | Exact symbol + exact canonical variant. |
| case_009 | EASY | Manual disease seed;Manual variant seed | Exact symbol + exact canonical variant. |
| case_010 | EASY | Manual disease seed;Manual variant seed | Exact symbol + exact canonical variant. |
| case_011 | EASY | Manual disease seed;Manual variant seed | Exact symbol + exact canonical variant. |
| case_012 | EASY | Manual disease seed;Manual variant seed | Exact symbol + exact canonical variant. |
| case_013 | MEDIUM | HGNC-derived;Manual disease seed;Manual variant seed | Gene alias + variant shorthand/synonym. |
| case_014 | MEDIUM | HGNC-derived;Manual disease seed;Manual variant seed | Gene alias + variant shorthand/synonym. |
| case_015 | MEDIUM | HGNC-derived;Manual disease seed;Manual variant seed | Gene alias + variant shorthand/synonym. |
| case_016 | MEDIUM | HGNC-derived;Manual disease seed;Manual variant seed | Gene alias + variant shorthand/synonym. |
| case_017 | MEDIUM | HGNC-derived;Manual disease seed;Manual variant seed | Gene alias + variant shorthand/synonym. |
| case_018 | MEDIUM | HGNC-derived;Manual disease seed;Manual variant seed | Gene alias + variant shorthand/synonym. |
| case_019 | MEDIUM | HGNC-derived;Manual disease seed;Manual variant seed | Gene alias + variant shorthand/synonym. |
| case_020 | MEDIUM | HGNC-derived;Manual disease seed;Manual variant seed | Gene alias + variant shorthand/synonym. |
| case_021 | MEDIUM | HGNC-derived;Manual disease seed;Manual variant seed | Gene alias + variant shorthand/synonym. |
| case_022 | MEDIUM | HGNC-derived;Manual disease seed;Manual variant seed | Gene alias + variant shorthand/synonym. |
| case_023 | MEDIUM | HGNC-derived;Manual disease seed;Manual variant seed | Gene alias + variant shorthand/synonym. |
| case_024 | MEDIUM | HGNC-derived;Manual disease seed;Manual variant seed | Gene alias + variant shorthand/synonym. |
| case_025 | DIFFICULT | HGNC-derived;Synthetic ambiguity test | Ambiguous disease and copy-number phrasing. |
| case_026 | DIFFICULT | Synthetic ambiguity test | Ambiguous disease + non-specific variant wording. |
| case_027 | DIFFICULT | Synthetic ambiguity test | Unknown gene negative control. |
| case_028 | DIFFICULT | Manual disease seed;Synthetic ambiguity test | Known gene, unresolved variant wording. |
| case_029 | DIFFICULT | HGNC-derived;Synthetic ambiguity test | Non-seed disease alias and fuzzy variant phrase. |
| case_030 | DIFFICULT | Synthetic ambiguity test | Abbreviated disease + shorthand variant phrase. |
| case_031 | DIFFICULT | Manual disease seed;Synthetic ambiguity test | Ambiguous hotspot class without exact substitution. |
| case_032 | DIFFICULT | Manual disease seed;Synthetic ambiguity test | Unknown variant negative control. |
