"""LLM Service orchestrating multi-provider completions with strict fallback.

Supports Groq, Google Gemini, and deterministic offline grounded templates
with custom timeouts and graceful error recovery.
"""

from __future__ import annotations

import concurrent.futures
from typing import Optional

from backend.config import backend_settings
from src.copilot.agent import COPILOT_SYSTEM_PROMPT


class LLMService:
    """Enterprise LLM execution service with multi-provider failover."""

    def __init__(
        self,
        groq_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        timeout: float = 6.0,
    ):
        self.groq_api_key = groq_api_key or backend_settings.GROQ_API_KEY
        self.gemini_api_key = gemini_api_key or backend_settings.GEMINI_API_KEY
        self.default_timeout = timeout

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> str:
        """Attempt Groq, Gemini, or fallback to deterministic grounded synthesis."""
        effective_timeout = timeout or self.default_timeout
        sys_prompt = system_prompt or COPILOT_SYSTEM_PROMPT

        # 1. Attempt Groq
        if self.groq_api_key:
            res = self._call_groq(prompt, sys_prompt, effective_timeout)
            if res:
                return res

        # 2. Attempt Gemini
        if self.gemini_api_key:
            res = self._call_gemini(prompt, sys_prompt, effective_timeout)
            if res:
                return res

        # 3. Grounded Deterministic Template (Zero External API Dependency)
        return self._grounded_fallback_synthesis(prompt)

    def _call_groq(self, prompt: str, system_prompt: str, timeout: float) -> Optional[str]:
        try:
            from groq import Groq
            client = Groq(api_key=self.groq_api_key, timeout=timeout)
            models = ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "llama-3.2-3b-preview"]
            for m in models:
                try:
                    resp = client.chat.completions.create(
                        model=m,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.0,
                    )
                    if resp.choices and resp.choices[0].message.content:
                        return resp.choices[0].message.content.strip()
                except Exception as model_err:
                    err_str = str(model_err).lower()
                    if any(k in err_str for k in ("decommissioned", "not_found", "400", "404")):
                        continue
                    break
        except Exception:
            pass
        return None

    def _call_gemini(self, prompt: str, system_prompt: str, timeout: float) -> Optional[str]:
        try:
            from google import genai

            def _invoke():
                client = genai.Client(api_key=self.gemini_api_key)
                full_text = f"{system_prompt}\n\n{prompt}"
                for m in ["gemini-2.0-flash", "gemini-1.5-flash"]:
                    try:
                        resp = client.models.generate_content(model=m, contents=full_text)
                        if resp.text:
                            return resp.text.strip()
                    except Exception:
                        continue
                return None

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_invoke)
                return future.result(timeout=timeout)
        except Exception:
            pass
        return None

    def _grounded_fallback_synthesis(self, prompt: str) -> str:
        """Deterministic policy synthesis directly extracting facts from evidence blocks."""
        lines = prompt.split("\n")
        user_q = ""
        for line in lines:
            if line.startswith("User Question:"):
                user_q = line.split("User Question:", 1)[-1].strip()

        extracted_rules = []
        customer_segments = set()
        required_docs = set()
        sources = []

        current_doc = ""
        for line in lines:
            line_str = line.strip()
            if line_str.startswith("[Source"):
                current_doc = line_str.split("]:", 1)[-1].strip()
                if current_doc and current_doc not in sources:
                    sources.append(current_doc)
            elif line_str.startswith("- Extracted Rule:"):
                r = line_str.replace("- Extracted Rule:", "").strip()
                if r:
                    extracted_rules.append(r)
            elif line_str.startswith("- Applies to:"):
                c = line_str.replace("- Applies to:", "").strip()
                if c and c != "General Banking Customers":
                    for item in c.split(","):
                        customer_segments.add(item.strip())
            elif line_str.startswith("- Requires Documents:"):
                d = line_str.replace("- Requires Documents:", "").strip()
                if d and d != "Standard Account Verification":
                    for item in d.split(","):
                        required_docs.add(item.strip())

        if not extracted_rules:
            return "I cannot find a verified active policy for this in the current database."

        response_parts = [
            f"**Verified Regulatory Policy Summary:**\n{extracted_rules[0]}",
        ]

        if customer_segments:
            response_parts.append(
                f"\n**Applicable Customer Segments:**\n- {', '.join(sorted(customer_segments))}"
            )

        if required_docs:
            response_parts.append(
                f"\n**Mandatory Compliance Documents:**\n- {', '.join(sorted(required_docs))}"
            )

        if sources:
            response_parts.append(
                f"\n**Authoritative Source Reference:**\n- {', '.join(sources)}"
            )

        return "\n".join(response_parts)
