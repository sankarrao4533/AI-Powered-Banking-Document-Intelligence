"""Generates high-resolution graphical assets for the Sentinel Banking Presentation.
Uses Charcoal Grey (#121418), Moonlit Silver (#E2E8F0, #CBD5E1), and Signal Red (#DC2626).
"""

import os
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent if Path(__file__).resolve().parent.name == "scripts" else Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_ROOT / "docs" / "assets"
ASSETS_DIR.mkdir(exist_ok=True)

# -------------------------------------------------------------
# 1. EVALUATION COMPARISON CHART (Slide 11)
# -------------------------------------------------------------
def generate_evaluation_chart():
    categories = [
        'Outdated Policy\nLeakage Rate',
        'Hallucination Rate\non Expired Rules',
        'Tabular Rate Card\nFidelity',
        'Customer-KYC\nMulti-Hop Accuracy',
        'Strict Fallback on\nUnverified Queries'
    ]
    
    naive_rag = [78, 64, 42, 28, 12]
    sentinel_graphrag = [0, 0, 96, 95, 100]

    x = np.arange(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=300)
    fig.patch.set_facecolor('#121418')
    ax.set_facecolor('#1B1F27')

    # Gridlines
    ax.grid(axis='y', color='#2D3341', linestyle='--', alpha=0.7, zorder=0)

    # Bars
    rects1 = ax.bar(x - width/2, naive_rag, width, label='Naive Vector RAG (Baseline)', 
                    color='#7F1D1D', edgecolor='#DC2626', linewidth=1.5, zorder=3)
    rects2 = ax.bar(x + width/2, sentinel_graphrag, width, label='Sentinel Regulatory GraphRAG (Ours)', 
                    color='#DC2626', edgecolor='#F8FAFC', linewidth=1.5, zorder=3)

    # Value Labels
    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f'{h}%',
                    xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points",
                    ha='center', va='bottom', color='#FCA5A5', fontsize=10, fontweight='bold')

    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f'{h}%',
                    xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points",
                    ha='center', va='bottom', color='#FFFFFF', fontsize=10, fontweight='bold')

    ax.set_ylabel('Benchmark Score / Percentage (%)', color='#E2E8F0', fontsize=11, fontweight='bold')
    ax.set_title('Empirical Comparison: Naive Vector RAG vs. Sentinel Hybrid GraphRAG', 
                 color='#F8FAFC', fontsize=13, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, color='#E2E8F0', fontsize=9.5, fontweight='bold')
    ax.set_ylim(0, 115)

    ax.tick_params(axis='x', colors='#E2E8F0')
    ax.tick_params(axis='y', colors='#E2E8F0')

    # Spines
    for spine in ax.spines.values():
        spine.set_color('#2D3341')

    # Legend
    legend = ax.legend(facecolor='#161920', edgecolor='#2D3341', fontsize=10, loc='upper right')
    for text in legend.get_texts():
        text.set_color('#E2E8F0')

    plt.tight_layout()
    chart_path = ASSETS_DIR / "results_comparison_chart.png"
    plt.savefig(chart_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"Generated chart: {chart_path}")


# -------------------------------------------------------------
# 2. SYSTEM ARCHITECTURE DIAGRAM (Slide 7)
# -------------------------------------------------------------
def generate_architecture_diagram():
    fig, ax = plt.subplots(figsize=(12, 3.8), dpi=300)
    fig.patch.set_facecolor('#121418')
    ax.set_facecolor('#121418')
    ax.axis('off')

    boxes = [
        ("1. INGESTION", "Regulatory PDFs\n& PNG Table Cards\n(PyMuPDF + Gemini)", 0.05, 0.22, '#1B1F27', '#2D3341'),
        ("2. CURATOR", "GraphAction Schema\nNormalization &\nSupersession Linker", 0.24, 0.22, '#1B1F27', '#2D3341'),
        ("3. DUAL STORAGE", "Neo4j Cypher Graph\n+\nNetworkX / SQLite", 0.43, 0.22, '#2B1417', '#7F1D1D'),
        ("4. FIREWALL", "SUPERSEDES Guard\n& Hybrid Fusion\n(Dense + BM25)", 0.62, 0.22, '#381317', '#DC2626'),
        ("5. CO-PILOT", "Grounded Llama-3.3\nAuditable Citations\n& Strict Fallback", 0.81, 0.22, '#1B1F27', '#2D3341')
    ]

    for title, subtitle, left, width, bg, border in boxes:
        # Draw box
        rect = plt.Rectangle((left, 0.15), width, 0.7, facecolor=bg, edgecolor=border, 
                             linewidth=2, transform=ax.transAxes, zorder=2)
        ax.add_patch(rect)

        # Title text
        ax.text(left + width/2, 0.72, title, transform=ax.transAxes,
                ha='center', va='center', color='#DC2626' if border == '#DC2626' else '#F8FAFC',
                fontsize=11, fontweight='bold', zorder=3)

        # Subtitle text
        ax.text(left + width/2, 0.45, subtitle, transform=ax.transAxes,
                ha='center', va='center', color='#CBD5E1',
                fontsize=9.5, zorder=3)

    # Draw arrows between boxes
    arrow_positions = [
        (0.05 + 0.22, 0.24),
        (0.24 + 0.22, 0.43),
        (0.43 + 0.22, 0.62),
        (0.62 + 0.22, 0.81)
    ]

    for x_start, x_end in arrow_positions:
        ax.annotate('', xy=(x_end - 0.005, 0.5), xytext=(x_start + 0.005, 0.5),
                    xycoords='axes fraction', textcoords='axes fraction',
                    arrowprops=dict(facecolor='#DC2626', edgecolor='#DC2626', width=2.5, headwidth=8),
                    zorder=4)

    plt.tight_layout()
    diag_path = ASSETS_DIR / "architecture_diagram.png"
    plt.savefig(diag_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"Generated architecture diagram: {diag_path}")


if __name__ == "__main__":
    generate_evaluation_chart()
    generate_architecture_diagram()
