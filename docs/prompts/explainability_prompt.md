# Explainability Prompt

Given an input oncology entity and its canonical reconciliation result, generate a plain-language explanation.

Requirements:
- Explain why the mapping occurred
- Mention evidence source if available
- Do not provide clinical interpretation
- Do not recommend therapy
- Keep explanation concise

Example:
Input: HER2 + Amplification
Canonical: ERBB2 Amplification
Evidence: HER2 is an alias of ERBB2

Output:
HER2 was reconciled to ERBB2 because HER2 is a recognized alias. Amplification was mapped in the context of ERBB2 to produce ERBB2 Amplification.
