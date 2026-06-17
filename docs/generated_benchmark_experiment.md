# Generated Benchmark Experiment

## Background

The OncoReconcile AI MVP currently uses a curated benchmark dataset for validation and demonstration purposes. While this approach provides clinically meaningful reconciliation scenarios, manual benchmark creation can be difficult to reproduce and scale.

To explore a more reproducible approach, the team conducted a benchmark-generation experiment using publicly available nomenclature resources and manually defined oncology seed rules.

---

## Objective

Evaluate whether public standards-based resources can automatically generate oncology benchmark data and alias mappings while improving reproducibility, provenance, and future standards alignment.

---

## Experimental Approach

The experiment used three categories of inputs:

### Gene Sources

Public nomenclature resources:

* HGNC gene nomenclature
* HGNC gene aliases

Target genes included:

* EGFR
* KRAS
* ALK
* ROS1
* RET
* MET
* ERBB2
* TP53
* BRAF
* PIK3CA
* NTRK family

### Disease Seeds

Manually defined oncology disease aliases:

* NSCLC
* Non-Small Cell Lung Cancer
* LUAD
* Lung Adenocarcinoma

### Variant Seeds

Manually defined variant concepts:

* EGFR Exon 19 Deletion
* EGFR L858R
* EGFR T790M
* KRAS G12C
* MET Exon 14 Skipping
* ERBB2 Amplification
* ALK Fusion
* ROS1 Fusion
* RET Fusion
* BRAF V600E
* TP53 R175H
* PIK3CA E545K

---

## Generated Outputs

The workflow generated:

* Candidate benchmark cases
* Candidate alias mappings
* Provenance information
* Synthetic ambiguity test cases

Each generated row included:

* cancer_type
* gene
* variant
* expected canonical outputs
* difficulty level
* source
* curation notes

---

## Findings

### Positive Findings

Public APIs improved:

* Reproducibility
* Traceability
* Provenance
* Benchmark generation speed

Public resources successfully generated many clinically meaningful oncology concepts.

Examples:

* EGFR Exon 19 Deletion
* KRAS G12C
* BRAF V600E
* MET Exon 14 Skipping

---

### Limitations

Some generated aliases were technically correct but clinically unrealistic.

Examples:

* CD340 → ERBB2
* DFNB97 → MET
* LFS1 → TP53

Although these aliases are recognized in nomenclature resources, they are rarely encountered in modern molecular oncology workflows.

---

## Key Lessons

The experiment demonstrated:

Public APIs can generate candidate benchmark cases.

Public APIs cannot automatically generate trusted oncology benchmark truth.

Human review remains necessary.

---

## Architectural Impact

The experiment introduced the concept of a Clinical Curation Filter.

Future workflow:

Public Resources

↓

Candidate Generation

↓

Clinical Curation Filter

↓

Approved Oncology Dictionary

↓

Curated Benchmark

↓

Reconciliation Engine

---

## Future Work

Future benchmark generation may incorporate:

* VICC Gene Normalizer
* VICC Variation Normalizer
* CAT-VRS concepts
* ClinVar
* CIViC
* Additional oncology ontologies

while preserving provenance tracking and human review requirements.

---

## Conclusion

The generated benchmark experiment demonstrated that reproducibility and provenance can be improved through standards-based resources. However, benchmark promotion requires clinical review to ensure realism and relevance for oncology reconciliation workflows.
