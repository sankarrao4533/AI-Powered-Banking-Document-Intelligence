"""Enterprise Neo4j storage backend with vector search and Cypher graph governance."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

from neo4j import Driver, GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from src.config import BANKING_CATEGORIES, settings
from src.models.schemas import ActivePolicy, ChatMessage, ChatSession, PolicyRecord
from src.storage.base import BaseStorage


def _to_bolt_uri(uri: str) -> str:
    """Ensure single-node endpoints use bolt://."""
    if uri.startswith("neo4j://"):
        return uri.replace("neo4j://", "bolt://", 1)
    if uri.startswith("neo4j+s://"):
        return uri.replace("neo4j+s://", "bolt+s://", 1)
    if uri.startswith("neo4j+ssc://"):
        return uri.replace("neo4j+ssc://", "bolt+ssc://", 1)
    return uri


class Neo4jStorageBackend(BaseStorage):
    """Enterprise Neo4j implementation with Cypher-based supersession firewall."""

    def __init__(self, uri: str | None = None, user: str | None = None, password: str | None = None):
        raw_uri = uri or settings.NEO4J_URI
        self.uri = _to_bolt_uri(raw_uri)
        self.user = user or settings.NEO4J_USER
        self.password = password or settings.NEO4J_PASSWORD
        self.driver: Driver = GraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password),
            connection_timeout=1.5,
        )
        self.driver.verify_connectivity()
        self._ensure_indexes()

    def _ensure_indexes(self) -> None:
        """Create vector and full-text indexes if not existing."""
        vec_index_query = """
        CREATE VECTOR INDEX policy_embeddings IF NOT EXISTS
        FOR (n:Policy) ON (n.embedding)
        OPTIONS {
          indexConfig: {
            `vector.dimensions`: $dimensions,
            `vector.similarity_function`: 'cosine'
          }
        }
        """
        fulltext_query = """
        CREATE FULLTEXT INDEX policy_keywords IF NOT EXISTS
        FOR (n:Policy) ON EACH [n.extracted_rule, n.source_text]
        """
        with self.driver.session() as session:
            try:
                session.run(vec_index_query, dimensions=settings.EMBEDDING_DIMENSIONS)
            except Exception as e:
                print(f"[Neo4j] Warning vector index init: {e}")
            try:
                session.run(fulltext_query)
            except Exception as e:
                print(f"[Neo4j] Warning fulltext index init: {e}")

    def initialize_ontology(self) -> None:
        clear_query = "MATCH (n) DETACH DELETE n"
        create_categories_query = """
        UNWIND $categories AS category_name
        MERGE (:Category {name: category_name})
        """
        with self.driver.session() as session:
            session.run(clear_query)
            session.run(create_categories_query, categories=list(BANKING_CATEGORIES))

    def save_policy(self, policy: PolicyRecord) -> None:
        query = """
        MATCH (c:Category {name: $category_name})
        MERGE (p:Policy {name: $policy_name})
        SET p.issue_date = $issue_date,
            p.source_text = $source_text,
            p.extracted_rule = $extracted_rule,
            p.embedding = $embedding,
            p.action_type = $action_type,
            p.active = $active,
            p.supersedes = $supersedes,
            p.superseded_by = $superseded_by,
            p.created_at = $created_at,
            p.retired_at = $retired_at
        MERGE (p)-[:BELONGS_TO]->(c)
        WITH p
        UNWIND (CASE WHEN size($applies_to_customer) > 0 THEN $applies_to_customer ELSE [null] END) AS customer
        FOREACH (ignoreMe IN CASE WHEN customer IS NOT NULL THEN [1] ELSE [] END |
            MERGE (ct:CustomerType {name: customer})
            MERGE (p)-[:APPLIES_TO]->(ct)
        )
        WITH p
        UNWIND (CASE WHEN size($requires_document) > 0 THEN $requires_document ELSE [null] END) AS doc
        FOREACH (ignoreMe IN CASE WHEN doc IS NOT NULL THEN [1] ELSE [] END |
            MERGE (dr:DocumentRequirement {name: doc})
            MERGE (p)-[:REQUIRES]->(dr)
        )
        RETURN p.name
        """
        with self.driver.session() as session:
            session.run(
                query,
                category_name=policy.category,
                policy_name=policy.name,
                issue_date=policy.issue_date,
                source_text=policy.source_text,
                extracted_rule=policy.extracted_rule,
                embedding=policy.embedding,
                action_type=policy.action_type,
                active=policy.active,
                supersedes=policy.supersedes,
                superseded_by=policy.superseded_by,
                applies_to_customer=policy.applies_to_customer,
                requires_document=policy.requires_document,
                created_at=policy.created_at,
                retired_at=policy.retired_at,
            )

    def supersede_policy(self, new_policy_name: str, old_policy_name: str) -> None:
        query = """
        MATCH (new_policy:Policy {name: $new_policy_name})
        MATCH (old_policy:Policy {name: $old_policy_name})
        MERGE (new_policy)-[:SUPERSEDES]->(old_policy)
        SET old_policy.active = false,
            old_policy.superseded_by = $new_policy_name,
            old_policy.retired_at = $retired_at,
            new_policy.supersedes = $old_policy_name
        RETURN new_policy.name, old_policy.name
        """
        now = datetime.now(timezone.utc).isoformat()
        with self.driver.session() as session:
            session.run(
                query,
                new_policy_name=new_policy_name,
                old_policy_name=old_policy_name,
                retired_at=now,
            )

    def query_active_policies(
        self,
        query_text: str,
        query_embedding: Sequence[float],
        top_k: int = 5,
    ) -> List[ActivePolicy]:
        hybrid_query = """
        CALL {
            WITH $query_embedding AS qe, $top_k AS tk
            CALL db.index.vector.queryNodes('policy_embeddings', tk, qe)
            YIELD node AS p, score AS vector_score
            RETURN p, vector_score, 0.0 AS text_score

            UNION ALL

            WITH $query_text AS uq, $top_k AS tk
            CALL db.index.fulltext.queryNodes('policy_keywords', uq, {limit: tk})
            YIELD node AS p, score AS raw_text_score
            RETURN p, 0.0 AS vector_score, raw_text_score AS text_score
        }
        WITH p, max(vector_score) AS vs, max(text_score) AS ts
        WITH p, (vs + (ts / 10.0)) AS combined_score

        // SUPERSEDES Firewall: strictly active policies only
        MATCH (p)-[:BELONGS_TO]->(c:Category)
        WHERE NOT ()-[:SUPERSEDES]->(p) AND p.active = true

        OPTIONAL MATCH (p)-[:APPLIES_TO]->(ct:CustomerType)
        OPTIONAL MATCH (p)-[:REQUIRES]->(dr:DocumentRequirement)
        WITH p, c, combined_score, collect(DISTINCT ct.name) AS customer_types, collect(DISTINCT dr.name) AS required_docs
        RETURN p.name AS document_name,
               c.name AS category,
               coalesce(p.extracted_rule, "") AS extracted_rule,
               coalesce(p.source_text, "") AS source_text,
               customer_types,
               required_docs,
               combined_score AS score
        ORDER BY score DESC
        LIMIT $top_k
        """

        # Fallback vector-only query if full-text index is not ready
        vector_only_query = """
        CALL db.index.vector.queryNodes('policy_embeddings', $top_k, $query_embedding)
        YIELD node AS p, score
        MATCH (p)-[:BELONGS_TO]->(c:Category)
        WHERE NOT ()-[:SUPERSEDES]->(p) AND p.active = true
        OPTIONAL MATCH (p)-[:APPLIES_TO]->(ct:CustomerType)
        OPTIONAL MATCH (p)-[:REQUIRES]->(dr:DocumentRequirement)
        WITH p, c, score, collect(DISTINCT ct.name) AS customer_types, collect(DISTINCT dr.name) AS required_docs
        RETURN p.name AS document_name,
               c.name AS category,
               coalesce(p.extracted_rule, "") AS extracted_rule,
               coalesce(p.source_text, "") AS source_text,
               customer_types,
               required_docs,
               score
        ORDER BY score DESC
        LIMIT $top_k
        """

        with self.driver.session() as session:
            try:
                result = session.run(
                    hybrid_query,
                    query_text=query_text,
                    query_embedding=list(query_embedding),
                    top_k=top_k,
                )
                records = list(result)
            except Exception:
                result = session.run(
                    vector_only_query,
                    query_embedding=list(query_embedding),
                    top_k=top_k,
                )
                records = list(result)

        if not records:
            return []

        max_score = records[0]["score"] if records else 1.0
        results = []
        for r in records:
            raw_s = r["score"]
            norm_conf = round(min(max(raw_s / (max_score if max_score > 0 else 1.0), 0.0), 1.0) * 96.5, 1)
            results.append(
                ActivePolicy(
                    document_name=r["document_name"],
                    category=r["category"],
                    customer_types=[c for c in r["customer_types"] if c],
                    required_docs=[d for d in r["required_docs"] if d],
                    extracted_rule=r["extracted_rule"],
                    source_text=r["source_text"],
                    score=round(raw_s, 4),
                    match_confidence=norm_conf,
                )
            )
        return results

    def get_all_policies(self) -> List[PolicyRecord]:
        query = """
        MATCH (p:Policy)-[:BELONGS_TO]->(c:Category)
        OPTIONAL MATCH (p)-[:APPLIES_TO]->(ct:CustomerType)
        OPTIONAL MATCH (p)-[:REQUIRES]->(dr:DocumentRequirement)
        WITH p, c, collect(DISTINCT ct.name) AS customer_types, collect(DISTINCT dr.name) AS required_docs
        RETURN p.name AS name,
               c.name AS category,
               coalesce(p.issue_date, "") AS issue_date,
               coalesce(p.source_text, "") AS source_text,
               coalesce(p.extracted_rule, "") AS extracted_rule,
               coalesce(p.action_type, "CREATE_NEW") AS action_type,
               coalesce(p.active, true) AS active,
               p.superseded_by AS superseded_by,
               p.supersedes AS supersedes,
               customer_types,
               required_docs,
               p.created_at AS created_at,
               p.retired_at AS retired_at
        ORDER BY p.name ASC
        """
        with self.driver.session() as session:
            records = list(session.run(query))

        policies = []
        for r in records:
            policies.append(
                PolicyRecord(
                    name=r["name"],
                    category=r["category"],
                    issue_date=r["issue_date"],
                    source_text=r["source_text"],
                    extracted_rule=r["extracted_rule"],
                    action_type=r["action_type"],
                    active=r["active"],
                    superseded_by=r["superseded_by"],
                    supersedes=r["supersedes"],
                    applies_to_customer=[c for c in r["customer_types"] if c],
                    requires_document=[d for d in r["required_docs"] if d],
                    created_at=r["created_at"] or "",
                    retired_at=r["retired_at"],
                )
            )
        return policies

    def get_policy(self, name: str) -> Optional[PolicyRecord]:
        all_p = self.get_all_policies()
        for p in all_p:
            if p.name == name:
                return p
        return None

    def get_graph_data(self) -> Dict[str, Any]:
        nodes_query = "MATCH (n) RETURN id(n) AS id, labels(n)[0] AS type, coalesce(n.name, '') AS label, coalesce(n.active, true) AS active"
        edges_query = "MATCH (a)-[r]->(b) RETURN coalesce(a.name, id(a)) AS source, coalesce(b.name, id(b)) AS target, type(r) AS relation"

        with self.driver.session() as session:
            node_recs = list(session.run(nodes_query))
            edge_recs = list(session.run(edges_query))

        nodes = []
        color_map = {
            "Category": "#3B82F6",
            "Policy_Active": "#10B981",
            "Policy_Superseded": "#64748B",
            "CustomerType": "#F59E0B",
            "DocumentRequirement": "#8B5CF6",
        }
        for n in node_recs:
            ntype = n["type"]
            is_active = n["active"]
            group_key = ntype
            if ntype == "Policy":
                group_key = "Policy_Active" if is_active else "Policy_Superseded"
            nodes.append(
                {
                    "id": str(n["label"]),
                    "label": str(n["label"]),
                    "type": ntype,
                    "active": is_active,
                    "color": color_map.get(group_key, "#6B7280"),
                }
            )

        links = [
            {"source": str(e["source"]), "target": str(e["target"]), "relation": e["relation"]}
            for e in edge_recs
        ]
        return {"nodes": nodes, "links": links}

    def save_chat_message(
        self,
        session_id: str,
        role: str,
        content: str,
        citations: Optional[List[ActivePolicy]] = None,
    ) -> None:
        query = """
        MERGE (s:Session {id: $session_id})
        ON CREATE SET s.created_at = $timestamp
        SET s.updated_at = $timestamp
        CREATE (m:Message {
            role: $role,
            content: $content,
            citations: $citations,
            timestamp: $timestamp
        })
        MERGE (s)-[:CONTAINS]->(m)
        """
        now = datetime.now(timezone.utc).isoformat()
        cit_json = json.dumps([c.model_dump() for c in (citations or [])])
        with self.driver.session() as session:
            session.run(
                query,
                session_id=session_id,
                role=role,
                content=content,
                citations=cit_json,
                timestamp=now,
            )

    def get_session_messages(self, session_id: str, limit: int = 20) -> List[ChatMessage]:
        query = """
        MATCH (s:Session {id: $session_id})-[:CONTAINS]->(m:Message)
        RETURN m.role AS role, m.content AS content, m.citations AS citations, m.timestamp AS timestamp
        ORDER BY m.timestamp ASC
        LIMIT $limit
        """
        with self.driver.session() as session:
            recs = list(session.run(query, session_id=session_id, limit=limit))

        messages = []
        for r in recs:
            cits = []
            if r["citations"]:
                try:
                    cits = [ActivePolicy(**item) for item in json.loads(r["citations"])]
                except Exception:
                    pass
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
        query = """
        MATCH (s:Session)
        RETURN s.id AS session_id, coalesce(s.created_at, "") AS created_at, coalesce(s.updated_at, "") AS updated_at
        ORDER BY s.updated_at DESC
        """
        with self.driver.session() as session:
            recs = list(session.run(query))
        return [
            ChatSession(
                session_id=r["session_id"],
                title=f"Session {r['session_id'][:8]}",
                created_at=r["created_at"],
                updated_at=r["updated_at"],
            )
            for r in recs
        ]

    def delete_session(self, session_id: str) -> None:
        query = """
        MATCH (s:Session {id: $session_id})
        OPTIONAL MATCH (s)-[:CONTAINS]->(m:Message)
        DETACH DELETE m, s
        """
        with self.driver.session() as session:
            session.run(query, session_id=session_id)
