"""Embedded graph and vector storage engine using NetworkX and SQLite."""

from __future__ import annotations

import json
import math
import os
import re
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

import networkx as nx
import numpy as np

from src.config import BANKING_CATEGORIES, settings
from src.models.schemas import ActivePolicy, ChatMessage, ChatSession, PolicyRecord
from src.storage.base import BaseStorage


class EmbeddedStorageBackend(BaseStorage):
    """Zero-prerequisite embedded storage implementing full GraphRAG semantics."""

    def __init__(self, db_path: Path | str | None = None):
        self.db_path = str(db_path or settings.SQLITE_DB_PATH)
        self.graph = nx.DiGraph()
        self._init_sqlite()
        self._load_graph_from_sqlite()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_sqlite(self) -> None:
        """Create tables if not existing."""
        with self._get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS categories (
                    name TEXT PRIMARY KEY
                );

                CREATE TABLE IF NOT EXISTS policies (
                    name TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    issue_date TEXT,
                    source_text TEXT,
                    extracted_rule TEXT,
                    action_type TEXT,
                    active INTEGER DEFAULT 1,
                    superseded_by TEXT,
                    supersedes TEXT,
                    applies_to_customer TEXT,
                    requires_document TEXT,
                    embedding TEXT,
                    created_at TEXT,
                    retired_at TEXT
                );

                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id TEXT PRIMARY KEY,
                    title TEXT,
                    created_at TEXT,
                    updated_at TEXT
                );

                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    citations TEXT,
                    timestamp TEXT,
                    FOREIGN KEY(session_id) REFERENCES chat_sessions(session_id)
                );
                """
            )
            conn.commit()

    def _load_graph_from_sqlite(self) -> None:
        """Hydrate NetworkX graph from SQLite."""
        self.graph.clear()

        # Add categories
        for cat in BANKING_CATEGORIES:
            self.graph.add_node(cat, type="Category", name=cat)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM policies")
            rows = cursor.fetchall()

            for row in rows:
                p_name = row["name"]
                customers = json.loads(row["applies_to_customer"] or "[]")
                requires = json.loads(row["requires_document"] or "[]")

                self.graph.add_node(
                    p_name,
                    type="Policy",
                    name=p_name,
                    category=row["category"],
                    active=bool(row["active"]),
                    extracted_rule=row["extracted_rule"] or "",
                    source_text=row["source_text"] or "",
                    issue_date=row["issue_date"] or "",
                    action_type=row["action_type"] or "CREATE_NEW",
                    superseded_by=row["superseded_by"],
                    supersedes=row["supersedes"],
                )

                # Category edge
                self.graph.add_edge(p_name, row["category"], relation="BELONGS_TO")

                # Customer segments
                for c in customers:
                    if c:
                        self.graph.add_node(c, type="CustomerType", name=c)
                        self.graph.add_edge(p_name, c, relation="APPLIES_TO")

                # Document requirements
                for r in requires:
                    if r:
                        self.graph.add_node(r, type="DocumentRequirement", name=r)
                        self.graph.add_edge(p_name, r, relation="REQUIRES")

            # Supersession edges
            for row in rows:
                p_name = row["name"]
                if row["supersedes"]:
                    old_doc = row["supersedes"]
                    if old_doc in self.graph:
                        self.graph.add_edge(p_name, old_doc, relation="SUPERSEDES")

    def initialize_ontology(self) -> None:
        """Reset database and seed standard categories."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM policies")
            conn.execute("DELETE FROM categories")
            for cat in BANKING_CATEGORIES:
                conn.execute("INSERT OR REPLACE INTO categories (name) VALUES (?)", (cat,))
            conn.commit()
        self._load_graph_from_sqlite()

    def save_policy(self, policy: PolicyRecord) -> None:
        """Store policy in SQLite and update NetworkX graph."""
        emb_json = json.dumps(policy.embedding) if policy.embedding else None
        cust_json = json.dumps(policy.applies_to_customer)
        req_json = json.dumps(policy.requires_document)

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO policies (
                    name, category, issue_date, source_text, extracted_rule,
                    action_type, active, superseded_by, supersedes,
                    applies_to_customer, requires_document, embedding,
                    created_at, retired_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    policy.name,
                    policy.category,
                    policy.issue_date,
                    policy.source_text,
                    policy.extracted_rule,
                    policy.action_type,
                    1 if policy.active else 0,
                    policy.superseded_by,
                    policy.supersedes,
                    cust_json,
                    req_json,
                    emb_json,
                    policy.created_at,
                    policy.retired_at,
                ),
            )
            conn.commit()

        # Update in-memory graph
        self._load_graph_from_sqlite()

    def supersede_policy(self, new_policy_name: str, old_policy_name: str) -> None:
        """Mark old policy as inactive and record supersession."""
        timestamp = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            # Deactivate old policy
            conn.execute(
                """
                UPDATE policies
                SET active = 0, superseded_by = ?, retired_at = ?
                WHERE name = ?
                """,
                (new_policy_name, timestamp, old_policy_name),
            )
            # Update new policy pointer
            conn.execute(
                """
                UPDATE policies
                SET supersedes = ?
                WHERE name = ?
                """,
                (old_policy_name, new_policy_name),
            )
            conn.commit()

        self._load_graph_from_sqlite()

    def _bm25_score(self, query_terms: List[str], text: str) -> float:
        """Lightweight BM25 term matching score."""
        if not text or not query_terms:
            return 0.0
        doc_tokens = re.findall(r"\w+", text.lower())
        if not doc_tokens:
            return 0.0
        doc_len = len(doc_tokens)
        counts = Counter(doc_tokens)
        score = 0.0
        k1 = 1.5
        b = 0.75
        avg_len = 150.0  # standard baseline length
        for t in query_terms:
            tf = counts.get(t.lower(), 0)
            if tf > 0:
                score += (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_len / avg_len)))
        return score

    def query_active_policies(
        self,
        query_text: str,
        query_embedding: Sequence[float],
        top_k: int = 5,
    ) -> List[ActivePolicy]:
        """Strict governance retrieval: only returns verified active policies."""
        query_vec = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(query_vec)
        if q_norm > 0:
            query_vec /= q_norm

        query_tokens = [w for w in re.findall(r"\w+", query_text.lower()) if len(w) > 2]

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM policies WHERE active = 1")
            active_rows = cursor.fetchall()

        candidates = []
        for row in active_rows:
            p_name = row["name"]

            # Double-check graph governance: must NOT be superseded by any node
            # (i.e., in DiGraph, no incoming edge with relation='SUPERSEDES')
            is_superseded = False
            if p_name in self.graph:
                for pred, _, edge_data in self.graph.in_edges(p_name, data=True):
                    if edge_data.get("relation") == "SUPERSEDES":
                        is_superseded = True
                        break
            if is_superseded:
                continue

            # 1. Vector Score
            vector_score = 0.0
            if row["embedding"]:
                emb = np.array(json.loads(row["embedding"]), dtype=np.float32)
                p_norm = np.linalg.norm(emb)
                if p_norm > 0:
                    emb /= p_norm
                    vector_score = float(np.dot(query_vec, emb))

            # 2. Text / Keyword BM25 Score
            search_corpus = f"{row['extracted_rule']} {row['source_text']}"
            keyword_score = self._bm25_score(query_tokens, search_corpus)

            # Rejection Gate: if zero keyword overlap and weak semantic similarity, discard candidate
            if keyword_score == 0 and vector_score < 0.48:
                continue

            # 3. Score Fusion
            combined_score = vector_score + (keyword_score / 10.0)

            # 4. Multi-hop traversal via graph
            customers = []
            requires = []
            if p_name in self.graph:
                for _, target, data in self.graph.out_edges(p_name, data=True):
                    rel = data.get("relation")
                    if rel == "APPLIES_TO":
                        customers.append(target)
                    elif rel == "REQUIRES":
                        requires.append(target)

            candidates.append(
                {
                    "document_name": p_name,
                    "category": row["category"],
                    "customer_types": sorted(list(set(customers))),
                    "required_docs": sorted(list(set(requires))),
                    "extracted_rule": row["extracted_rule"] or "",
                    "source_text": row["source_text"] or "",
                    "vector_score": vector_score,
                    "keyword_score": keyword_score,
                    "score": combined_score,
                }
            )

        if not candidates:
            return []

        # Sort descending
        candidates.sort(key=lambda x: x["score"], reverse=True)
        top_candidates = candidates[:top_k]

        results = []
        for c in top_candidates:
            raw_s = c["score"]
            # Absolute calibrated confidence percentage
            # High confidence requires both good semantic score and keyword relevance
            if c["keyword_score"] > 0:
                norm_conf = min(max(c["vector_score"] * 50.0 + min(c["keyword_score"] * 20.0, 46.0), 25.0), 98.0)
            else:
                norm_conf = min(max(c["vector_score"] * 70.0, 10.0), 55.0)

            results.append(
                ActivePolicy(
                    document_name=c["document_name"],
                    category=c["category"],
                    customer_types=c["customer_types"],
                    required_docs=c["required_docs"],
                    extracted_rule=c["extracted_rule"],
                    source_text=c["source_text"],
                    score=round(raw_s, 4),
                    match_confidence=round(norm_conf, 1),
                )
            )
        return results

    def get_all_policies(self) -> List[PolicyRecord]:
        """Return all policies with their current status."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM policies ORDER BY created_at DESC")
            rows = cursor.fetchall()

        policies = []
        for r in rows:
            policies.append(
                PolicyRecord(
                    name=r["name"],
                    category=r["category"],
                    issue_date=r["issue_date"] or "",
                    source_text=r["source_text"] or "",
                    extracted_rule=r["extracted_rule"] or "",
                    action_type=r["action_type"] or "CREATE_NEW",
                    active=bool(r["active"]),
                    superseded_by=r["superseded_by"],
                    supersedes=r["supersedes"],
                    applies_to_customer=json.loads(r["applies_to_customer"] or "[]"),
                    requires_document=json.loads(r["requires_document"] or "[]"),
                    embedding=json.loads(r["embedding"]) if r["embedding"] else None,
                    created_at=r["created_at"] or "",
                    retired_at=r["retired_at"],
                )
            )
        return policies

    def get_policy(self, name: str) -> Optional[PolicyRecord]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM policies WHERE name = ?", (name,))
            r = cursor.fetchone()
            if not r:
                return None
            return PolicyRecord(
                name=r["name"],
                category=r["category"],
                issue_date=r["issue_date"] or "",
                source_text=r["source_text"] or "",
                extracted_rule=r["extracted_rule"] or "",
                action_type=r["action_type"] or "CREATE_NEW",
                active=bool(r["active"]),
                superseded_by=r["superseded_by"],
                supersedes=r["supersedes"],
                applies_to_customer=json.loads(r["applies_to_customer"] or "[]"),
                requires_document=json.loads(r["requires_document"] or "[]"),
                embedding=json.loads(r["embedding"]) if r["embedding"] else None,
                created_at=r["created_at"] or "",
                retired_at=r["retired_at"],
            )

    def get_graph_data(self) -> Dict[str, Any]:
        """Return nodes and links for 2D/3D visualization."""
        nodes = []
        links = []

        color_map = {
            "Category": "#3B82F6",         # Blue
            "Policy_Active": "#10B981",    # Emerald Green
            "Policy_Superseded": "#64748B",# Muted Slate
            "CustomerType": "#F59E0B",     # Amber
            "DocumentRequirement": "#8B5CF6", # Purple
        }

        for node_id, data in self.graph.nodes(data=True):
            ntype = data.get("type", "Unknown")
            is_active = data.get("active", True)
            group_key = ntype
            if ntype == "Policy":
                group_key = "Policy_Active" if is_active else "Policy_Superseded"

            nodes.append(
                {
                    "id": str(node_id),
                    "label": str(node_id),
                    "type": ntype,
                    "active": is_active,
                    "color": color_map.get(group_key, "#6B7280"),
                }
            )

        for u, v, data in self.graph.edges(data=True):
            links.append(
                {
                    "source": str(u),
                    "target": str(v),
                    "relation": data.get("relation", "CONNECTS_TO"),
                }
            )

        return {"nodes": nodes, "links": links}

    def save_chat_message(
        self,
        session_id: str,
        role: str,
        content: str,
        citations: Optional[List[ActivePolicy]] = None,
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        cit_json = json.dumps([c.model_dump() for c in (citations or [])])

        with self._get_connection() as conn:
            # Ensure session
            conn.execute(
                """
                INSERT OR IGNORE INTO chat_sessions (session_id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, content[:35] + ("..." if len(content) > 35 else ""), now, now),
            )
            conn.execute(
                "UPDATE chat_sessions SET updated_at = ? WHERE session_id = ?",
                (now, session_id),
            )
            conn.execute(
                """
                INSERT INTO chat_messages (session_id, role, content, citations, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, role, content, cit_json, now),
            )
            conn.commit()

    def get_session_messages(self, session_id: str, limit: int = 20) -> List[ChatMessage]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT role, content, citations, timestamp
                FROM chat_messages
                WHERE session_id = ?
                ORDER BY id ASC
                LIMIT ?
                """,
                (session_id, limit),
            )
            rows = cursor.fetchall()

        messages = []
        for r in rows:
            cits = []
            if r["citations"]:
                try:
                    cits = [ActivePolicy(**item) for item in json.loads(r["citations"])]
                except Exception:
                    cits = []
            messages.append(
                ChatMessage(
                    role=r["role"],
                    content=r["content"],
                    timestamp=r["timestamp"] or "",
                    citations=cits,
                )
            )
        return messages

    def list_sessions(self) -> List[ChatSession]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT session_id, title, created_at, updated_at FROM chat_sessions ORDER BY updated_at DESC"
            )
            rows = cursor.fetchall()

        sessions = []
        for r in rows:
            sessions.append(
                ChatSession(
                    session_id=r["session_id"],
                    title=r["title"] or "New Session",
                    created_at=r["created_at"] or "",
                    updated_at=r["updated_at"] or "",
                )
            )
        return sessions

    def delete_session(self, session_id: str) -> None:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))
            conn.commit()
