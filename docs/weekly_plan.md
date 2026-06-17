# 5-Week Execution Plan

Assumption: approximately 5 weeks remain before final competition delivery.

---

## Week 1: End-to-End Skeleton

### Goal

One record flows through the system.

```text
Input
↓
Backend reconcile endpoint
↓
Result output
```

### Specific Tasks

| Task | Deliverable | Due |
|---|---|---|
| API contract | `contracts/api_contract.md` finalized | Tue |
| Benchmark data | `data/nsclc_benchmark.csv` with 20 cases | Wed |
| Alias dictionaries | cancer/gene/variant alias JSON files | Thu |
| Backend endpoint | `POST /reconcile` returns sample output | Thu |
| Frontend upload/manual input | simple UI accepts one record | Fri |
| Result display | show output JSON/table | Sun |

### Week 1 Demo

Submit:

```json
{
  "cancer_type": "NSCLC",
  "gene": "HER2",
  "variant": "Amplification"
}
```

Return canonical ERBB2 amplification output.

---

## Week 2: Reconciliation Engine

### Goal

Process all 20 benchmark cases.

### Specific Tasks

| Task | Deliverable | Due |
|---|---|---|
| Cancer reconciliation | map NSCLC/LUAD/etc. | Tue |
| Gene reconciliation | map HER2/p53/etc. | Wed |
| Variant reconciliation | map Ex19del/G12C/etc. | Fri |
| Batch processing | accept multiple records | Fri |
| Tests | basic unit tests for 20 examples | Sun |

### Week 2 Demo

CSV with 20 cases processed end-to-end.

---

## Week 3: Evidence + Explainability

### Goal

Every reconciliation has evidence, explanation, and confidence.

### Specific Tasks

| Task | Deliverable | Due |
|---|---|---|
| Evidence layer | source/type/description for each match | Tue |
| Explanation generator | plain-language explanation | Wed |
| Confidence rules | HIGH/MEDIUM/LOW | Thu |
| Review recommendation | AUTO/REVIEW/CANNOT | Fri |
| UI enhancement | show evidence/explanation/status | Sun |

### Week 3 Demo

20 records with canonical output, evidence, explanation, confidence, and review status.

---

## Week 4: Human Review Workflow + Polish

### Goal

Create a clear demo-ready review workflow.

### Specific Tasks

| Task | Deliverable | Due |
|---|---|---|
| Review queue | filter records needing review | Tue |
| Cannot reconcile handling | clear status and message | Wed |
| CSV/JSON export | download final results | Thu |
| Dashboard summary | total/auto/review/cannot counts | Fri |
| Integration test | full MVP test | Sun |

### Week 4 Demo

Full workflow from upload to output with review queue.

---

## Week 5: Final Competition Delivery

### Goal

No major new features. Focus on presentation, demo, and reliability.

### Specific Tasks

| Task | Deliverable | Due |
|---|---|---|
| Demo script | 5-minute script | Mon |
| Pitch deck content | problem, solution, MVP, impact | Tue |
| Architecture diagram | final diagram | Tue |
| Customer validation summary | 2+ expert/user findings | Wed |
| Demo video | recorded demo | Thu |
| Final testing | bug fixes only | Fri |
| Final rehearsal | team practice | Weekend |

### Week 5 Demo

Polished competition demo and presentation.

---

## Weekly Meeting Format

Each person reports:

```text
Completed:
Working on:
Blocked by:
Need help:
```

Demo working software first. Status discussion second.
