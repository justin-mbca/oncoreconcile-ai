# Architecture

## High-Level Architecture

```mermaid
flowchart TD
    subgraph UI["🖥️ Frontend (React + Vite)"]
        A1[Manual Input Form\ncancer_type / gene / variant]
        A2[CSV Upload\nbatch records]
        A3[Results Table\ncanonical / confidence / review_status]
        A4[Evidence & Explanation Display]
    end

    subgraph API["⚙️ FastAPI Backend"]
        B1["POST /reconcile\nsingle record"]
        B2["POST /reconcile/batch\nmultiple records"]
        B3[reconcile_record\nentry point]
    end

    subgraph Engine["🔬 Reconciliation Engine (reconcile.py)"]
        C1[Cancer Type Reconciliation\nalias lookup]
        C2[Gene Reconciliation\nalias lookup]
        C3[Variant Reconciliation\nalias + gene template]
        C4[Confidence Scoring\nHIGH / MEDIUM / LOW]
        C5[Review Status\nAUTO_RECONCILE / REVIEW_REQUIRED / CANNOT_RECONCILE]
        C6[Explanation Builder\ndeterministic text]
    end

    subgraph Data["📦 Seed Data (data/)"]
        D1[cancer_aliases.json]
        D2[gene_aliases.json]
        D3[variant_aliases.json]
        D4[nsclc_benchmark.csv\n20 benchmark cases]
    end

    subgraph Output["📋 Canonical Oncology Concept Object"]
        E1["canonical:\n  cancer_type\n  gene\n  variant"]
        E2["evidence: [ ]"]
        E3["explanation: string"]
        E4["confidence: HIGH / MEDIUM / LOW"]
        E5["review_status: AUTO / REVIEW / CANNOT"]
    end

    subgraph Future["🔮 Future Integrations (Roadmap)"]
        F1[HGNC]
        F2[ClinVar]
        F3[CIViC / OncoKB]
        F4[GA4GH VRS / CAT-VRS]
    end

    A1 -->|JSON POST| B1
    A2 -->|JSON POST| B2
    B1 --> B3
    B2 --> B3
    B3 --> C1
    B3 --> C2
    B3 --> C3
    C1 --> D1
    C2 --> D2
    C3 --> D3
    C1 --> C4
    C2 --> C4
    C3 --> C4
    C4 --> C5
    C4 --> C6
    C5 --> Output
    C6 --> Output
    Output --> A3
    Output --> A4
    D4 -.->|benchmark validation| Engine
    Data -.->|future connector| Future
```

---

## Backend Components

| Component | Purpose |
|---|---|
| `main.py` | FastAPI app and endpoints |
| `models.py` | Pydantic request/response models |
| `reconcile.py` | Reconciliation engine |
| `evidence.py` | Evidence generation |
| `explain.py` | Explanation generation |
| `rules.py` | Confidence and review rules |

---

## Data Sources for MVP

The MVP starts with local seed dictionaries:

- `data/cancer_aliases.json`
- `data/gene_aliases.json`
- `data/variant_aliases.json`

Future versions can connect to:

- HGNC
- ClinVar
- CIViC
- VICC
- OncoKB if allowed
- GA4GH standards-based services

---

## API Contract

All frontend and backend work should follow:

```text
contracts/api_contract.md
```

Do not change the API contract without team discussion.

---

## Canonical Oncology Concept Object

The internal object should contain:

```json
{
  "canonical": {
    "cancer_type": "",
    "gene": "",
    "variant": ""
  },
  "evidence": [],
  "explanation": "",
  "confidence": "",
  "review_status": ""
}
```

This simplified object may later be mapped to GA4GH VRS or CAT-VRS-compatible structures.
