"""Chat and governance status rendering components for Streamlit frontend."""

from __future__ import annotations

from typing import Any, List, Optional
import streamlit as st


def render_governance_badge(status: str) -> None:
    """Render a badge showing the governance gate outcome."""
    if status == "VERIFIED_ACTIVE":
        st.markdown(
            """
            <span style="
                background: rgba(16, 185, 129, 0.2);
                color: #34D399;
                border: 1px solid rgba(52, 211, 153, 0.4);
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: 600;
                display: inline-block;
                margin-bottom: 8px;
            ">
                🛡️ Verified Active Policy Context
            </span>
            """,
            unsafe_allow_html=True,
        )
    elif status == "FALLBACK_NO_ACTIVE_POLICY":
        st.markdown(
            """
            <span style="
                background: rgba(239, 68, 68, 0.2);
                color: #F87171;
                border: 1px solid rgba(248, 113, 113, 0.4);
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: 600;
                display: inline-block;
                margin-bottom: 8px;
            ">
                ⚠️ Strict Fallback: No Verified Active Policy Found
            </span>
            """,
            unsafe_allow_html=True,
        )


def render_chat_bubble(
    role: str,
    content: str,
    citations: Optional[List[Any]] = None,
    confidence: float = 0.0,
    governance_status: Optional[str] = None,
) -> None:
    """Render styled message bubble."""
    is_user = role.lower() == "user"
    align = "flex-end" if is_user else "flex-start"
    bg = "rgba(20, 184, 166, 0.2)" if is_user else "rgba(15, 30, 36, 0.65)"
    border = "1px solid rgba(153, 225, 217, 0.3)" if is_user else "1px solid rgba(153, 225, 217, 0.15)"

    st.markdown(
        f"""
        <div style="display: flex; justify-content: {align}; margin-bottom: 14px;">
            <div style="
                max-width: 85%;
                background: {bg};
                border: {border};
                border-radius: 14px;
                padding: 14px 18px;
                color: #F1F5F9;
                font-size: 0.95rem;
                line-height: 1.5;
            ">
                <div style="font-size: 0.75rem; color: #94A3B8; margin-bottom: 4px; font-weight: 600;">
                    {"👤 Banking Officer" if is_user else "🤖 Sentinel Co-Pilot"}
                </div>
                <div>{content}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
