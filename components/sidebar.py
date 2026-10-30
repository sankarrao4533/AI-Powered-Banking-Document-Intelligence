"""Sidebar and status panel components for Streamlit frontend."""

from __future__ import annotations

from typing import Any, Dict
import streamlit as st


def render_system_status(status_info: Dict[str, Any]) -> None:
    """Render the sidebar telemetry widget."""
    backend_name = status_info.get("storage_backend", "EmbeddedStorageBackend")
    total_docs = status_info.get("total_policies", 12)
    active_docs = status_info.get("active_policies", 10)
    superseded = status_info.get("superseded_policies", 2)

    st.sidebar.markdown("### 🏛️ System Governance")
    st.sidebar.markdown(
        f"""
        <div style="
            background: rgba(14, 37, 42, 0.6);
            border: 1px solid rgba(153, 225, 217, 0.2);
            border-radius: 10px;
            padding: 12px;
            font-size: 0.85rem;
            margin-bottom: 16px;
        ">
            <div style="color: #5EEAD4; font-weight: 600; margin-bottom: 6px;">
                Engine: <span style="color: #F8FAFC;">{backend_name}</span>
            </div>
            <div style="color: #94A3B8;">Total Ingested: <span style="color: #F8FAFC;">{total_docs}</span></div>
            <div style="color: #34D399;">Active Policies: <span style="color: #F8FAFC;">{active_docs}</span></div>
            <div style="color: #F87171;">Quarantined/Superseded: <span style="color: #F8FAFC;">{superseded}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
