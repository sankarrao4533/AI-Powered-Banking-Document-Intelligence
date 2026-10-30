"""Reusable card components for Streamlit frontend."""

from __future__ import annotations

import streamlit as st


def render_kpi_card(title: str, value: str | int, subtitle: str = "", icon: str = "📊") -> None:
    """Render a glassmorphic KPI metric card."""
    st.markdown(
        f"""
        <div class="kpi-card" style="
            background: rgba(14, 37, 42, 0.52);
            backdrop-filter: blur(14px);
            border: 1px solid rgba(153, 225, 217, 0.2);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            margin-bottom: 12px;
        ">
            <div style="font-size: 1.8rem; margin-bottom: 4px;">{icon}</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: #99E1D9;">{value}</div>
            <div style="font-size: 0.85rem; font-weight: 600; color: #E0F2FE; text-transform: uppercase;">{title}</div>
            {f'<div style="font-size: 0.75rem; color: #94A3B8; margin-top: 4px;">{subtitle}</div>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_citation_card(citation: dict | Any, index: int = 1) -> None:
    """Render a structured citation card with document source and metadata."""
    doc_name = getattr(citation, "document_name", citation.get("document_name", "Unknown"))
    category = getattr(citation, "category", citation.get("category", "General"))
    rule = getattr(citation, "extracted_rule", citation.get("extracted_rule", ""))
    confidence = getattr(citation, "match_confidence", citation.get("match_confidence", 0.0))

    st.markdown(
        f"""
        <div style="
            background: rgba(20, 48, 54, 0.45);
            border-left: 3px solid #14B8A6;
            border-radius: 6px;
            padding: 10px 14px;
            margin-bottom: 8px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 600; color: #99E1D9; font-size: 0.9rem;">
                    [{index}] {doc_name}
                </span>
                <span style="font-size: 0.75rem; background: rgba(20, 184, 166, 0.2); color: #5EEAD4; padding: 2px 8px; border-radius: 10px;">
                    {confidence:.1f}% Match
                </span>
            </div>
            <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 2px;">Category: {category}</div>
            <div style="font-size: 0.82rem; color: #E2E8F0; margin-top: 4px;">{rule}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_policy_item(policy: Any) -> None:
    """Render a policy record card."""
    name = getattr(policy, "name", "Policy")
    category = getattr(policy, "category", "Banking")
    active = getattr(policy, "active", True)
    status_label = "ACTIVE" if active else "SUPERSEDED"
    badge_bg = "rgba(16, 185, 129, 0.2)" if active else "rgba(239, 68, 68, 0.2)"
    badge_color = "#34D399" if active else "#F87171"

    st.markdown(
        f"""
        <div style="
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <div>
                <div style="font-weight: 600; color: #F8FAFC;">{name}</div>
                <div style="font-size: 0.75rem; color: #64748B;">Category: {category}</div>
            </div>
            <span style="background: {badge_bg}; color: {badge_color}; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                {status_label}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
