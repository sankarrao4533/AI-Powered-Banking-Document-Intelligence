"""CLI diagnostic tool for Sentinel Banking Knowledge Graph and Supersession links."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent if Path(__file__).resolve().parent.name == "scripts" else Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.storage.factory import get_storage
from src.config import settings

def main():
    storage = get_storage()
    print("=" * 70)
    print("  SENTINEL BANKING INTELLIGENCE: KNOWLEDGE GRAPH DIAGNOSTIC")
    print("=" * 70)
    print(f"Active Storage Engine: {type(storage).__name__}")
    print(f"Storage Mode setting: {settings.STORAGE_MODE}")
    print("-" * 70)

    policies = storage.get_all_policies()
    print(f"Total Policies in Storage: {len(policies)}")
    active_count = sum(1 for p in policies if p.active)
    superseded_count = len(policies) - active_count
    print(f"  - Active: {active_count}")
    print(f"  - Superseded: {superseded_count}")

    if hasattr(storage, 'graph'):
        G = storage.graph
        print("\n--- NetworkX Graph Structure ---")
        print(f"Total Graph Nodes: {G.number_of_nodes()}")
        print(f"Total Graph Edges: {G.number_of_edges()}")

        node_types = {}
        for n, data in G.nodes(data=True):
            ntype = data.get("type", "Unknown")
            node_types[ntype] = node_types.get(ntype, 0) + 1
        print(f"Node types breakdown: {node_types}")

        edge_types = {}
        for u, v, data in G.edges(data=True):
            rel = data.get("relationship", "UNKNOWN")
            edge_types[rel] = edge_types.get(rel, 0) + 1
        print(f"Edge relationships breakdown: {edge_types}")

        print("\n--- Supersession Verification ---")
        supersedes_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get("relationship") == "SUPERSEDES"]
        for u, v in supersedes_edges:
            print(f"  [Active New] {u} --SUPERSEDES--> [Legacy Old] {v}")
            u_active = G.nodes[u].get("active", False)
            v_active = G.nodes[v].get("active", True)
            print(f"    - {u}: active={u_active}")
            print(f"    - {v}: active={v_active}")

    data = storage.get_graph_data()
    nodes = data.get("nodes", [])
    links = data.get("links", [])
    print("\n--- Vis.js UI Explorer Payload ---")
    print(f"Total Visualization Nodes: {len(nodes)}")
    print(f"Total Visualization Links: {len(links)}")
    print("=" * 70)

if __name__ == "__main__":
    main()
