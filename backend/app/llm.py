"""
LLM disambiguation module — model-agnostic interface.

Supports: Claude (Anthropic), GPT-4o (OpenAI), or a stub fallback.
Configured via environment variables:
    LLM_PROVIDER=claude | openai | stub   (default: stub)
    ANTHROPIC_API_KEY=...
    OPENAI_API_KEY=...
"""

import os
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "stub").lower()

SYSTEM_PROMPT = """You are an oncology entity reconciliation expert.
Given an ambiguous oncology term and a list of candidate canonical entities,
select the best match and explain why in 1-2 sentences.
Respond ONLY with valid JSON in this exact format:
{
  "best_match": "<canonical name or null>",
  "confidence": <0.0-1.0>,
  "rationale": "<plain-English explanation>",
  "alternatives_considered": ["<alt1>", "<alt2>"]
}
Never include markdown code fences. Never add extra keys."""


def _build_user_prompt(entity_type: str, input_value: str, candidates: list[str], context: dict) -> str:
    candidates_str = "\n".join(f"  - {c}" for c in candidates) if candidates else "  (none found)"
    ctx_str = ", ".join(f"{k}={v}" for k, v in context.items() if v) or "unknown"
    return (
        f"Entity type: {entity_type}\n"
        f"Input value: \"{input_value}\"\n"
        f"Clinical context: {ctx_str}\n"
        f"Candidate canonical entities:\n{candidates_str}\n\n"
        "Select the best match or return null if none are appropriate."
    )


def _call_claude(user_prompt: str) -> dict:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text = msg.content[0].text.strip()
        return json.loads(text)
    except Exception as e:
        logger.warning(f"Claude LLM call failed: {e}")
        return _stub_response()


def _call_openai(user_prompt: str) -> dict:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        resp = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=512,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        text = resp.choices[0].message.content.strip()
        return json.loads(text)
    except Exception as e:
        logger.warning(f"OpenAI LLM call failed: {e}")
        return _stub_response()


def _stub_response() -> dict:
    """Safe deterministic fallback when no LLM is configured."""
    return {
        "best_match": None,
        "confidence": 0.0,
        "rationale": "LLM disambiguation not configured. Set LLM_PROVIDER env var.",
        "alternatives_considered": [],
    }


def disambiguate(
    entity_type: str,
    input_value: str,
    candidates: list[str],
    context: Optional[dict] = None,
) -> dict:
    """
    Main entry point. Call with entity_type='disease'|'gene'|'variant',
    the raw input value, a list of candidate canonical strings, and
    optional context dict (e.g. {'cancer_type': 'NSCLC', 'gene': 'EGFR'}).

    Returns:
        {
          "best_match": str | None,
          "confidence": float,
          "rationale": str,
          "alternatives_considered": list[str],
          "provider": str,
        }
    """
    context = context or {}
    user_prompt = _build_user_prompt(entity_type, input_value, candidates, context)

    if LLM_PROVIDER == "claude":
        result = _call_claude(user_prompt)
    elif LLM_PROVIDER == "openai":
        result = _call_openai(user_prompt)
    else:
        result = _stub_response()

    result["provider"] = LLM_PROVIDER
    return result
