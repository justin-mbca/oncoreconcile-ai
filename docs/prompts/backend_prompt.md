# Backend Vibe Coding Prompt

Build a FastAPI endpoint for OncoReconcile AI.

Endpoint:
POST /reconcile

Input:
case_id, cancer_type, gene, variant

Output:
canonical cancer type, canonical gene, canonical variant, evidence, explanation, confidence, review_status

Rules:
- Follow contracts/api_contract.md
- Do not make treatment recommendations
- Use local JSON dictionaries first
- Return AUTO_RECONCILE, REVIEW_REQUIRED, or CANNOT_RECONCILE
