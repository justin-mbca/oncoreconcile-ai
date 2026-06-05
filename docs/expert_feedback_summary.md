# Expert Feedback Summary

## Purpose

This document summarizes external expert feedback collected during development of OncoReconcile AI and describes how that feedback influenced product direction and architecture decisions.

---

# Daniel Puthawala, PhD

## Role

CAT-VRS Maintainer

GA4GH Genomic Knowledge Standards Contributor

---

## Key Feedback

### Interpretation Bottleneck

Normalization and evidence retrieval alone do not solve real-world interoperability challenges.

Additional challenges include:

* Knowledge matching
* EHR integration
* Clinical reporting
* Auditability
* Clinical decision support workflows

---

### Standards Alignment

Standards are important because they provide a common interoperable data environment.

Relevant standards include:

* CAT-VRS
* VRS
* VA-Spec
* HL7 FHIR

---

### Provenance

Provenance and auditability should be first-class concerns.

---

### Future AI Opportunities

AI can assist many areas of reconciliation and interpretation workflows, depending on the specific problem being addressed.

---

## Impact on OncoReconcile AI

Changes made:

* Added Cannot Reconcile outcome
* Strengthened audit trail requirements
* Added future standards-aligned architecture
* Added provenance roadmap
* Reduced MVP scope

---

# Dr. Xiuhua Dong

## Role

Molecular Diagnostics Laboratory Director

---

## Key Feedback

* Variant ambiguity is common.
* Human review remains important.
* Explainability improves trust.
* Traceability is critical.

---

## Impact on OncoReconcile AI

Changes made:

* Added review workflows
* Strengthened confidence scoring
* Improved explainability goals
* Increased focus on auditability

---

# PlasmoLab Feedback

## Key Recommendations

* Keep the first version simple and strict.
* Preserve uncertainty.
* Separate extraction from interpretation.
* Use canonical representations.
* Treat evidence as supporting context, not recommendations.
* Make Cannot Reconcile a first-class outcome.
* Prioritize strong audit trails.

---

## Impact on OncoReconcile AI

Changes made:

* Reduced MVP scope
* Increased auditability focus
* Added canonical object roadmap
* Added benchmark provenance work
* Strengthened human review workflows

---

# Overall Lessons

Across all expert feedback, several themes consistently emerged:

* Trust is more important than scope.
* Explainability is essential.
* Provenance matters.
* Human review remains necessary.
* Standards improve interoperability but do not replace expert judgment.

These lessons continue to guide the development of OncoReconcile AI.
