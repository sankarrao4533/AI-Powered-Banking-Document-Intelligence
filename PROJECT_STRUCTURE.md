# Project File Structure: AI-Powered Banking Document Intelligence (Sentinel AI)

This document details the standardized file and directory structure of the **AI-Powered Banking Document Intelligence** project in full accordance with the **GMRIT Student Project Handbook — Grand AI & NLP Projects** reference standard.

---

## 📁 Standardized Directory Layout

```text
AI-Powered Banking Document Intelligence/
├── app.py                       # Streamlit entry point (frontend): the Main file on deploy
├── pages/                       # Optional extra pages (Streamlit multipage convention)
│   └── 1_History.py             # Session and regulatory audit trail view
├── components/                  # Optional reusable UI pieces (cards, forms, charts)
│   ├── __init__.py
│   ├── cards.py                 # KPI cards, citation cards, and policy badges
│   ├── chat.py                  # Styled chat message bubbles and governance badges
│   └── sidebar.py               # Telemetry and system engine widgets
├── backend/                     # Project logic: imported by the frontend, no UI code
│   ├── __init__.py
│   ├── config.py                # Reads st.secrets / environment variables with fallback
│   ├── services/
│   │   ├── __init__.py
│   │   └── llm_service.py       # LLM provider calls (Groq, Gemini, offline fallback), timeouts
│   ├── core/
│   │   ├── __init__.py
│   │   └── pipeline.py          # Project-specific logic (GraphRAG, supersession, scoring)
│   └── utils/
│       ├── __init__.py
│       └── validators.py        # Input query sanitization and document file validation
├── data/
│   ├── baseline_docs/           # 12 Regulated banking PDFs and PNG rate cards
│   ├── sample/                  # Small public/synthetic sample files for testing
│   ├── uploads/                 # Storage for user-uploaded custom documents
│   └── banking_intelligence.db  # SQLite persistent graph and session database
├── tests/                       # Automated Pytest suite
│   ├── test_validators.py       # Validation logic unit tests
│   ├── test_pipeline.py         # Pipeline metrics and query flow integration tests
│   ├── test_governance.py       # SUPERSEDES firewall and policy quarantine tests
│   └── test_storage.py          # Storage backend CRUD and session persistence tests
├── assets/                      # Screenshots or diagrams used in documentation
│   ├── architecture_diagram.png # End-to-end GraphRAG pipeline architecture diagram
│   └── results_comparison_chart.png # Benchmark comparison chart
├── .streamlit/
│   ├── config.toml              # Streamlit theme and server configuration (safe to commit)
│   └── secrets.toml             # LOCAL ONLY: API keys (listed in .gitignore)
├── .env.example                 # Placeholder variable names only
├── .gitignore                   # Must list .env and .streamlit/secrets.toml
├── pyproject.toml               # Package build metadata & Pytest configuration
├── requirements.txt             # Complete list of application dependencies
├── LICENSE                      # Open-source MIT License
├── README.md                    # Standardized 17-section project documentation handbook
│
├── src/                         # Modular enterprise backend implementation
│   ├── __init__.py
│   ├── config.py                # Central environment configuration & paths
│   ├── api/                     # FastAPI REST API (app.py, routes.py)
│   ├── copilot/                 # Grounded Co-Pilot agent & prompt enhancer
│   ├── ingestion/               # Curator pipeline, PyMuPDF parser, multimodal extractor
│   ├── models/                  # Pydantic v2 schemas (PolicyRecord, ActivePolicy, GraphAction)
│   ├── retrieval/               # Hybrid retriever & vector embedding generator
│   └── storage/                 # Storage backends (BaseStorage, Embedded, Neo4j, Factory)
│
├── frontend/                    # Modern React 18 + Vite + Tailwind client
└── scripts/                     # Word report, PPTX deck, and asset generator utilities
```

---

## 🏛️ Architectural Layer Breakdown

| Directory / File | Handbook Role | Implementation Details |
| :--- | :--- | :--- |
| **[`app.py`](file:///c:/Users/sanka/Downloads/AI-Powered%20Banking%20Document%20Intelligence/app.py)** | Streamlit Entry Point | Executive banking compliance portal with KPI metrics, citation inspector, and multi-turn chat. |
| **[`pages/1_History.py`](file:///c:/Users/sanka/Downloads/AI-Powered%20Banking%20Document%20Intelligence/pages/1_History.py)** | Multipage Convention | Audit trail view of historical queries, active citations, and CSV audit export. |
| **[`components/`](file:///c:/Users/sanka/Downloads/AI-Powered%20Banking%20Document%20Intelligence/components)** | Reusable UI Pieces | Clean visual elements ([`cards.py`](file:///c:/Users/sanka/Downloads/AI-Powered%20Banking%20Document%20Intelligence/components/cards.py), [`chat.py`](file:///c:/Users/sanka/Downloads/AI-Powered%20Banking%20Document%20Intelligence/components/chat.py), [`sidebar.py`](file:///c:/Users/sanka/Downloads/AI-Powered%20Banking%20Document%20Intelligence/components/sidebar.py)) isolated from business logic. |
| **[`backend/config.py`](file:///c:/Users/sanka/Downloads/AI-Powered%20Banking%20Document%20Intelligence/backend/config.py)** | Configuration Reader | Reads from `st.secrets` when deployed to Streamlit Cloud or `.env` in local development. |
| **[`backend/services/llm_service.py`](file:///c:/Users/sanka/Downloads/AI-Powered%20Banking%20Document%20Intelligence/backend/services/llm_service.py)** | LLM Service | Manages Groq and Gemini API calls with configurable timeouts and deterministic offline fallback. |
| **[`backend/core/pipeline.py`](file:///c:/Users/sanka/Downloads/AI-Powered%20Banking%20Document%20Intelligence/backend/core/pipeline.py)** | Core Logic | Orchestrates parsing, hybrid retrieval, SUPERSEDES firewall validation, and confidence scoring. |
| **[`backend/utils/validators.py`](file:///c:/Users/sanka/Downloads/AI-Powered%20Banking%20Document%20Intelligence/backend/utils/validators.py)** | Validation & Sanitization | Validates query length, alphanumeric constraints, allowed file extensions, and file sizes. |
| **[`data/sample/`](file:///c:/Users/sanka/Downloads/AI-Powered%20Banking%20Document%20Intelligence/data/sample)** | Sample Data | Standalone sample banking PDFs and PNG rate sheets for evaluation and quick testing. |
| **[`tests/test_validators.py`](file:///c:/Users/sanka/Downloads/AI-Powered%20Banking%20Document%20Intelligence/tests/test_validators.py)** | Unit Testing | Tests validation rules for queries and uploaded files. |
| **[`tests/test_pipeline.py`](file:///c:/Users/sanka/Downloads/AI-Powered%20Banking%20Document%20Intelligence/tests/test_pipeline.py)** | Integration Testing | Tests pipeline metrics, query lifecycle, and active policy extraction. |
| **[`LICENSE`](file:///c:/Users/sanka/Downloads/AI-Powered%20Banking%20Document%20Intelligence/LICENSE)** | License | Open-source MIT License. |
