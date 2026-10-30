"""Banking compliance Co-Pilot agent enforcing grounded synthesis and strict auditability."""

from __future__ import annotations

import os
import uuid
from typing import List, Optional

from src.config import settings
from src.copilot.prompt_enhancer import enhance_banking_query
from src.models.schemas import ActivePolicy, ChatMessage, ChatResponse
from src.retrieval.hybrid_retriever import STRICT_NO_ANSWER, HybridRetriever
from src.storage.base import BaseStorage
from src.storage.factory import get_storage


COPILOT_SYSTEM_PROMPT = """
You are the Sentinel Enterprise Banking Assistant, an authoritative AI assistant for banking compliance and policy governance.

CORE GOVERNANCE DIRECTIVES:
1. Strict Grounding: You must synthesize your answer ONLY from the provided Verified Active Policy Context.
2. Supersession Awareness: Never cite or acknowledge superseded or outdated rules. All provided context has passed the Supersession Firewall.
3. No Speculation: If the active policy context does NOT directly answer the question, fail closed and respond strictly with:
   "I cannot find a verified active policy for this in the current database."
4. Structure:
   - State the authoritative active rule clearly with exact numbers, interest rates, currency thresholds, and limits.
   - Specify applicable customer segments (e.g., NRI, MSME, Corporate, Senior Citizens).
   - List mandatory documentation requirements (e.g., PAN Card, Passport, Trade License).
   - Conclude with explicit source attribution citing the active policy document name and category.
"""


