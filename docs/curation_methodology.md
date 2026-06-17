# Curation Methodology

## Purpose

The OncoReconcile AI benchmark dataset was created to evaluate oncology entity reconciliation workflows.

The benchmark is intended to test:

* Cancer type reconciliation
* Gene reconciliation
* Variant reconciliation
* Confidence scoring
* Review recommendations
* Cannot Reconcile workflows
* Explainability
* Auditability

The benchmark is not intended to represent clinical truth or a comprehensive oncology knowledgebase.

---

## Data Sources

The benchmark was curated using:

* Public oncology knowledge resources
* HGNC nomenclature
* CIViC concepts
* ClinVar terminology
* OncoKB concepts
* Molecular diagnostics terminology
* Team domain expertise

No patient-identifiable information was used.

---

## Curation Principles

### Clinical Realism

Benchmark cases prioritize terminology commonly encountered in oncology workflows.

Examples:

Preferred:

* HER2
* HER-2
* ERBB2
* EGFR Ex19del
* KRAS G12C

Avoided:

* Rare historical aliases
* Obsolete nomenclature
* Uncommon reporting terms

---

### Representative Coverage

The benchmark includes:

#### Disease Aliases

Examples:

* NSCLC
* Non-Small Cell Lung Cancer
* LUAD
* Lung Adenocarcinoma

#### Gene Aliases

Examples:

* HER2 → ERBB2
* HER-2 → ERBB2
* p53 → TP53

#### Variant Synonyms

Examples:

* Ex19del
* del19
* E746_A750del

#### Fusions

Examples:

* ALK Fusion
* RET Fusion
* ROS1 Rearrangement

#### Copy Number Alterations

Examples:

* Amplification
* Copy Gain

---

### Difficulty Stratification

Benchmark cases are assigned difficulty levels.

#### EASY

Canonical or common terminology.

Examples:

* EGFR L858R
* KRAS G12C

#### MEDIUM

Alias or shorthand normalization required.

Examples:

* HER2 Amplification
* p53 R175H

#### DIFFICULT

Ambiguous or incomplete terminology.

Examples:

* Unknown Gene
* ALK Positive
* Copy Gain

---

### Human Review

The benchmark intentionally contains examples requiring review.

Examples:

* Ambiguous diseases
* Ambiguous variants
* Missing context
* Unknown entities

These scenarios support evaluation of:

* Confidence scoring
* Review recommendations
* Cannot Reconcile outcomes

---

## Benchmark Promotion Rules

Generated candidate cases may be promoted if they are:

* Clinically meaningful
* Traceable to authoritative resources
* Useful for reconciliation testing
* Consistent with oncology reporting terminology

Otherwise they may be classified as:

* Needs Review
* Rejected
* Synthetic Negative Control

---

## Provenance

Every benchmark case should be traceable to:

* Public source
* Manual seed rule
* Generated experiment
* Team curation decision

Future versions may include explicit provenance fields.

---

## Summary

The benchmark balances:

* Clinical realism
* Explainability
* Provenance
* Reproducibility
* Validation coverage

while maintaining transparency regarding how benchmark truth was established.
