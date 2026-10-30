"""Streamlit Multipage: Session & Regulatory Audit History."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.core.pipeline import BankingIntelligencePipeline
from components.cards import render_kpi_card

st.set_page_config(
    page_title="Audit History | Sentinel Banking Intelligence",
    page_icon="📜",
    layout="wide",
)

# Custom Styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #061619 !important;
        background-image: 
            radial-gradient(circle at 10% 8%, rgba(153, 225, 217, 0.12) 0%, transparent 40%),
            radial-gradient(circle at 90% 12%, rgba(20, 184, 166, 0.08) 0%, transparent 45%),
            radial-gradient(circle at 50% 50%, rgba(15, 60, 72, 0.18) 0%, transparent 55%) !important;
        background-attachment: fixed !important;
    }
    .history-card {
        background: rgba(14, 37, 42, 0.55);
        border: 1px solid rgba(153, 225, 217, 0.18);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

pipeline = BankingIntelligencePipeline()

st.title("📜 Regulatory Audit & Conversation History")
st.markdown("Inspect historical banking compliance queries, verified citations, and audit logs.")

# Fetch messages from SQLite backend
storage = pipeline.storage
try:
    messages = storage.get_all_chat_history(limit=100) if hasattr(storage, "get_all_chat_history") else []
except Exception:
    messages = []

# Fallback: query database directly if method doesn't exist
if not messages:
    try:
        import sqlite3
        from src.config import SQLITE_DB_PATH
        if SQLITE_DB_PATH.exists():
            with sqlite3.connect(SQLITE_DB_PATH) as conn:
                cursor = conn.cursor()
                rows = cursor.execute(
                    "SELECT session_id, role, content, citations, timestamp FROM chat_history ORDER BY id DESC LIMIT 100"
                ).fetchall()
                for r in rows:
                    cits = json.loads(r[3]) if r[3] else []
                    messages.append({
                        "session_id": r[0],
                        "role": r[1],
                        "content": r[2],
                        "citations": cits,
                        "timestamp": r[4],
                    })
    except Exception as e:
        st.warning(f"Could not load historical logs: {e}")

col1, col2, col3 = st.columns(3)
with col1:
    render_kpi_card("Total Audit Logs", len(messages), "Recorded Sessions", "📋")
with col2:
    user_queries = [m for m in messages if m.get("role") == "user"]
    render_kpi_card("User Inquiries", len(user_queries), "Compliance Checks", "🔍")
with col3:
    cits_count = sum(len(m.get("citations", [])) for m in messages if m.get("role") == "assistant")
    render_kpi_card("Active Citations", cits_count, "Governed Sources", "🛡️")

st.markdown("---")

search_term = st.text_input("🔎 Search audit history by keyword or session ID:", "")

filtered = messages
if search_term:
    term = search_term.lower()
    filtered = [
        m for m in messages
        if term in str(m.get("content", "")).lower() or term in str(m.get("session_id", "")).lower()
    ]

if not filtered:
    st.info("No recorded interactions found matching criteria.")
else:
    st.write(f"Displaying **{len(filtered)}** log entries:")
    for item in filtered:
        role = item.get("role", "user")
        content = item.get("content", "")
        ts = item.get("timestamp", "")
        sid = item.get("session_id", "")
        cits = item.get("citations", [])

        is_user = role == "user"
        badge = "👤 User Query" if is_user else "🤖 Copilot Response"
        badge_color = "#38BDF8" if is_user else "#34D399"

        st.markdown(
            f"""
            <div class="history-card">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-weight: 600; color: {badge_color};">{badge}</span>
                    <span style="font-size: 0.8rem; color: #94A3B8;">Session: {sid[:8]}... | {ts}</span>
                </div>
                <div style="color: #F1F5F9; font-size: 0.95rem;">{content}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if cits:
            with st.expander(f"📌 View {len(cits)} Governing Citations"):
                for idx, c in enumerate(cits, 1):
                    doc = c.get("document_name") if isinstance(c, dict) else getattr(c, "document_name", "Policy")
                    rule = c.get("extracted_rule") if isinstance(c, dict) else getattr(c, "extracted_rule", "")
                    st.markdown(f"- **[{idx}] {doc}**: {rule}")

    # Export button
    df_export = pd.DataFrame(filtered)
    if not df_export.empty:
        csv_data = df_export.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Audit Trail (CSV)",
            data=csv_data,
            file_name="sentinel_audit_trail.csv",
            mime="text/csv",
        )
