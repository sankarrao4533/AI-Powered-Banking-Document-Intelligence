"""Sentinel: Enterprise Banking Document Intelligence & Regulatory GraphRAG Portal."""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import BANKING_CATEGORIES, settings
from src.copilot.agent import CopilotAgent
from src.copilot.prompt_enhancer import enhance_banking_query
from src.ingestion.curator import CuratorPipeline
from src.models.schemas import ActivePolicy, GraphAction
from src.storage.factory import get_storage

st.set_page_config(
    page_title="AI-Powered Banking Document Intelligence | Sentinel",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for executive banking theme (Turquoise #99E1D9 Accent & Glassmorphism)
st.markdown(
    """
    <style>
    /* ── Atmospheric Glassmorphic Background ─────────────────────────── */
    .stApp {
        background-color: #061619 !important;
        background-image: 
            radial-gradient(circle at 10% 8%, rgba(153, 225, 217, 0.14) 0%, transparent 42%),
            radial-gradient(circle at 90% 12%, rgba(20, 184, 166, 0.10) 0%, transparent 45%),
            radial-gradient(circle at 50% 45%, rgba(15, 60, 72, 0.22) 0%, transparent 58%),
            radial-gradient(circle at 85% 88%, rgba(153, 225, 217, 0.10) 0%, transparent 45%),
            radial-gradient(circle at 8% 92%, rgba(14, 116, 144, 0.14) 0%, transparent 50%) !important;
        background-attachment: fixed !important;
    }
    .main {
        background: transparent !important;
    }

    /* ── Frosted Glass Sidebar ────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: rgba(6, 22, 26, 0.72) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
        border-right: 1px solid rgba(153, 225, 217, 0.15) !important;
    }

    /* ── Frosted Glass KPI Cards ──────────────────────────────────────── */
    .kpi-card {
        background: rgba(14, 37, 42, 0.52) !important;
        backdrop-filter: blur(14px) saturate(160%) !important;
        -webkit-backdrop-filter: blur(14px) saturate(160%) !important;
        border: 1px solid rgba(153, 225, 217, 0.18) !important;
        border-radius: 14px;
        padding: 20px 16px;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.35), inset 0 1px 1px 0 rgba(255, 255, 255, 0.08);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        background: rgba(18, 48, 54, 0.68) !important;
        border-color: rgba(153, 225, 217, 0.45) !important;
        box-shadow: 0 14px 40px 0 rgba(0, 0, 0, 0.45), 0 0 22px rgba(153, 225, 217, 0.25);
    }
    .kpi-val { font-size: 30px; font-weight: 800; color: #99E1D9; margin: 4px 0; letter-spacing: -0.5px; }
    .kpi-label { font-size: 12px; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.8px; font-weight: 600; }
    .badge-active { background: rgba(6, 95, 70, 0.6); color: #34D399; padding: 3px 9px; border-radius: 6px; font-size: 11px; font-weight: 600; border: 1px solid rgba(52, 211, 153, 0.3); }
    .badge-superseded { background: rgba(51, 65, 85, 0.6); color: #94A3B8; padding: 3px 9px; border-radius: 6px; font-size: 11px; font-weight: 600; border: 1px solid rgba(148, 163, 184, 0.3); }

    /* ── Frosted Glass Citation Cards ─────────────────────────────────── */
    .citation-card {
        background: rgba(14, 37, 42, 0.55);
        backdrop-filter: blur(12px) saturate(160%);
        -webkit-backdrop-filter: blur(12px) saturate(160%);
        border-left: 4px solid #99E1D9;
        border-top: 1px solid rgba(153, 225, 217, 0.12);
        border-right: 1px solid rgba(153, 225, 217, 0.12);
        border-bottom: 1px solid rgba(153, 225, 217, 0.12);
        border-radius: 0 10px 10px 0;
        padding: 14px 18px;
        margin-top: 10px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25), inset 0 1px 1px rgba(255, 255, 255, 0.05);
    }
    div[data-testid="stMarkdownContainer"] {
        overflow: visible !important;
    }
    .query-boxes-container {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 12px;
        margin-top: 10px;
        margin-bottom: 24px;
        align-items: start;
        position: relative;
    }
    @media (max-width: 1250px) {
        .query-boxes-container {
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }
    }
    @media (max-width: 768px) {
        .query-boxes-container {
            grid-template-columns: 1fr;
        }
    }

    /* ── Frosted Glass Query Boxes ────────────────────────────────────── */
    .query-box {
        background: rgba(14, 37, 42, 0.52);
        backdrop-filter: blur(14px) saturate(160%);
        -webkit-backdrop-filter: blur(14px) saturate(160%);
        border: 1px solid rgba(153, 225, 217, 0.18);
        border-radius: 12px;
        padding: 12px 14px;
        cursor: pointer;
        position: relative;
        min-height: 75px;
        height: 75px;
        align-self: start;
        box-shadow: 0 8px 28px 0 rgba(0, 0, 0, 0.3), inset 0 1px 1px 0 rgba(255, 255, 255, 0.06);
        box-sizing: border-box;
        transition: all 0.2s ease;
    }
    .query-box:hover {
        background: rgba(7, 24, 27, 0.88);
        border-color: #99E1D9;
        box-shadow: 0 12px 36px -4px rgba(0, 0, 0, 0.6), 0 0 22px rgba(153, 225, 217, 0.35);
        z-index: 9999;
    }
    /* Invisible hover bridge to prevent dropdown from closing when moving mouse */
    .query-box::after {
        content: "";
        position: absolute;
        bottom: -8px;
        left: 0;
        right: 0;
        height: 8px;
        background: transparent;
    }
    .query-box-title {
        font-size: 13px;
        font-weight: 700;
        color: #F1F5F9;
        margin-bottom: 3px;
        display: flex;
        align-items: center;
        gap: 5px;
        line-height: 1.3;
    }
    .query-box:hover .query-box-title {
        color: #99E1D9;
    }
    .query-box-hint {
        font-size: 10.5px;
        color: #94A3B8;
        display: block;
        margin-top: 3px;
    }
    .query-box:hover .query-box-hint {
        display: none;
    }
    .query-box-list {
        display: none;
        position: absolute;
        top: calc(100% + 3px);
        left: 0;
        right: 0;
        min-width: 260px;
        background: rgba(7, 24, 27, 0.88);
        backdrop-filter: blur(18px) saturate(180%);
        -webkit-backdrop-filter: blur(18px) saturate(180%);
        border: 1px solid rgba(153, 225, 217, 0.35);
        border-radius: 12px;
        padding: 8px;
        box-shadow: 0 20px 45px rgba(0, 0, 0, 0.8), 0 0 20px rgba(153, 225, 217, 0.25);
        z-index: 9999;
        flex-direction: column;
        gap: 5px;
        box-sizing: border-box;
    }
    /* Invisible top bridge on list to keep hover active */
    .query-box-list::before {
        content: "";
        position: absolute;
        top: -6px;
        left: 0;
        right: 0;
        height: 6px;
        background: transparent;
    }
    .query-box:nth-child(4) .query-box-list,
    .query-box:nth-child(5) .query-box-list {
        left: auto;
        right: 0;
    }
    .query-box:hover .query-box-list {
        display: flex;
        animation: fadeInQuery 0.15s ease-out;
    }
    @keyframes fadeInQuery {
        from { opacity: 0; transform: translateY(-3px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .query-box-link {
        font-size: 11px;
        color: #E6FAF8;
        background: rgba(14, 37, 42, 0.65);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        padding: 8px 10px;
        border-radius: 8px;
        border: 1px solid rgba(153, 225, 217, 0.12);
        text-decoration: none !important;
        line-height: 1.35;
        transition: all 0.15s ease;
        display: block;
        box-sizing: border-box;
    }
    .query-box-link:hover {
        color: #99E1D9 !important;
        background: rgba(153, 225, 217, 0.14) !important;
        border-color: #99E1D9 !important;
        padding-left: 13px !important;
        box-shadow: 0 2px 10px rgba(153, 225, 217, 0.25);
    }
    
    /* ══════════════════════════════════════════════════════════════════
       NAVIGATION MENU & SELECTBOXES (Teal & Turquoise Glassmorphism)
       ══════════════════════════════════════════════════════════════════ */
    div[data-testid="stSelectbox"] > label,
    div[data-testid="stSelectbox"] p {
        color: #99E1D9 !important;
        font-weight: 700 !important;
        font-size: 12.5px !important;
        letter-spacing: 0.6px !important;
        text-transform: uppercase !important;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        background: transparent !important;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background: rgba(14, 37, 42, 0.72) !important;
        backdrop-filter: blur(14px) saturate(160%) !important;
        -webkit-backdrop-filter: blur(14px) saturate(160%) !important;
        border: 1px solid rgba(153, 225, 217, 0.28) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35), inset 0 1px 1px rgba(255, 255, 255, 0.08) !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {
        border-color: #99E1D9 !important;
        background: rgba(18, 48, 54, 0.85) !important;
        box-shadow: 0 0 18px rgba(153, 225, 217, 0.35) !important;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] * {
        color: #E6FAF8 !important;
        font-weight: 600 !important;
        font-size: 13.5px !important;
    }
    div[data-testid="stSelectbox"] svg {
        fill: #99E1D9 !important;
    }

    /* Dropdown Popover & Options (Completely replaces black popup) */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div {
        background: rgba(7, 24, 27, 0.96) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
        border: 1px solid rgba(153, 225, 217, 0.35) !important;
        border-radius: 14px !important;
        box-shadow: 0 20px 48px rgba(0, 0, 0, 0.85), 0 0 24px rgba(153, 225, 217, 0.25) !important;
        overflow: hidden !important;
        padding: 6px !important;
    }
    ul[role="listbox"] {
        background: transparent !important;
        padding: 4px !important;
    }
    li[role="option"] {
        background: rgba(14, 37, 42, 0.5) !important;
        color: #CBD5E1 !important;
        border: 1px solid transparent !important;
        border-radius: 8px !important;
        margin: 4px 0 !important;
        padding: 10px 14px !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
    }
    li[role="option"]:hover {
        background: rgba(153, 225, 217, 0.16) !important;
        border-color: rgba(153, 225, 217, 0.45) !important;
        color: #99E1D9 !important;
        font-weight: 700 !important;
        padding-left: 18px !important;
    }
    li[role="option"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(19, 78, 94, 0.85) 0%, rgba(15, 56, 66, 0.85) 100%) !important;
        border-color: #99E1D9 !important;
        color: #99E1D9 !important;
        font-weight: 700 !important;
    }

    /* ══════════════════════════════════════════════════════════════════
       CHAT INTERFACE & MESSAGES (Harmonized with Turquoise & Teal Glass)
       ══════════════════════════════════════════════════════════════════ */
    div[data-testid="stChatMessage"] {
        background: rgba(14, 37, 42, 0.55) !important;
        backdrop-filter: blur(14px) saturate(160%) !important;
        -webkit-backdrop-filter: blur(14px) saturate(160%) !important;
        border: 1px solid rgba(153, 225, 217, 0.18) !important;
        border-radius: 14px !important;
        padding: 16px 20px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35), inset 0 1px 1px rgba(255, 255, 255, 0.06) !important;
    }
    /* User chat bubble */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        background: linear-gradient(135deg, rgba(19, 64, 76, 0.6) 0%, rgba(14, 37, 42, 0.6) 100%) !important;
        border: 1px solid rgba(153, 225, 217, 0.3) !important;
        border-left: 5px solid #99E1D9 !important;
    }
    /* Assistant chat bubble */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {
        background: linear-gradient(135deg, rgba(14, 37, 42, 0.65) 0%, rgba(8, 24, 28, 0.65) 100%) !important;
        border: 1px solid rgba(153, 225, 217, 0.2) !important;
        border-left: 5px solid #14B8A6 !important;
    }
    /* Avatars */
    div[data-testid="stChatMessageAvatarUser"],
    div[data-testid="stChatMessageAvatarAssistant"] {
        background: rgba(19, 78, 94, 0.8) !important;
        border: 1.5px solid #99E1D9 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 14px rgba(153, 225, 217, 0.25) !important;
    }
    div[data-testid="stChatMessageContent"] {
        color: #E6FAF8 !important;
        font-size: 14.5px !important;
        line-height: 1.6 !important;
    }
    div[data-testid="stChatMessageContent"] p,
    div[data-testid="stChatMessageContent"] li,
    div[data-testid="stChatMessageContent"] strong {
        color: #E6FAF8 !important;
    }

    /* ── Bottom Floating Dock & Chat Input Bar ────────────────────────── */
    div[data-testid="stBottom"],
    div[data-testid="stBottom"] > div {
        background: transparent !important;
        background-image: none !important;
        border: none !important;
    }
    div[data-testid="stChatInput"] {
        background: rgba(14, 37, 42, 0.78) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
        border: 1px solid rgba(153, 225, 217, 0.35) !important;
        border-radius: 16px !important;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.08) !important;
        padding: 4px 6px !important;
        transition: all 0.25s ease !important;
    }
    div[data-testid="stChatInput"]:focus-within {
        border-color: #99E1D9 !important;
        background: rgba(18, 48, 54, 0.9) !important;
        box-shadow: 0 14px 44px rgba(0, 0, 0, 0.6), 0 0 24px rgba(153, 225, 217, 0.35) !important;
    }
    div[data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: #E6FAF8 !important;
        font-size: 14.5px !important;
        caret-color: #99E1D9 !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #94A3B8 !important;
        font-size: 13.5px !important;
    }
    div[data-testid="stChatInput"] button {
        background: #99E1D9 !important;
        color: #07181B !important;
        border: none !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 10px rgba(153, 225, 217, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stChatInput"] button:hover {
        background: #B8F2EC !important;
        transform: scale(1.05);
        box-shadow: 0 4px 16px rgba(153, 225, 217, 0.5) !important;
    }
    div[data-testid="stChatInput"] button svg {
        fill: #07181B !important;
    }

    /* ══════════════════════════════════════════════════════════════════
       DATA CONTAINERS & FORM WIDGETS
       ══════════════════════════════════════════════════════════════════ */
    div[data-testid="stDataFrame"] {
        background: rgba(14, 37, 42, 0.45) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(153, 225, 217, 0.16) !important;
        border-radius: 12px !important;
        padding: 8px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
    }
    div[data-testid="stExpander"] {
        background: rgba(14, 37, 42, 0.42) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(153, 225, 217, 0.15) !important;
        border-radius: 12px !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.22) !important;
    }
    .stButton > button[kind="primary"] {
        background-color: #99E1D9 !important;
        color: #07181B !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 16px rgba(153, 225, 217, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #B8F2EC !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 22px rgba(153, 225, 217, 0.45) !important;
    }
    .stDownloadButton > button {
        background: rgba(14, 37, 42, 0.5) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(153, 225, 217, 0.22) !important;
        color: #E6FAF8 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    .stDownloadButton > button:hover {
        border-color: #99E1D9 !important;
        color: #99E1D9 !important;
        box-shadow: 0 0 12px rgba(153, 225, 217, 0.3) !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    div[data-testid="stMetric"] {
        background: rgba(14, 37, 42, 0.45) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(153, 225, 217, 0.12) !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        margin-bottom: 8px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2) !important;
    }
    div[data-testid="stMetricValue"] {
        color: #99E1D9 !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
    }

    /* Universal Text Input and Area Styling (No harsh black inputs) */
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div,
    div[data-baseweb="textarea"] textarea {
        background: rgba(14, 37, 42, 0.6) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(153, 225, 217, 0.22) !important;
        border-radius: 10px !important;
        color: #E6FAF8 !important;
    }
    div[data-baseweb="input"] input {
        color: #E6FAF8 !important;
    }
    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="textarea"] > div:focus-within {
        border-color: #99E1D9 !important;
        box-shadow: 0 0 14px rgba(153, 225, 217, 0.3) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def load_system():
    from src.config import load_environment
    load_environment()
    storage = get_storage()
    # Auto-seed baseline corpus if database is fresh/empty on cloud deploy
    try:
        if not storage.get_all_policies():
            from seed_database import seed_baseline_corpus
            seed_baseline_corpus()
    except Exception as e:
        print(f"[AutoSeed] Warning: {e}")
    agent = CopilotAgent(storage)
    curator = CuratorPipeline(storage)
    return storage, agent, curator


storage, agent, curator = load_system()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    backend_name = "Enterprise Neo4j" if "Neo4j" in type(storage).__name__ else "Embedded SQLite + NetworkX"
    
    st.markdown(
        f"""
        <div style="padding: 4px 0 10px 0;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="background: linear-gradient(135deg, rgba(19, 78, 94, 0.85) 0%, rgba(15, 56, 66, 0.85) 100%); backdrop-filter: blur(10px); border: 1px solid #99E1D9; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px; box-shadow: 0 4px 16px rgba(153, 225, 217, 0.25); flex-shrink: 0;">
                    🏦
                </div>
                <div>
                    <div style="font-size: 15px; font-weight: 800; color: #F8FAFC; letter-spacing: -0.3px; line-height: 1.2;">
                        AI-Powered <span style="color: #99E1D9;">Banking Intelligence</span>
                    </div>
                    <div style="font-size: 10.5px; font-weight: 600; color: #94A3B8; letter-spacing: 0.2px; margin-top: 2px;">
                        Sentinel Tier-1 GraphRAG Governance
                    </div>
                </div>
            </div>
            <div style="background: rgba(14, 37, 42, 0.55); backdrop-filter: blur(10px); border: 1px solid rgba(153, 225, 217, 0.16); border-radius: 10px; padding: 7px 12px; display: flex; align-items: center; justify-content: space-between; margin-top: 14px; margin-bottom: 8px; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);">
                <span style="font-size: 10.5px; color: #94A3B8; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px;">Engine</span>
                <span style="font-size: 11px; color: #99E1D9; font-weight: 600; display: flex; align-items: center; gap: 5px;">
                    <span style="display: inline-block; width: 6px; height: 6px; background: #99E1D9; border-radius: 50%; box-shadow: 0 0 6px #99E1D9;"></span>
                    {backend_name}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.selectbox(
        "Navigation",
        [
            "💬 Compliance Assistant",
            "📊 Executive Dashboard",
            "🕸️ Regulatory Knowledge Graph",
            "📥 Document Ingestion Studio",
            "🛡️ Supersession & Audit Trail",
        ],
        index=0,
    )

    st.divider()
    st.subheader("Runtime Controls")
    enhance_toggle = st.toggle("Edge Query Enhancer", value=True, help="Expands banking acronyms (PAN, NRI, TDS, LC, etc.)")
    top_k_val = st.slider("Retrieval Depth (Top-K)", min_value=1, max_value=8, value=settings.TOP_K)
    min_conf_val = st.slider("Min Confidence %", min_value=0.0, max_value=50.0, value=settings.MIN_CONFIDENCE_THRESHOLD, step=5.0)

    st.divider()
    all_policies = storage.get_all_policies()
    active_cnt = sum(1 for p in all_policies if p.active)
    st.metric("Total Indexed Policies", len(all_policies))
    st.metric("Active Governed Rules", active_cnt)
    st.metric("Superseded (Blocked)", len(all_policies) - active_cnt)


# ── TAB 1: Compliance Assistant ───────────────────────────────────────────────
if page == "💬 Compliance Assistant":
    st.title("AI-Powered Banking Document Intelligence")
    st.subheader("💬 Banking Compliance Assistant")
    st.caption("Ask questions about active bank policies, KYC/AML limits, lounge access, loan limits, and TDS slabs.")

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    session_messages = storage.get_session_messages(st.session_state.session_id)

    col_s1, col_s2, col_s3 = st.columns([3, 1.2, 1])
    with col_s3:
        if st.button("➕ New Session", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()

    with col_s2:
        if session_messages:
            transcript_lines = [
                "# SENTINEL BANKING ASSISTANT - COMPLIANCE AUDIT TRANSCRIPT",
                f"**Session ID:** `{st.session_state.session_id}`",
                f"**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
                f"**Total Exchanges:** {len(session_messages) // 2}",
                "\n---\n",
            ]
            for m in session_messages:
                if m.role == "user":
                    transcript_lines.append(f"\n### 👤 User Inquiry:\n> {m.content}\n")
                elif m.role == "assistant":
                    transcript_lines.append(f"### 🤖 Verified Assistant Response:\n{m.content}\n")
                    if m.citations:
                        transcript_lines.append("#### 📚 Verified Evidence Sources:")
                        for c in m.citations:
                            transcript_lines.append(f"- **{c.document_name}** ({c.category}) | Confidence: `{c.match_confidence}%`")
                            transcript_lines.append(f"  - *Active Rule:* {c.extracted_rule}")
                            if c.customer_types:
                                transcript_lines.append(f"  - *Applies to:* {', '.join(c.customer_types)}")
                            if c.required_docs:
                                transcript_lines.append(f"  - *Mandatory Docs:* {', '.join(c.required_docs)}")
                        transcript_lines.append("")
            transcript_text = "\n".join(transcript_lines)
            st.download_button(
                label="📥 Export Audit (MD)",
                data=transcript_text.encode("utf-8"),
                file_name=f"compliance_audit_{st.session_state.session_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
                use_container_width=True,
                help="Download formal compliance record of this conversation including all citations and confidence scores."
            )

    # 5 Interactive Hover Boxes (Highlight and Reveal 4 Questions on Cursor Hover)
    st.write("**Suggested Regulatory Queries:**")

    # Check if a query link was clicked via URL query param
    selected_query = None
    if "q" in st.query_params and st.query_params["q"]:
        selected_query = st.query_params["q"]
        st.query_params.clear()

    category_boxes = [
        {
            "title": "💳 Credit Cards & Lounge",
            "questions": [
                "What are the 2026 lounge access rules for Signature and Infinite cards?",
                "What is the minimum quarterly spend required for Infinite Card lounge visits in 2026?",
                "How many lounge access visits are permitted per quarter on Signature cards?",
                "Is there any lounge access allowed without meeting the minimum spend requirement in 2026?",
            ]
        },
        {
            "title": "🛂 KYC & AML Cash Limits",
            "questions": [
                "What is the PAN card threshold for cash deposits?",
                "When is Form 60 accepted in lieu of a PAN card for banking transactions?",
                "What documents are required for NRI account onboarding?",
                "What proof of foreign address is acceptable for NRI onboarding?",
            ]
        },
        {
            "title": "🏠 Retail Loans & Fixed Deposits",
            "questions": [
                "What is the base interest rate and tenure for NRI Home Loans?",
                "What is the minimum overseas residence requirement for an NRI home loan applicant?",
                "What are the 2026 Fixed Deposit interest rates for senior citizens?",
                "What is the premature withdrawal penalty for retail term deposits?",
            ]
        },
        {
            "title": "🏢 Corporate Banking & Trade Finance",
            "questions": [
                "What is the maximum unsecured LC limit for MSMEs?",
                "What collateral is required for Letters of Credit exceeding ₹50 Lakhs?",
                "What documents are mandatory for an NRI Commercial Property Loan?",
                "Is a registered Trade License mandatory for MSME business loan disbursement?",
            ]
        },
        {
            "title": "📑 Tax Compliance & TDS",
            "questions": [
                "What are the TDS tax deduction slabs on fixed deposit interest for 2026?",
                "What is the interest income threshold for TDS deduction on senior citizen deposits?",
                "What happens to the TDS rate if a PAN card is not provided by the depositor?",
                "Can depositors submit Form 15G or 15H to avoid TDS deductions on term deposits?",
            ]
        },
    ]

    boxes_html = ['<div class="query-boxes-container">']
    for b in category_boxes:
        links_html = "".join(
            f'<a href="?q={urllib.parse.quote_plus(q)}" target="_self" class="query-box-link">👉 {q}</a>'
            for q in b["questions"]
        )
        box_item = (
            f'<div class="query-box">'
            f'<div class="query-box-title">{b["title"]}</div>'
            f'<span class="query-box-hint">✨ Move cursor here to view 4 queries</span>'
            f'<div class="query-box-list">{links_html}</div>'
            f'</div>'
        )
        boxes_html.append(box_item)
    boxes_html.append('</div>')
    st.markdown("".join(boxes_html), unsafe_allow_html=True)

    # Load session history
    messages = storage.get_session_messages(st.session_state.session_id)
    if not messages:
        st.markdown(
            """
            <div style="background: rgba(14, 37, 42, 0.48); backdrop-filter: blur(16px) saturate(160%); -webkit-backdrop-filter: blur(16px) saturate(160%); border: 1px dashed rgba(153, 225, 217, 0.28); border-radius: 14px; padding: 24px 20px; text-align: center; margin: 15px 0 25px 0; box-shadow: 0 12px 36px rgba(0, 0, 0, 0.3), inset 0 1px 1px rgba(255, 255, 255, 0.06);">
                <div style="font-size: 28px; margin-bottom: 6px;">🛡️</div>
                <h4 style="color: #99E1D9; margin: 0 0 6px 0; font-weight: 700;">Welcome to AI-Powered Banking Document Intelligence</h4>
                <p style="color: #94A3B8; font-size: 13px; max-width: 620px; margin: 0 auto 12px auto; line-height: 1.5;">
                    Ask questions on active bank circulars, interest rates, KYC thresholds, and loan limits. Every response is verified through our <strong>SUPERSEDES Firewall</strong> to eliminate outdated policies and prevent hallucinations.
                </p>
                <div style="display: flex; justify-content: center; gap: 20px; font-size: 11.5px; color: #CBD5E1;">
                    <span>🔒 <strong>Active Policies Only</strong></span>
                    <span>🕸️ <strong>Multi-Hop Graph Context</strong></span>
                    <span>📚 <strong>Auditable Evidence Citations</strong></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    for msg in messages:
        with st.chat_message(msg.role):
            st.markdown(msg.content)
            if msg.citations:
                with st.expander(f"📚 Verified Evidence Sources ({len(msg.citations)} active policies)"):
                    for cit in msg.citations:
                        cust_str = ", ".join(cit.customer_types) if cit.customer_types else "All Customers"
                        doc_str = ", ".join(cit.required_docs) if cit.required_docs else "Standard"
                        st.markdown(
                            f"""
                            **{cit.document_name}** | *{cit.category}* (Confidence: `{cit.match_confidence}%`)  
                            - **Active Rule:** {cit.extracted_rule}  
                            - **Customer Segment:** `{cust_str}`  
                            - **Required KYC/Collateral:** `{doc_str}`  
                            ---
                            """
                        )

    # Process prompt
    user_input = st.chat_input("Ask about Sentinel Banking policies...") or selected_query
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Executing Hybrid GraphRAG retrieval with Supersession Firewall..."):
                response = agent.answer_question(
                    user_question=user_input,
                    session_id=st.session_state.session_id,
                    enhance_query=enhance_toggle,
                )

            st.markdown(response.response)

            if response.citations:
                with st.expander(f"📚 Verified Evidence Sources ({len(response.citations)} active policies)", expanded=True):
                    for cit in response.citations:
                        cust_str = ", ".join(cit.customer_types) if cit.customer_types else "All Customers"
                        doc_str = ", ".join(cit.required_docs) if cit.required_docs else "Standard"
                        st.markdown(
                            f"""
                            <div class="citation-card">
                                <strong>{cit.document_name}</strong> &nbsp;
                                <span class="badge-active">ACTIVE GOVERNED</span> &nbsp;
                                <code>Confidence: {cit.match_confidence}%</code><br/>
                                <small><strong>Category:</strong> {cit.category}</small><br/>
                                <p style="margin: 6px 0;"><strong>Active Rule:</strong> {cit.extracted_rule}</p>
                                <small><strong>Applies To:</strong> {cust_str} | <strong>Mandatory Docs:</strong> {doc_str}</small>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )


# ── TAB 2: Executive Dashboard ────────────────────────────────────────────────
elif page == "📊 Executive Dashboard":
    st.title("AI-Powered Banking Document Intelligence")
    st.subheader("📊 Executive Governance Dashboard")
    st.caption("Live monitoring of regulatory policies, active/superseded ratios, and ontology coverage.")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    total_p = len(all_policies)
    active_p = sum(1 for p in all_policies if p.active)
    superseded_p = total_p - active_p

    kpi1.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Documents</div><div class="kpi-val">{total_p}</div></div>', unsafe_allow_html=True)
    kpi2.markdown(f'<div class="kpi-card"><div class="kpi-label">Active Policies</div><div class="kpi-val" style="color: #34D399;">{active_p}</div></div>', unsafe_allow_html=True)
    kpi3.markdown(f'<div class="kpi-card"><div class="kpi-label">Superseded / Retired</div><div class="kpi-val" style="color: #94A3B8;">{superseded_p}</div></div>', unsafe_allow_html=True)
    kpi4.markdown(f'<div class="kpi-card"><div class="kpi-label">Ontology Categories</div><div class="kpi-val">{len(BANKING_CATEGORIES)}</div></div>', unsafe_allow_html=True)

    st.subheader("Policy Distribution by Banking Category")
    cat_counts = {c: 0 for c in BANKING_CATEGORIES}
    for p in all_policies:
        if p.category in cat_counts:
            cat_counts[p.category] += 1
    st.bar_chart(cat_counts)

    st.subheader("Active Governed Policies Catalog")
    table_data = []
    for p in all_policies:
        table_data.append(
            {
                "Status": "🟢 ACTIVE" if p.active else "⚪ SUPERSEDED",
                "Policy Document": p.name,
                "Category": p.category,
                "Customer Segments": ", ".join(p.applies_to_customer) or "General Banking",
                "Mandatory KYC / Collateral": ", ".join(p.requires_document) or "Standard Verification",
                "Superseded By": p.superseded_by or "—",
            }
        )
    df_catalog = pd.DataFrame(table_data)

    def style_status_badge(val):
        if "ACTIVE" in val:
            return "background-color: rgba(6, 95, 70, 0.45); color: #34D399; font-weight: 700; border-radius: 4px;"
        elif "SUPERSEDED" in val:
            return "background-color: rgba(51, 65, 85, 0.45); color: #94A3B8; font-weight: 700; border-radius: 4px;"
        return ""

    styled_catalog = df_catalog.style.map(style_status_badge, subset=["Status"])
    st.dataframe(styled_catalog, use_container_width=True, hide_index=True)


# ── TAB 3: Regulatory Knowledge Graph ─────────────────────────────────────────
elif page == "🕸️ Regulatory Knowledge Graph":
    st.title("AI-Powered Banking Document Intelligence")
    st.subheader("🕸️ Regulatory Multi-Hop Knowledge Graph")
    st.caption("Interactive visual topology connecting Categories, Active Policies, Supersessions, Customer Segments, and Requirements.")

    graph_data = storage.get_graph_data()
    nodes = graph_data["nodes"]
    links = graph_data["links"]

    st.write(f"**Graph Statistics:** `{len(nodes)}` Entities, `{len(links)}` Relational Edges.")

    # Render interactive vis.js HTML graph
    vis_nodes = json.dumps([{"id": n["id"], "label": n["label"], "color": n["color"], "shape": "dot", "size": 18 if n["type"] == "Category" else 12} for n in nodes])
    vis_edges = json.dumps([{"from": l["source"], "to": l["target"], "label": l["relation"], "arrows": "to", "font": {"size": 10, "color": "#94A3B8"}} for l in links])

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
      <style>
        #network {{
          width: 100%;
          height: 600px;
          background: rgba(7, 24, 27, 0.75);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          border: 1px solid rgba(153, 225, 217, 0.2);
          border-radius: 14px;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35), inset 0 1px 1px rgba(255, 255, 255, 0.05);
        }}
      </style>
    </head>
    <body>
      <div id="network"></div>
      <script>
        var nodes = new vis.DataSet({vis_nodes});
        var edges = new vis.DataSet({vis_edges});
        var container = document.getElementById('network');
        var data = {{ nodes: nodes, edges: edges }};
        var options = {{
          physics: {{ stabilization: true, barnesHut: {{ springLength: 120 }} }},
          nodes: {{ font: {{ color: '#FFFFFF', size: 12 }} }},
          edges: {{ color: {{ color: '#244B53', highlight: '#99E1D9' }} }}
        }};
        var network = new vis.Network(container, data, options);
      </script>
    </body>
    </html>
    """
    st.components.v1.html(html_code, height=620)

    st.markdown(
        """
        **Legend:**
        - 🔵 **Blue:** Category
        - 🟢 **Green:** Active Governed Policy
        - ⚪ **Muted Slate:** Superseded / Archived Policy (Blocked by Firewall)
        - 🟡 **Yellow:** Customer Type (APPLIES_TO)
        - 🟣 **Purple:** Required Document (REQUIRES)
        """
    )


# ── TAB 4: Document Ingestion Studio ──────────────────────────────────────────
elif page == "📥 Document Ingestion Studio":
    st.title("AI-Powered Banking Document Intelligence")
    st.subheader("📥 Universal Document Ingestion Studio")
    st.caption("Upload new banking policies, circulars, or table rate cards (PDF/PNG) to dynamically update the Knowledge Graph.")

    uploaded = st.file_uploader("Upload Policy Document (PDF or PNG)", type=["pdf", "png", "jpg", "jpeg"])
    if uploaded:
        temp_dir = settings.DATA_DIR / "uploads"
        temp_dir.mkdir(parents=True, exist_ok=True)
        file_path = temp_dir / uploaded.name
        with open(file_path, "wb") as f:
            f.write(uploaded.getbuffer())

        st.success(f"File uploaded: `{uploaded.name}`")

        # Automatic Content & Structure Extraction for Smart Pre-Population
        extracted_text = ""
        if uploaded.name.lower().endswith(".pdf"):
            from src.ingestion.pdf_parser import extract_pdf_content
            pdf_data = extract_pdf_content(file_path)
            extracted_text = pdf_data["text"]
        else:
            extracted_text = f"Regulatory Table: {uploaded.name}. Visual rate card matrix."

        from src.ingestion.multimodal_extractor import extract_offline_heuristic
        auto_action = extract_offline_heuristic(uploaded.name, extracted_text)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Document Preview")
            if uploaded.name.lower().endswith(".pdf"):
                st.text_area("Extracted Text Content", extracted_text, height=340)
            else:
                st.image(str(file_path), caption=uploaded.name, use_container_width=True)

        with col2:
            st.subheader("Curator Extraction & Ingestion")

            # Smart Pre-Selected Category
            def_cat_idx = BANKING_CATEGORIES.index(auto_action.target_node) if auto_action.target_node in BANKING_CATEGORIES else 0
            cat_choice = st.selectbox("Assign Ontology Category", BANKING_CATEGORIES, index=def_cat_idx)

            # Smart Pre-Selected Action Type
            action_options = ["CREATE_NEW", "SUPERSEDE_OLD"]
            def_action_idx = 1 if auto_action.action_type == "SUPERSEDE_OLD" else 0
            action_choice = st.selectbox("Action Type", action_options, index=def_action_idx)

            # Active Policy Dropdown for Supersession (Avoids manual typing/typos)
            supersedes_final = None
            if action_choice == "SUPERSEDE_OLD":
                existing_doc_names = [p.name for p in all_policies if p.name != uploaded.name]
                
                # Check if heuristic detected a superseded document
                if auto_action.superseded_document and auto_action.superseded_document in existing_doc_names:
                    dropdown_options = existing_doc_names + ["Custom / Enter Other Filename..."]
                    pre_selected_idx = dropdown_options.index(auto_action.superseded_document)
                else:
                    dropdown_options = ["-- Select Existing Policy to Supersede --"] + existing_doc_names + ["Custom / Enter Other Filename..."]
                    pre_selected_idx = 0

                selected_supersede_option = st.selectbox(
                    "Select Policy to Supersede (Retire from retrieval)",
                    dropdown_options,
                    index=pre_selected_idx,
                    help="The selected policy will be marked as inactive and blocked by the Supersession Firewall."
                )

                if selected_supersede_option == "Custom / Enter Other Filename...":
                    supersedes_final = st.text_input("Enter Superseded Filename manually", auto_action.superseded_document or "")
                elif selected_supersede_option != "-- Select Existing Policy to Supersede --":
                    supersedes_final = selected_supersede_option
                else:
                    supersedes_final = None

            rule_input = st.text_area("Regulatory Rule Summary", auto_action.extracted_rule, height=100)
            default_customers = ", ".join(auto_action.applies_to_customer) if auto_action.applies_to_customer else "Domestic Retail, NRI"
            customers_input = st.text_input("Target Customer Segments (comma-separated)", default_customers)
            default_reqs = ", ".join(auto_action.requires_document) if auto_action.requires_document else "PAN Card, Passport"
            reqs_input = st.text_input("Required Documents (comma-separated)", default_reqs)

            if st.button("🚀 Ingest into Knowledge Graph", type="primary", use_container_width=True):
                with st.spinner("Indexing into knowledge graph and vector store..."):
                    cust_list = [c.strip() for c in customers_input.split(",") if c.strip()]
                    req_list = [r.strip() for r in reqs_input.split(",") if r.strip()]
                    action = GraphAction(
                        target_node=cat_choice,  # type: ignore
                        action_type=action_choice,  # type: ignore
                        extracted_rule=rule_input,
                        superseded_document=supersedes_final.strip() if supersedes_final else None,
                        applies_to_customer=cust_list,
                        requires_document=req_list,
                    )
                    res = curator.ingest_file(file_path, override_action=action)
                    st.success(f"Successfully indexed '{res.document_name}' into {res.category}!")
                    if action.action_type == "SUPERSEDE_OLD" and supersedes_final:
                        st.info(f"🛡️ Supersession Firewall Active: '{supersedes_final}' is now permanently quarantined.")
                    st.balloons()


# ── TAB 5: Supersession & Audit Trail ─────────────────────────────────────────
elif page == "🛡️ Supersession & Audit Trail":
    st.title("AI-Powered Banking Document Intelligence")
    st.subheader("🛡️ Regulatory Supersession & Governance Audit Trail")
    st.caption("Audit verification ensuring that legacy, outdated policies are quarantined by the Supersession Firewall.")

    st.subheader("Supersession Lineage Matrix")
    superseded_policies = [p for p in all_policies if not p.active or p.superseded_by]
    if superseded_policies:
        sup_data = []
        for p in superseded_policies:
            sup_data.append(
                {
                    "Outdated / Retired Policy": p.name,
                    "Superseded By (Active Successor)": p.superseded_by or "—",
                    "Category": p.category,
                    "Status": "QUARANTINED (INACTIVE)",
                    "Retirement Date": p.retired_at or "Historical",
                }
            )
        st.dataframe(sup_data, use_container_width=True)

        # 📥 Export Audit Report Button (CSV)
        import pandas as pd
        df_audit = pd.DataFrame(sup_data)
        csv_bytes = df_audit.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Audit Trail (CSV)",
            data=csv_bytes,
            file_name=f"sentinel_audit_lineage_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            help="Download complete audit trail matrix for compliance reporting."
        )

        st.divider()

        # 🔍 Side-by-Side Policy Comparator Tool
        st.subheader("🔍 Side-by-Side Policy Comparator")
        st.caption("Compare an outdated policy against its active successor to inspect regulatory rule changes.")
        
        sup_names = [p.name for p in superseded_policies]
        selected_sup_name = st.selectbox("Select a Quarantined Policy to inspect", sup_names)
        old_policy = next((p for p in all_policies if p.name == selected_sup_name), None)
        new_policy = next((p for p in all_policies if p.name == old_policy.superseded_by), None) if old_policy and old_policy.superseded_by else None

        col_old, col_new = st.columns(2)
        with col_old:
            st.markdown(
                f"""
                <div style="background: rgba(30, 41, 59, 0.45); backdrop-filter: blur(14px) saturate(160%); -webkit-backdrop-filter: blur(14px) saturate(160%); border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 12px; padding: 18px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35), inset 0 1px 1px rgba(255, 255, 255, 0.05);">
                    <span class="badge-superseded">QUARANTINED / RETIRED</span>
                    <h4 style="color: #CBD5E1; margin-top: 8px;">{old_policy.name if old_policy else 'N/A'}</h4>
                    <p><strong>Category:</strong> {old_policy.category if old_policy else 'N/A'}</p>
                    <p><strong>Retired Date:</strong> {old_policy.retired_at if old_policy and old_policy.retired_at else 'Historical Archive'}</p>
                    <hr style="border-color: rgba(153, 225, 217, 0.12);"/>
                    <p><strong>Historical Rule:</strong><br/>{old_policy.extracted_rule if old_policy else 'No rule extracted'}</p>
                    <small style="color: #94A3B8;">Source excerpt: {old_policy.source_text[:200] + '...' if old_policy else ''}</small>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_new:
            st.markdown(
                f"""
                <div style="background: rgba(10, 38, 30, 0.45); backdrop-filter: blur(14px) saturate(160%); -webkit-backdrop-filter: blur(14px) saturate(160%); border: 1px solid rgba(52, 211, 153, 0.35); border-radius: 12px; padding: 18px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35), inset 0 1px 1px rgba(255, 255, 255, 0.05);">
                    <span class="badge-active">ACTIVE GOVERNED SUCCESSOR</span>
                    <h4 style="color: #34D399; margin-top: 8px;">{new_policy.name if new_policy else 'No Direct Successor Linked'}</h4>
                    <p><strong>Category:</strong> {new_policy.category if new_policy else 'N/A'}</p>
                    <p><strong>Status:</strong> Enforceable Active Directive</p>
                    <hr style="border-color: rgba(153, 225, 217, 0.12);"/>
                    <p><strong>Governing Active Rule:</strong><br/>{new_policy.extracted_rule if new_policy else 'Policy superseded without a single successor'}</p>
                    <small style="color: #94A3B8;">Source excerpt: {new_policy.source_text[:200] + '...' if new_policy else ''}</small>
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:
        st.info("No superseded policies found.")

    st.divider()
    st.subheader("Supersession Firewall Verification Test")
    st.write(
        """
        The **Supersession Firewall** enforces a graph guardrail pattern:
        - In Cypher: `WHERE NOT ()-[:SUPERSEDES]->(p) AND p.active = true`
        - In NetworkX: `not has_predecessor_with_edge('SUPERSEDES')`
        
        This prevents older guidelines (e.g. 2024/2025 Lounge Access) from corrupting the Assistant context.
        """
    )
