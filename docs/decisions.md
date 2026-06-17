# Decision Log

## Decision 001: Human-Governed Workbench

Date: 2026-06-01

Decision:
The MVP will be positioned as a Human-Governed Oncology Reconciliation Workbench.

Reason:
Expert feedback and clinical genomics best practices indicate that human review remains essential for ambiguous records.

---

## Decision 002: Scope Reduction

Date: 2026-06-01

Decision:
PDF extraction, OCR, treatment recommendation, and clinical interpretation are excluded from the MVP.

Reason:
These features increase risk and are not required to demonstrate the core value.

---

## Decision 003: Simplified Canonical Object Before CAT-VRS

Date: 2026-06-01

Decision:
The MVP will use a simplified Canonical Oncology Concept Object.

Reason:
GA4GH VRS/CAT-VRS alignment is valuable, but full implementation is too complex for the short competition timeline.

---

## Decision 004: NSCLC First

Date: 2026-06-01

Decision:
The initial benchmark dataset focuses on NSCLC.

Reason:
NSCLC includes common oncology reconciliation challenges: SNVs, indels, fusions, amplifications, and resistance mutations.