class CopilotAgent:
    """Conversational banking intelligence agent with active policy grounding."""

    def __init__(self, storage: Optional[BaseStorage] = None):
        self.storage = storage or get_storage()
        self.retriever = HybridRetriever(self.storage)

    def answer_question(
        self,
        user_question: str,
        session_id: Optional[str] = None,
        enhance_query: bool = False,
    ) -> ChatResponse:
        """Process user question through GraphRAG retrieval and grounded generation."""
        sid = session_id or str(uuid.uuid4())
        original_query = user_question.strip()

        # 1. Query Enhancement
        search_query = original_query
        enhanced_text = None
        if enhance_query:
            enhanced_text = enhance_banking_query(original_query)
            search_query = enhanced_text

        # 2. Hybrid Retrieval with Supersession Firewall
        citations: List[ActivePolicy] = self.retriever.retrieve(
            query=search_query,
            top_k=settings.TOP_K,
            min_confidence=settings.MIN_CONFIDENCE_THRESHOLD,
        )

        # 3. Governance Gate: Strict Fallback if no verified active policy exists
        if not citations:
            fallback_reply = STRICT_NO_ANSWER
            self.storage.save_chat_message(
                session_id=sid,
                role="user",
                content=original_query,
                citations=[],
            )
            self.storage.save_chat_message(
                session_id=sid,
                role="assistant",
                content=fallback_reply,
                citations=[],
            )
            return ChatResponse(
                session_id=sid,
                response=fallback_reply,
                citations=[],
                confidence_score=0.0,
                governance_status="FALLBACK_NO_ACTIVE_POLICY",
                enhanced_query=enhanced_text,
            )

        # 4. Context Synthesis
        context_blocks = []
        for idx, cit in enumerate(citations, 1):
            cust_str = ", ".join(cit.customer_types) if cit.customer_types else "General Banking Customers"
            doc_str = ", ".join(cit.required_docs) if cit.required_docs else "Standard Account Verification"
            block = (
                f"[Source {idx}]: {cit.document_name} ({cit.category})\n"
                f"- Extracted Rule: {cit.extracted_rule}\n"
                f"- Applies to: {cust_str}\n"
                f"- Requires Documents: {doc_str}\n"
                f"- Source Text Excerpt: {cit.source_text[:400]}"
            )
            context_blocks.append(block)

        context_str = "\n\n".join(context_blocks)

        # 5. Fetch Session History
        history = self.storage.get_session_messages(sid, limit=4)
        history_str = ""
        if history:
            turn_texts = [f"{msg.role.upper()}: {msg.content}" for msg in history]
            history_str = "\nRecent Conversation History:\n" + "\n".join(turn_texts) + "\n"

        user_prompt = (
            f"{history_str}\n"
            f"Verified Active Policy Context:\n{context_str}\n\n"
            f"User Question: {original_query}\n\n"
            "Synthesize an authoritative, policy-grounded answer based strictly on the context above."
        )

        # 6. LLM Response Generation (Groq -> Gemini -> Grounded Synthesizer)
        answer = self._generate_llm_response(user_prompt)

        # Governance status check: if answer failed closed, mark as fallback
        if answer == STRICT_NO_ANSWER or "cannot find a verified active policy" in answer.lower():
            governance_status = "FALLBACK_NO_ACTIVE_POLICY"
            citations = []
            avg_confidence = 0.0
        else:
            governance_status = "VERIFIED_ACTIVE"
            avg_confidence = (
                round(sum(c.match_confidence for c in citations) / len(citations), 1)
                if citations
                else 0.0
            )

        # 7. Persist to Session Memory
        self.storage.save_chat_message(
            session_id=sid,
            role="user",
            content=original_query,
            citations=[],
        )
        self.storage.save_chat_message(
            session_id=sid,
            role="assistant",
            content=answer,
            citations=citations,
        )

        return ChatResponse(
            session_id=sid,
            response=answer,
            citations=citations,
            confidence_score=avg_confidence,
            governance_status=governance_status,
            enhanced_query=enhanced_text,
        )

    def _generate_llm_response(self, user_prompt: str) -> str:
        """Call Groq, Gemini, or deterministic Grounded Template Generator."""
        # 1. Try Groq
        if settings.GROQ_API_KEY:
            try:
                from groq import Groq
                client = Groq(api_key=settings.GROQ_API_KEY, timeout=5.0)
                groq_candidates = [
                    settings.GROQ_MODEL,
                    "llama-3.1-8b-instant",
                    "llama-3.3-70b-versatile",
                    "llama-3.2-3b-preview",
                    "llama-3.2-1b-preview",
                    "mixtral-8x7b-32768",
                ]
                for model_name in dict.fromkeys(groq_candidates):
                    if not model_name:
                        continue
                    try:
                        resp = client.chat.completions.create(
                            model=model_name,
                            messages=[
                                {"role": "system", "content": COPILOT_SYSTEM_PROMPT},
                                {"role": "user", "content": user_prompt},
                            ],
                            temperature=0.0,
                        )
                        return resp.choices[0].message.content.strip()
                    except Exception as model_err:
                        err_str = str(model_err).lower()
                        if any(k in err_str for k in ("decommissioned", "not_found", "does not exist", "access", "400", "404")):
                            continue
                        raise
            except Exception as e:
                print(f"[CopilotAgent] Groq generation unavailable/timed out: {e}")

        # 2. Try Gemini
        if settings.GEMINI_API_KEY:
            try:
                import concurrent.futures
                from google import genai

                def _call_gemini():
                    client = genai.Client(api_key=settings.GEMINI_API_KEY)
                    full_text = f"{COPILOT_SYSTEM_PROMPT}\n\n{user_prompt}"
                    gemini_candidates = [
                        settings.GEMINI_MODEL,
                        "gemini-3.8-flash",
                        "gemini-2.0-flash",
                        "gemini-1.5-flash",
                    ]
                    for model_name in dict.fromkeys(gemini_candidates):
                        try:
                            resp = client.models.generate_content(
                                model=model_name,
                                contents=full_text,
                            )
                            return resp.text.strip()
                        except Exception as m_err:
                            if "NOT_FOUND" in str(m_err) or "404" in str(m_err):
                                continue
                            raise
                    raise RuntimeError("No compatible Gemini model found.")

                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(_call_gemini)
                    return future.result(timeout=6.0)
            except Exception as e:
                print(f"[CopilotAgent] Gemini generation unavailable/timed out: {e}")

        # 3. Grounded Fallback Synthesizer (Zero external API dependencies)
        return self._grounded_template_synthesis(user_prompt)

    def _grounded_template_synthesis(self, prompt: str) -> str:
        """Format an authoritative response directly from retrieved evidence blocks."""
        import re
        lines = prompt.split("\n")
        sources = []
        current_rule = ""
        current_doc = ""
        current_cust = ""
        current_req = ""

        # Extract user question from prompt
        user_q = ""
        for line in lines:
            if line.startswith("User Question:"):
                user_q = line.split("User Question:", 1)[-1].strip()

        for line in lines:
            if line.startswith("[Source"):
                current_doc = line.split("]:", 1)[-1].strip()
            elif "- Extracted Rule:" in line:
                current_rule = line.split("- Extracted Rule:", 1)[-1].strip()
            elif "- Applies to:" in line:
                current_cust = line.split("- Applies to:", 1)[-1].strip()
            elif "- Requires Documents:" in line:
                current_req = line.split("- Requires Documents:", 1)[-1].strip()
                if current_doc and current_rule:
                    sources.append(
                        {
                            "doc": current_doc,
                            "rule": current_rule,
                            "cust": current_cust,
                            "req": current_req,
                        }
                    )

        if not sources:
            return STRICT_NO_ANSWER

        # Governance Check: detect queries asking about completely unverified external subjects
        common_words = {
            "what", "which", "when", "where", "who", "why", "how", "does", "will", "would",
            "the", "and", "for", "with", "from", "are", "have", "been", "this", "that", "any",
            "rate", "rates", "interest", "policy", "rules", "rule", "card", "cards",
            "bank", "banking", "sentinel", "active", "directive", "about", "customer", "customers",
            "loan", "loans", "limits", "limit", "amount", "guidelines", "general",
            "verified", "context", "question", "synthesize", "authoritative",
            "procedure", "procedures", "require", "requires", "required", "requirements",
            "particular", "currently", "valid", "applying", "apply", "applicant", "applicants",
            "documents", "document", "documentation", "details", "needed", "need",
            "give", "tell", "show", "list", "explain", "information", "info", "specifies",
            "terms", "term", "code", "year", "years", "time", "date", "status"
        }
        user_tokens = [w for w in re.findall(r"\b[a-z]{3,}\b", user_q.lower()) if w not in common_words]
        all_evidence = " ".join([s["rule"] + " " + s["doc"] + " " + s["cust"] + " " + s["req"] for s in sources]).lower()

        # If user asked about substantive nouns that never appear anywhere in the active context, fail closed
        if user_tokens:
            unmatched = [t for t in user_tokens if t not in all_evidence]
            if len(unmatched) >= max(1, len(user_tokens) * 0.7):
                return STRICT_NO_ANSWER

        resp = f"### Verified Banking Policy Assessment\n\n"
        # Synthesize top active policy sources
        for idx, s in enumerate(sources[:2], 1):
            doc_display = s["doc"].replace(".pdf", "").replace("_", " ")
            resp += f"#### {doc_display}\n"
            resp += f"**Official Directive:**\n{s['rule']}\n\n"
            if s["cust"] and s["cust"] != "General Banking Customers":
                resp += f"- **Applicable Customer Segment:** `{s['cust']}`\n"
            if s["req"]:
                resp += f"- **Mandatory Documentation Required:** `{s['req']}`\n"
            resp += f"\n*Governance Source: `{s['doc']}` (Status: Active Verified)*\n\n"

        return resp.strip()
