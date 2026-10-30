"""Baseline database seeding script for Sentinel Banking Knowledge Graph.

Scans data/baseline_docs for PDFs and image tables, parses regulatory rules,
links supersession chains, and populates the active knowledge graph.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import settings
from src.ingestion.curator import CuratorPipeline
from src.storage.factory import get_storage


def seed_baseline_corpus() -> None:
    """Ingest all baseline banking documents in logical version order."""
    print("=" * 70)
    print("  SENTINEL BANKING INTELLIGENCE: BASELINE KNOWLEDGE GRAPH SEEDING")
    print("=" * 70)

    storage = get_storage()
    print("[1/3] Initializing Root SME Banking Ontology...")
    storage.initialize_ontology()
    print("       Done: Categories initialized.")

    curator = CuratorPipeline(storage)

    docs_dir = settings.BASELINE_DOCS_DIR
    if not docs_dir.exists():
        print(f"[Error] Baseline docs folder not found at {docs_dir}")
        return

    # Ingestion order: 2024 policies first, then 2025, then 2026 updates
    all_files = sorted(
        list(docs_dir.glob("*.pdf")) + list(docs_dir.glob("*.png")),
        key=lambda p: (
            0 if "2024" in p.name else (1 if "2025" in p.name else 2),
            p.name,
        ),
    )

    print(f"\n[2/3] Found {len(all_files)} baseline regulatory documents in {docs_dir.name}/")
    print("-" * 70)
    print(f"{'Document Name':<38} | {'Category':<18} | {'Status'}")
    print("-" * 70)

    successful = 0
    for file_path in all_files:
        try:
            res = curator.ingest_file(file_path)
            sub_info = f"-> SUPERSEDES {res.superseded_document}" if res.superseded_document else ""
            print(f"{res.document_name:<38} | {res.category:<18} | {res.status} {sub_info}")
            successful += 1
        except Exception as e:
            print(f"{file_path.name:<38} | ERROR              | {e}")

    print("-" * 70)
    print(f"\n[3/3] Seeding Summary: {successful}/{len(all_files)} documents successfully indexed.")

    # Verification of active policies
    all_policies = storage.get_all_policies()
    active_count = sum(1 for p in all_policies if p.active)
    superseded_count = sum(1 for p in all_policies if not p.active)

    print(f"       Total Policies Stored: {len(all_policies)}")
    print(f"       Active Governed Policies: {active_count}")
    print(f"       Superseded Policies: {superseded_count}")
    print("=" * 70)


if __name__ == "__main__":
    seed_baseline_corpus()
