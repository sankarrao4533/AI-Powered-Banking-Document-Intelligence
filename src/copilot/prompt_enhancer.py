"""Domain prompt enhancer and acronym expander for banking queries."""

from __future__ import annotations

import re
from typing import Optional

from src.config import settings

BANKING_ACRONYMS = {
    r"\bnri\b": "Non-Resident Indian (NRI)",
    r"\bmsme\b": "Micro, Small, and Medium Enterprises (MSME)",
    r"\bpan\b": "Permanent Account Number (PAN)",
    r"\btds\b": "Tax Deducted at Source (TDS)",
    r"\bfd\b": "Fixed Deposit (FD) term deposit",
    r"\blc\b": "Letter of Credit (LC) trade guarantee",
    r"\bltv\b": "Loan-to-Value (LTV)",
    r"\baml\b": "Anti-Money Laundering (AML)",
    r"\bkyc\b": "Know Your Customer (KYC)",
    r"\bnre\b": "Non-Resident External (NRE) account",
    r"\bnro\b": "Non-Resident Ordinary (NRO) account",
    r"\broi\b": "Rate of Interest",
    r"\blounge\b": "airport lounge access limits and quarterly spend",
}


def enhance_banking_query(user_query: str) -> str:
    """Rewrite shorthand user query into an audit-grade retrieval intent string."""
    text = user_query.strip()
    if not text:
        return ""

    # Attempt LLM expansion if Groq is available
    if settings.GROQ_API_KEY:
        try:
            import concurrent.futures
            from groq import Groq

            def _call_groq():
                client = Groq(api_key=settings.GROQ_API_KEY, timeout=4.0)
                prompt = (
                    "You are an expert banking compliance AI. Rewrite the following user query into a concise, "
                    "formal banking policy retrieval query. Keep under 2 sentences. "
                    "Expand banking acronyms (PAN, NRI, TDS, FD, LC, MSME). Do not add conversational text.\n\n"
                    f"Query: {text}"
                )
                candidates = [
                    settings.GROQ_MODEL,
                    "llama-3.1-8b-instant",
                    "llama-3.3-70b-versatile",
                    "llama-3.2-3b-preview",
                    "llama-3.2-1b-preview",
                    "mixtral-8x7b-32768",
                ]
                for model_name in dict.fromkeys(candidates):
                    if not model_name:
                        continue
                    try:
                        resp = client.chat.completions.create(
                            model=model_name,
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=100,
                            temperature=0.0,
                        )
                        return resp.choices[0].message.content.strip()
                    except Exception as me:
                        err_str = str(me).lower()
                        if any(k in err_str for k in ("decommissioned", "not_found", "does not exist", "access", "400", "404")):
                            continue
                        raise
                return None

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_call_groq)
                enhanced = future.result(timeout=2.0)
                if enhanced and len(enhanced) > 5:
                    return enhanced
        except Exception:
            pass

    # Instant resilient domain-heuristic expansion
    expanded = text
    for pattern, replacement in BANKING_ACRONYMS.items():
        expanded = re.sub(pattern, replacement, expanded, flags=re.IGNORECASE)

    # Normalize tone
    if not expanded.endswith("?"):
        expanded = f"What are the official active policy rules regarding {expanded}?"

    return expanded
