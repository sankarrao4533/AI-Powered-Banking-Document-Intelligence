"""Comprehensive, executive-grade 15-slide PowerPoint deck generator
Project: AI-Powered Banking Document Intelligence
Theme:
  - Charcoal Grey: Rich dark backgrounds (#121418, #1A1D24, #222630)
  - Moonlit Silver: Crisp silver typography (#F8FAFC, #E2E8F0, #94A3B8)
  - Signal Red: High-impact accents, badges, warning indicators (#DC2626, #EF4444, #7F1D1D)
"""

import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

PROJECT_ROOT = Path(__file__).resolve().parent.parent if Path(__file__).resolve().parent.name == "scripts" else Path(__file__).resolve().parent
OUTPUT_FILE = PROJECT_ROOT / "docs" / "AI_Powered_Banking_Document_Intelligence_Deck.pptx"
ASSETS_DIR = PROJECT_ROOT / "docs" / "assets"
DOCS_DIR = PROJECT_ROOT / "data" / "baseline_docs"

# -------------------------------------------------------------
# PALETTE DEFINITIONS
# -------------------------------------------------------------
# Charcoal Grey
C_BG = RGBColor(0x12, 0x14, 0x18)             # Deep Charcoal background
C_CARD = RGBColor(0x1B, 0x1F, 0x27)           # Primary Charcoal Card
C_CARD_ALT = RGBColor(0x16, 0x19, 0x20)       # Darker Charcoal Card
C_CARD_BORDER = RGBColor(0x2D, 0x33, 0x41)    # Subtle Silver-Charcoal Border
C_CARD_RED_TINT = RGBColor(0x2B, 0x14, 0x17)  # Red-tinted Charcoal Card
C_RED_BORDER = RGBColor(0x7F, 0x1D, 0x1D)     # Red Accent Border

# Moonlit Silver
C_SILVER_WHITE = RGBColor(0xF8, 0xFA, 0xFC)   # Crisp Silver Header
C_SILVER_LIGHT = RGBColor(0xE2, 0xE8, 0xF0)   # Body Text
C_SILVER_MUTED = RGBColor(0x94, 0xA3, 0xB8)   # Subtitles, labels, metadata
C_SILVER_LINE = RGBColor(0x33, 0x3C, 0x4D)    # Dividers

# Signal Red
C_SIGNAL_RED = RGBColor(0xDC, 0x26, 0x26)     # Vivid Signal Red Primary
C_SIGNAL_RED_LIGHT = RGBColor(0xEF, 0x44, 0x44) # Bright Red Highlight
C_SIGNAL_RED_DARK = RGBColor(0x99, 0x1B, 0x1B)  # Dark Red Accent

FONT_FAMILY = "Segoe UI"


def set_slide_background(slide):
    """Sets a solid deep charcoal grey background."""
    bg_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5)
    )
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = C_BG
    bg_shape.line.fill.background()
    return bg_shape


def add_header(slide, tag_text, title_text, subtitle_text=None, slide_num=None):
    """Adds a standard header with a tag pill, main title, subtitle, and slide counter."""
    # Tag Pill
    tag_box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.42), Inches(3.4), Inches(0.34)
    )
    tag_box.fill.solid()
    tag_box.fill.fore_color.rgb = C_SIGNAL_RED_DARK
    tag_box.line.color.rgb = C_SIGNAL_RED
    tag_box.line.width = Pt(1)
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    tf_tag.margin_left = tf_tag.margin_right = tf_tag.margin_top = tf_tag.margin_bottom = 0
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = tag_text.upper()
    p_tag.font.name = FONT_FAMILY
    p_tag.font.size = Pt(9.5)
    p_tag.font.bold = True
    p_tag.font.color.rgb = C_SILVER_WHITE
    p_tag.alignment = PP_ALIGN.CENTER

    # Slide Counter Badge (Top Right)
    if slide_num:
        cnt_box = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(11.3), Inches(0.42), Inches(1.2), Inches(0.34)
        )
        cnt_box.fill.solid()
        cnt_box.fill.fore_color.rgb = C_CARD
        cnt_box.line.color.rgb = C_CARD_BORDER
        cnt_box.line.width = Pt(1)
        tf_cnt = cnt_box.text_frame
        tf_cnt.margin_left = tf_cnt.margin_right = tf_cnt.margin_top = tf_cnt.margin_bottom = 0
        p_cnt = tf_cnt.paragraphs[0]
        p_cnt.text = f"{slide_num:02d} / 15"
        p_cnt.font.name = FONT_FAMILY
        p_cnt.font.size = Pt(10)
        p_cnt.font.bold = True
        p_cnt.font.color.rgb = C_SILVER_MUTED
        p_cnt.alignment = PP_ALIGN.CENTER

    # Main Title
    t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.82), Inches(11.7), Inches(0.62))
    tf = t_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.name = FONT_FAMILY
    p.font.size = Pt(23)
    p.font.bold = True
    p.font.color.rgb = C_SILVER_WHITE

    # Subtitle (if present)
    if subtitle_text:
        st_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.45), Inches(11.7), Inches(0.38))
        stf = st_box.text_frame
        stf.word_wrap = True
        stf.margin_left = stf.margin_right = stf.margin_top = stf.margin_bottom = 0
        sp = stf.paragraphs[0]
        sp.text = subtitle_text
        sp.font.name = FONT_FAMILY
        sp.font.size = Pt(11.5)
        sp.font.color.rgb = C_SILVER_MUTED

    # Bottom hairline separator
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.88), Inches(11.7), Inches(0.02)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = C_SILVER_LINE
    line.line.fill.background()


def add_card(slide, left, top, width, height, bg_color=C_CARD, border_color=C_CARD_BORDER, border_width=1):
    """Draws a clean charcoal container card with rounded edges."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(border_width)
    else:
        card.line.fill.background()
    return card


def build_full_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Top Tag
    pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.65), Inches(4.2), Inches(0.36))
    pill.fill.solid()
    pill.fill.fore_color.rgb = C_SIGNAL_RED_DARK
    pill.line.color.rgb = C_SIGNAL_RED
    pill.line.width = Pt(1)
    p_pill = pill.text_frame.paragraphs[0]
    p_pill.text = "ENTERPRISE FINTECH · HYBRID GRAPHRAG RESEARCH"
    p_pill.font.name = FONT_FAMILY
    p_pill.font.size = Pt(9.5)
    p_pill.font.bold = True
    p_pill.font.color.rgb = C_SILVER_WHITE
    p_pill.alignment = PP_ALIGN.CENTER

    # Title & Subtitle Box
    t_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.15), Inches(11.7), Inches(2.1))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    p_t = tf1.paragraphs[0]
    p_t.text = "AI-Powered Banking\nDocument Intelligence"
    p_t.font.name = FONT_FAMILY
    p_t.font.size = Pt(36)
    p_t.font.bold = True
    p_t.font.color.rgb = C_SILVER_WHITE
    p_t.space_after = Pt(8)

    p_sub = tf1.add_paragraph()
    p_sub.text = "A Production-Grade Hybrid GraphRAG and Regulatory Policy Governance Platform for Tier-1 Financial Operations"
    p_sub.font.name = FONT_FAMILY
    p_sub.font.size = Pt(13.5)
    p_sub.font.color.rgb = C_SILVER_MUTED

    # Red Accent Separator Line
    red_line = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(3.38), Inches(11.7), Inches(0.04))
    red_line.fill.solid()
    red_line.fill.fore_color.rgb = C_SIGNAL_RED
    red_line.line.fill.background()

    # Team Members Section (4 Cards)
    team_members = [
        ("01", "A. Sankara Rao", "23341A4210", "Data Cleaning, Preprocessing &\nStorage Engine Architect"),
        ("02", "K. Laxminarayana", "23341A4253", "Data Inspection &\nMultimodal Extraction Pipeline"),
        ("03", "K. Ramu", "23341A4250", "Regulatory Governance &\nRetrieval Evaluation"),
        ("04", "G. Lokesh", "24345A4211", "Data Visualization, Streamlit &\nReact Web Client"),
    ]

    card_w = Inches(2.78)
    card_gap = Inches(0.19)
    card_top = Inches(3.68)
    card_h = Inches(2.15)

    for i, (num, name, roll, role) in enumerate(team_members):
        c_left = Inches(0.8) + i * (card_w + card_gap)
        c = add_card(s1, c_left, card_top, card_w, card_h, bg_color=C_CARD, border_color=C_CARD_BORDER)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.2)
        tf.margin_top = Inches(0.18)

        p_num = tf.paragraphs[0]
        p_num.text = num
        p_num.font.name = FONT_FAMILY
        p_num.font.size = Pt(18)
        p_num.font.bold = True
        p_num.font.color.rgb = C_SIGNAL_RED
        p_num.space_after = Pt(2)

        p_name = tf.add_paragraph()
        p_name.text = name
        p_name.font.name = FONT_FAMILY
        p_name.font.size = Pt(13)
        p_name.font.bold = True
        p_name.font.color.rgb = C_SILVER_WHITE
        p_name.space_after = Pt(2)

        p_roll = tf.add_paragraph()
        p_roll.text = f"Roll: {roll}"
        p_roll.font.name = FONT_FAMILY
        p_roll.font.size = Pt(10)
        p_roll.font.color.rgb = C_SILVER_MUTED
        p_roll.space_after = Pt(6)

        p_role = tf.add_paragraph()
        p_role.text = role
        p_role.font.name = FONT_FAMILY
        p_role.font.size = Pt(9.5)
        p_role.font.color.rgb = C_SILVER_LIGHT

    # Bottom Guide & Institutional Banner
    bot_card = add_card(s1, Inches(0.8), Inches(6.05), Inches(11.7), Inches(0.85), bg_color=C_CARD_ALT, border_color=C_CARD_BORDER)
    btf = bot_card.text_frame
    btf.word_wrap = True
    btf.margin_left = Inches(0.3)
    btf.margin_top = Inches(0.15)
    bp1 = btf.paragraphs[0]
    bp1.text = "PROJECT GUIDE:  Dr. / Prof. Faculty Mentor & Guide       |       DEPARTMENT:  Department of Computer Science & Engineering (AI & ML)"
    bp1.font.name = FONT_FAMILY
    bp1.font.size = Pt(10.5)
    bp1.font.bold = True
    bp1.font.color.rgb = C_SILVER_LIGHT
    bp1.space_after = Pt(2)

    bp2 = btf.add_paragraph()
    bp2.text = "INSTITUTION:  College of Engineering & Technology       |       ACADEMIC YEAR:  2025 – 2026"
    bp2.font.name = FONT_FAMILY
    bp2.font.size = Pt(10)
    bp2.font.color.rgb = C_SILVER_MUTED

    # =========================================================
    # SLIDE 2: ABSTRACT
    # =========================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "01 · Executive Summary", "Project Abstract & Strategic Purpose",
               "Eliminating LLM Hallucinations in High-Stakes Banking Operations via Topological Policy Governance", 2)

    col_w = Inches(3.72)
    col_gap = Inches(0.28)
    col_top = Inches(2.12)
    col_h = Inches(4.75)

    abstract_cols = [
        ("The Enterprise Challenge",
         "Regulated financial institutions manage thousands of dynamic policies (AML, KYC, Retail Credit, TDS Tax Slabs).",
         [
             ("Policy Churn:", "Outdated circulars remain in search indices, serving invalid or hazardous compliance guidance."),
             ("Tabular Degradation:", "Flat OCR strips interest rate matrices, bracket tiers, and footnote exclusions."),
             ("Audit Exposure:", "Hallucinations lead to regulatory penalties and costly advisory failures.")
         ],
         C_CARD, C_CARD_BORDER),

        ("The Sentinel Innovation",
         "A production-grade Hybrid GraphRAG architecture coupling Knowledge Graphs with Vector & Keyword search.",
         [
             ("SUPERSEDES Firewall:", "Topologically quarantines legacy policies (e.g. 2024/2025 rules) when 2026 updates arrive."),
             ("Dual-Engine Backend:", "Enterprise Neo4j paired with zero-dependency embedded NetworkX + SQLite."),
             ("Multimodal Extraction:", "Preserves high-fidelity tables and documents with Gemini Vision and PyMuPDF.")
         ],
         C_CARD_RED_TINT, C_RED_BORDER),

        ("Expected Impact & Outcomes",
         "Guarantees deterministic, auditable, and zero-hallucination compliance across banking workflows.",
         [
             ("100% Policy Protection:", "Superseded directives are strictly blocked from LLM inference context."),
             ("Multi-Hop Intelligence:", "Links policies directly to Customer Segments (NRI, MSME) and required KYC documents."),
             ("Full Enterprise Stack:", "Includes FastAPI REST backend, Streamlit Executive Portal, and React 18 client.")
         ],
         C_CARD, C_CARD_BORDER)
    ]

    for i, (heading, summary, points, bg, border) in enumerate(abstract_cols):
        c_left = Inches(0.8) + i * (col_w + col_gap)
        c = add_card(s2, c_left, col_top, col_w, col_h, bg_color=bg, border_color=border)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.22)

        p_h = tf.paragraphs[0]
        p_h.text = heading
        p_h.font.name = FONT_FAMILY
        p_h.font.size = Pt(14.5)
        p_h.font.bold = True
        p_h.font.color.rgb = C_SIGNAL_RED if bg == C_CARD_RED_TINT else C_SILVER_WHITE
        p_h.space_after = Pt(6)

        p_s = tf.add_paragraph()
        p_s.text = summary
        p_s.font.name = FONT_FAMILY
        p_s.font.size = Pt(10.5)
        p_s.font.color.rgb = C_SILVER_LIGHT
        p_s.space_after = Pt(12)

        for p_title, p_desc in points:
            p_bullet = tf.add_paragraph()
            p_bullet.text = f"•  {p_title} "
            p_bullet.font.name = FONT_FAMILY
            p_bullet.font.size = Pt(10)
            p_bullet.font.bold = True
            p_bullet.font.color.rgb = C_SILVER_WHITE

            run = p_bullet.add_run()
            run.text = p_desc
            run.font.name = FONT_FAMILY
            run.font.size = Pt(10)
            run.font.bold = False
            run.font.color.rgb = C_SILVER_MUTED
            p_bullet.space_after = Pt(6)

    # =========================================================
    # SLIDE 3: PROBLEM STATEMENT
    # =========================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "02 · The Challenge", "Problem Statement: Why Naive RAG Fails in Banking",
               "Standard Flat Retrieval Pipelines Create Catastrophic Regulatory Compliance Risks", 3)

    col_w = Inches(3.72)
    col_gap = Inches(0.28)
    col_top = Inches(2.12)
    col_h = Inches(3.65)

    flaws = [
        ("01", "Policy Churn & The Legacy Trap",
         "Banking rules are frequently superseded (e.g. 2024 vs 2025 vs 2026 Credit Card Lounge Access or AML cash thresholds).",
         "Standard flat vector search retrieves outdated chunks due to high cosine semantic similarity, delivering obsolete and legally dangerous guidance to clients."),

        ("02", "Tabular & Visual Degradation",
         "Interest rate slabs, TDS tax deductions, and collateral schedules are structured in multi-column matrices with fine-print footnotes.",
         "Naive text splitters destroy spatial alignment, brackets, and footnote qualifiers, producing inaccurate financial interest rates and faulty tax calculations."),

        ("03", "Flat Retrieval Blindness",
         "Banking policies are deeply relational. A home loan or Letter of Credit (LC) is contingent on customer type and required KYC documents.",
         "Isolated text chunks lack multi-hop connectivity, failing to associate policies with customer eligibility (NRI, MSME) or collateral requirements.")
    ]

    for i, (num, title, issue, impact) in enumerate(flaws):
        c_left = Inches(0.8) + i * (col_w + col_gap)
        c = add_card(s3, c_left, col_top, col_w, col_h, bg_color=C_CARD, border_color=C_CARD_BORDER)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.22)

        p_num = tf.paragraphs[0]
        p_num.text = f"VULNERABILITY {num}"
        p_num.font.name = FONT_FAMILY
        p_num.font.size = Pt(11)
        p_num.font.bold = True
        p_num.font.color.rgb = C_SIGNAL_RED
        p_num.space_after = Pt(4)

        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(13.5)
        p_t.font.bold = True
        p_t.font.color.rgb = C_SILVER_WHITE
        p_t.space_after = Pt(8)

        p_iss = tf.add_paragraph()
        p_iss.text = issue
        p_iss.font.name = FONT_FAMILY
        p_iss.font.size = Pt(10)
        p_iss.font.color.rgb = C_SILVER_LIGHT
        p_iss.space_after = Pt(8)

        p_imp = tf.add_paragraph()
        p_imp.text = "Compliance Impact: "
        p_imp.font.name = FONT_FAMILY
        p_imp.font.size = Pt(9.5)
        p_imp.font.bold = True
        p_imp.font.color.rgb = C_SIGNAL_RED_LIGHT

        run = p_imp.add_run()
        run.text = impact
        run.font.name = FONT_FAMILY
        run.font.size = Pt(9.5)
        run.font.bold = False
        run.font.color.rgb = C_SILVER_MUTED

    # Bottom Callout: Financial & Legal Liability
    alert_box = add_card(s3, Inches(0.8), Inches(5.95), Inches(11.7), Inches(0.95), bg_color=C_CARD_RED_TINT, border_color=C_RED_BORDER)
    atf = alert_box.text_frame
    atf.word_wrap = True
    atf.margin_left = Inches(0.3)
    atf.margin_top = Inches(0.18)
    ap = atf.paragraphs[0]
    ap.text = "REGULATORY REALITY: In regulated finance, LLM hallucinations are not just 'bad UX' - they constitute statutory compliance violations."
    ap.font.name = FONT_FAMILY
    ap.font.size = Pt(11.5)
    ap.font.bold = True
    ap.font.color.rgb = C_SIGNAL_RED_LIGHT
    ap.space_after = Pt(2)

    ap2 = atf.add_paragraph()
    ap2.text = "Serving an outdated interest rate or revoked AML exemption exposes financial institutions to severe legal penalties, license sanctions, and customer disputes."
    ap2.font.name = FONT_FAMILY
    ap2.font.size = Pt(10.5)
    ap2.font.color.rgb = C_SILVER_LIGHT

    # =========================================================
    # SLIDE 4: OBJECTIVES
    # =========================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "03 · Strategic Goals", "Project Objectives & Technical Milestones",
               "5 Foundational Engineering Pillars Engineered for Deterministic Banking Compliance", 4)

    objectives = [
        ("01", "Zero-Hallucination Regulatory Governance",
         "Implement a mathematical SUPERSEDES Knowledge Graph firewall that systematically quarantines superseded circulars and prevents outdated rules from reaching LLM context."),
        ("02", "Multimodal Document & Table Ingestion",
         "Engineer an automated ingestion pipeline that parses native PDFs and complex image table cards (FD interest matrices, TDS slabs) without loss of tabular fidelity."),
        ("03", "Dual-Engine Zero-Prerequisite Storage",
         "Architect an enterprise Neo4j Cypher graph backend alongside a standalone NetworkX + SQLite embedded engine with instantaneous automatic failover."),
        ("04", "Multi-Hop Relational Intelligence",
         "Construct an interconnected banking ontology linking Policy nodes to root Categories, Customer Segments (NRI, MSME), and required KYC collateral."),
        ("05", "Grounded Co-Pilot with Strict Fallback",
         "Deploy a conversational assistant that answers exclusively from verified active policy evidence, providing auditable source citations and failing closed on unverified topics.")
    ]

    card_h = Inches(0.84)
    card_gap = Inches(0.14)
    start_top = Inches(2.12)

    for i, (num, title, desc) in enumerate(objectives):
        top_pos = start_top + i * (card_h + card_gap)
        c = add_card(s4, Inches(0.8), top_pos, Inches(11.7), card_h, bg_color=C_CARD, border_color=C_CARD_BORDER)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_top = Inches(0.12)

        p = tf.paragraphs[0]
        p.text = f"{num}  ·  {title}:  "
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = C_SIGNAL_RED if i == 0 else C_SILVER_WHITE

        run = p.add_run()
        run.text = desc
        run.font.name = FONT_FAMILY
        run.font.size = Pt(10.5)
        run.font.bold = False
        run.font.color.rgb = C_SILVER_LIGHT

    # =========================================================
    # SLIDE 5: EXISTING SYSTEM
    # =========================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "04 · Current Landscape", "Existing Systems & Their Inherent Limitations",
               "Comparison Between Legacy Compliance Search and Modern Naive Vector RAG", 5)

    card_w = Inches(5.72)
    card_h = Inches(3.65)
    c_top = Inches(2.12)

    # Left: Traditional Search
    c_left = add_card(s5, Inches(0.8), c_top, card_w, card_h, bg_color=C_CARD, border_color=C_CARD_BORDER)
    tf_l = c_left.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = Inches(0.3)
    tf_l.margin_right = Inches(0.3)
    tf_l.margin_top = Inches(0.22)

    p = tf_l.paragraphs[0]
    p.text = "TRADITIONAL INTRANET & KEYWORD SEARCH"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13.5)
    p.font.bold = True
    p.font.color.rgb = C_SILVER_WHITE
    p.space_after = Pt(8)

    points_trad = [
        ("Keyword Rigidity:", "Fails on banking shorthand, synonyms, and natural language questions (e.g. 'LC limits' vs 'Letter of Credit ceiling')."),
        ("Manual Audit Bottleneck:", "Compliance officers must manually open and read 40-page circulars to cross-reference amendment dates."),
        ("No Synthesized Answers:", "Outputs a list of disconnected PDF files rather than verified answers, causing severe operational delay."),
        ("High Cost & Human Error:", "Auditor fatigue leads to missed exclusions and incorrect guidance to front-line branch officers.")
    ]
    for p_title, p_desc in points_trad:
        p_pt = tf_l.add_paragraph()
        p_pt.text = f"•  {p_title} "
        p_pt.font.name = FONT_FAMILY
        p_pt.font.size = Pt(10)
        p_pt.font.bold = True
        p_pt.font.color.rgb = C_SIGNAL_RED_LIGHT

        run = p_pt.add_run()
        run.text = p_desc
        run.font.name = FONT_FAMILY
        run.font.size = Pt(10)
        run.font.bold = False
        run.font.color.rgb = C_SILVER_LIGHT
        p_pt.space_after = Pt(5)

    # Right: Naive RAG
    c_right = add_card(s5, Inches(6.8), c_top, card_w, card_h, bg_color=C_CARD, border_color=C_CARD_BORDER)
    tf_r = c_right.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = Inches(0.3)
    tf_r.margin_right = Inches(0.3)
    tf_r.margin_top = Inches(0.22)

    p = tf_r.paragraphs[0]
    p.text = "NAIVE VECTOR RAG (FLAT SIMILARITY CHUNKING)"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13.5)
    p.font.bold = True
    p.font.color.rgb = C_SIGNAL_RED
    p.space_after = Pt(8)

    points_rag = [
        ("Blind Temporal Merging:", "Old 2024 and active 2026 circular chunks share nearly identical embeddings, causing the LLM to blend obsolete rules."),
        ("Broken Tabular Topology:", "Standard chunkers slice across rate sheets, separating interest rates from their respective tenor conditions."),
        ("Hallucinatory Compulsion:", "When asked out-of-scope questions, naive RAG forces generation from weakly similar chunks instead of failing closed."),
        ("Zero Graph Lineage:", "Lacks structural entity relationships to determine whether an NRI is eligible for domestic retail schemes.")
    ]
    for p_title, p_desc in points_rag:
        p_pt = tf_r.add_paragraph()
        p_pt.text = f"•  {p_title} "
        p_pt.font.name = FONT_FAMILY
        p_pt.font.size = Pt(10)
        p_pt.font.bold = True
        p_pt.font.color.rgb = C_SIGNAL_RED_LIGHT

        run = p_pt.add_run()
        run.text = p_desc
        run.font.name = FONT_FAMILY
        run.font.size = Pt(10)
        run.font.bold = False
        run.font.color.rgb = C_SILVER_LIGHT
        p_pt.space_after = Pt(5)

    # Summary Comparison Box
    sum_box = add_card(s5, Inches(0.8), Inches(5.95), Inches(11.7), Inches(0.95), bg_color=C_CARD_ALT, border_color=C_CARD_BORDER)
    stf = sum_box.text_frame
    stf.word_wrap = True
    stf.margin_left = Inches(0.3)
    stf.margin_top = Inches(0.18)
    sp = stf.paragraphs[0]
    sp.text = "SYSTEM GAP: Neither traditional search nor standard naive RAG can handle the continuous amendment lifecycle of banking regulations."
    sp.font.name = FONT_FAMILY
    sp.font.size = Pt(11)
    sp.font.bold = True
    sp.font.color.rgb = C_SILVER_WHITE
    sp.space_after = Pt(2)

    sp2 = stf.add_paragraph()
    sp2.text = "A compliant system requires active topological governance, multimodal table comprehension, and strict fallback guardrails."
    sp2.font.name = FONT_FAMILY
    sp2.font.size = Pt(10.5)
    sp2.font.color.rgb = C_SILVER_MUTED

    # =========================================================
    # SLIDE 6: PROPOSED SYSTEM
    # =========================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "05 · Sentinel Innovation", "Proposed System: Sentinel Regulatory GraphRAG",
               "An Enterprise-Grade, Hallucination-Proof Banking Intelligence Platform", 6)

    cards = [
        ("01", "SUPERSEDES Governance Firewall",
         "Topological Cryptographic Guardrail",
         "A graph filter strictly excludes superseded policies: WHERE NOT ()-[:SUPERSEDES]->(p) AND p.active = true. When 2026 circulars arrive, 2024 and 2025 directives are permanently quarantined from retrieval."),

        ("02", "Hybrid Retrieval & Score Fusion",
         "Dense Semantic Vectors + Full-Text BM25",
         "Combines HuggingFace 384-dimensional dense vector embeddings with Lucene/BM25 exact keyword matching, ensuring precise retrieval of technical acronyms (LC, NRI, KYC) and exact numerical thresholds."),

        ("03", "Multi-Hop Knowledge Graph Expansion",
         "Structured Financial Domain Ontology",
         "Traverses interconnected entities: (:Policy) -[:APPLIES_TO]-> (:CustomerType) and (:Policy) -[:REQUIRES]-> (:DocumentRequirement). Connects regulatory policies directly with customer eligibility and mandatory KYC."),

        ("04", "Dual-Engine Portability & Strict Fallback",
         "Zero-Prerequisite Architecture",
         "Runs in Enterprise Neo4j mode or embedded NetworkX + SQLite mode with 0ms auto-fallback. If an inquiry lacks verified active evidence, the system deterministically fails closed to eliminate hallucinations.")
    ]

    card_w = Inches(5.72)
    card_h = Inches(2.25)

    for i, (num, title, subtitle, desc) in enumerate(cards):
        col = i % 2
        row = i // 2
        c_left = Inches(0.8) + col * Inches(6.0)
        c_top = Inches(2.12) + row * Inches(2.45)

        bg = C_CARD_RED_TINT if i == 0 else C_CARD
        border = C_RED_BORDER if i == 0 else C_CARD_BORDER

        c = add_card(s6, c_left, c_top, card_w, card_h, bg_color=bg, border_color=border)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.18)

        p_num = tf.paragraphs[0]
        p_num.text = f"PILLAR {num}  ·  {subtitle.upper()}"
        p_num.font.name = FONT_FAMILY
        p_num.font.size = Pt(10)
        p_num.font.bold = True
        p_num.font.color.rgb = C_SIGNAL_RED
        p_num.space_after = Pt(2)

        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(13.5)
        p_t.font.bold = True
        p_t.font.color.rgb = C_SILVER_WHITE
        p_t.space_after = Pt(6)

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = C_SILVER_LIGHT

    # =========================================================
    # SLIDE 7: SYSTEM ARCHITECTURE
    # =========================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "06 · System Architecture", "End-to-End Sentinel System Architecture",
               "Visual Workflow Diagram and Component Interaction Across Ingestion, Storage, Firewall & Co-Pilot", 7)

    # Embed generated architecture diagram image
    arch_img_path = ASSETS_DIR / "architecture_diagram.png"
    if arch_img_path.exists():
        s7.shapes.add_picture(str(arch_img_path), Inches(0.8), Inches(2.1), Inches(11.7), Inches(2.4))

    # 4 Detailed Component Cards below diagram
    comp_cards = [
        ("1. Ingestion & Curator",
         "PyMuPDF + Gemini Vision extracts PDFs and PNG rate cards into Pydantic GraphAction schemas with auto-detected supersession."),
        ("2. Dual Storage Engine",
         "Zero-prerequisite architecture: Neo4j Cypher graph for enterprise scale, NetworkX + SQLite for instant local runtime."),
        ("3. Governance Firewall",
         "Enforces mathematical filter: NOT ()-[:SUPERSEDES]->(p). Quarantines 2024/2025 circulars when 2026 amendments exist."),
        ("4. Grounded Co-Pilot",
         "Llama-3.3-70B via Groq generates answers grounded strictly in verified active policies with clickable source citations.")
    ]

    cw = Inches(2.78)
    c_gap = Inches(0.19)
    c_top = Inches(4.65)
    ch = Inches(2.25)

    for i, (title, desc) in enumerate(comp_cards):
        c_left = Inches(0.8) + i * (cw + c_gap)
        bg = C_CARD_RED_TINT if i == 2 else C_CARD
        border = C_RED_BORDER if i == 2 else C_CARD_BORDER

        c = add_card(s7, c_left, c_top, cw, ch, bg_color=bg, border_color=border)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.2)
        tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.18)

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = C_SIGNAL_RED if i == 2 else C_SILVER_WHITE
        p.space_after = Pt(6)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.name = FONT_FAMILY
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = C_SILVER_LIGHT

    # =========================================================
    # SLIDE 8: METHODOLOGY
    # =========================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "07 · Execution Workflow", "Methodology: Step-by-Step System Execution",
               "5-Stage Engineering Pipeline Converting Unstructured Regulatory Circulars into Auditable Advice", 8)

    steps = [
        ("Step 1", "Multimodal Ingestion & Schema Transformation",
         "PyMuPDF extracts raw text and structural hierarchy from PDFs. Gemini Vision processes complex image table cards (e.g. FD_Interest_Rates_2026.png). The Curator pipeline parses extracted data into a validated Pydantic GraphAction schema specifying target ontology, extracted rule, and superseded circulars."),

        ("Step 2", "Knowledge Graph Topology & Supersession Linking",
         "Populates core nodes: (:Policy), (:Category), (:CustomerType), and (:DocumentRequirement). Creates directed edges: [:BELONGS_TO], [:APPLIES_TO], [:REQUIRES], and [:SUPERSEDES]. When a new circular supersedes an older directive, the older policy is automatically marked active = false."),

        ("Step 3", "Domain Acronym Expansion & Query Normalization",
         "Banking queries frequently contain domain shorthand (e.g. 'LC', 'NRI', 'AML', 'TDS'). The EdgeDomainQueryEnhancer expands shorthand acronyms into formal regulatory terms to align query vectors with indexed policy embeddings."),

        ("Step 4", "Hybrid Retrieval & Firewall Enforcement",
         "The retriever computes dense vector cosine similarity (all-MiniLM-L6-v2) alongside BM25 full-text keyword matching. Candidate policies are passed through the SUPERSEDES Firewall, which strictly eliminates any policy having incoming SUPERSEDES edges."),

        ("Step 5", "Multi-Hop Context Expansion & Fallback Guard",
         "Retrieves active policy rules along with connected customer segments and mandatory KYC documents. The Grounded Co-Pilot synthesizes an auditable answer with citations; if no active policy matches, it strictly triggers the fallback: 'I cannot find a verified active policy...'")
    ]

    card_h = Inches(0.84)
    card_gap = Inches(0.14)
    start_top = Inches(2.12)

    for i, (step_num, title, body) in enumerate(steps):
        top_pos = start_top + i * (card_h + card_gap)
        c = add_card(s8, Inches(0.8), top_pos, Inches(11.7), card_h, bg_color=C_CARD, border_color=C_CARD_BORDER)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_top = Inches(0.12)

        p = tf.paragraphs[0]
        p.text = f"{step_num} · {title}:  "
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = C_SIGNAL_RED if i == 3 else C_SILVER_WHITE

        run = p.add_run()
        run.text = body
        run.font.name = FONT_FAMILY
        run.font.size = Pt(10.5)
        run.font.bold = False
        run.font.color.rgb = C_SILVER_LIGHT

    # =========================================================
    # SLIDE 9: TECHNOLOGIES USED
    # =========================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "08 · Technical Stack", "Technologies, Frameworks & Infrastructure",
               "Modern Enterprise-Grade Stack Selected for Speed, Graph Portability, and Determinism", 9)

    tech_cols = [
        ("AI Models & NLP",
         C_CARD, C_CARD_BORDER,
         [("HuggingFace all-MiniLM-L6-v2", "Dense 384-dimensional sentence embeddings; runs locally with zero external API latency."),
          ("Groq Llama-3.3-70B Versatile", "Ultra-fast inference engine for grounded context synthesis and multi-turn reasoning."),
          ("Google Gemini Vision API", "Multimodal vision-language model for parsing complex table cards, tax schedules, and rate slabs.")]),

        ("Graph & Database Engines",
         C_CARD_RED_TINT, C_RED_BORDER,
         [("Neo4j Enterprise (Graph & Vector)", "Cypher graph traversals, vector index (policy_embeddings), and Lucene keyword indices."),
          ("NetworkX (Embedded Graph)", "Pure-Python in-memory directed graph engine enabling zero-setup local deployment."),
          ("SQLite3 (Persistent Store)", "Local ACID-compliant relational storage for session memory, chat logs, and metadata.")]),

        ("Backend & Frameworks",
         C_CARD, C_CARD_BORDER,
         [("Python 3.10+ & Pydantic v2", "Type-safe domain schemas, GraphAction parsing, and runtime data validation."),
          ("FastAPI & Uvicorn", "High-performance asynchronous REST API backend powering /chat, /sessions, and /upload."),
          ("PyMuPDF (fitz)", "High-speed native C-level PDF layout parser for extracting circular text and headers.")]),

        ("Frontend & Testing",
         C_CARD, C_CARD_BORDER,
         [("Streamlit Banking Portal", "Executive multi-tab dashboard with live metrics, audit trail, and Vis.js graph explorer."),
          ("React 18 + Vite + Tailwind", "Modern client-side web application with responsive session management and citations."),
          ("Pytest Test Suite", "Automated verification suite validating the supersession firewall, multi-hop, and fallbacks.")])
    ]

    card_w = Inches(2.78)
    card_gap = Inches(0.19)
    card_top = Inches(2.12)
    card_h = Inches(4.75)

    for i, (category, bg, border, items) in enumerate(tech_cols):
        c_left = Inches(0.8) + i * (card_w + card_gap)
        c = add_card(s9, c_left, card_top, card_w, card_h, bg_color=bg, border_color=border)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.22)
        tf.margin_right = Inches(0.22)
        tf.margin_top = Inches(0.22)

        p_cat = tf.paragraphs[0]
        p_cat.text = category
        p_cat.font.name = FONT_FAMILY
        p_cat.font.size = Pt(13.5)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_SIGNAL_RED if bg == C_CARD_RED_TINT else C_SILVER_WHITE
        p_cat.space_after = Pt(14)

        for name, desc in items:
            p_item = tf.add_paragraph()
            p_item.text = f"• {name}"
            p_item.font.name = FONT_FAMILY
            p_item.font.size = Pt(10.5)
            p_item.font.bold = True
            p_item.font.color.rgb = C_SILVER_WHITE
            p_item.space_after = Pt(2)

            p_desc = tf.add_paragraph()
            p_desc.text = desc
            p_desc.font.name = FONT_FAMILY
            p_desc.font.size = Pt(9.5)
            p_desc.font.color.rgb = C_SILVER_MUTED
            p_desc.space_after = Pt(10)

    # =========================================================
    # SLIDE 10: IMPLEMENTATION
    # =========================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "09 · Core Modules", "System Implementation: Modules & Multimodal Data",
               "Architectural Breakdown of the Sentinel Codebase Coupled with Real Ingested Financial Data", 10)

    # Left: 3 Module Cards (width = 6.8 Inches)
    left_w = Inches(6.8)
    modules_left = [
        ("MODULE 1: CURATOR INGESTION & OCR", "src/ingestion/curator.py & multimodal_extractor.py",
         "Ingests 12 baseline PDFs and PNG rate cards. Automatically parses documents into GraphAction schemas, establishing supersession chains (2024 -> 2025 -> 2026)."),
        ("MODULE 2: HYBRID STORAGE & FIREWALL", "src/storage/ & src/retrieval/hybrid_retriever.py",
         "Dual-engine backend (Neo4j + NetworkX/SQLite). Executes dense vector cosine search + BM25 keyword matching with topological quarantine of superseded circulars."),
        ("MODULE 3: GROUNDED CO-PILOT & REST API", "src/copilot/agent.py & src/api/routes.py",
         "FastAPI service with streaming chat endpoints, persistent multi-session memory, and strict fallback outputting STRICT_NO_ANSWER on unverified inquiries.")
    ]

    m_top = Inches(2.12)
    m_h = Inches(1.4)
    m_gap = Inches(0.18)

    for i, (m_tag, m_path, m_desc) in enumerate(modules_left):
        top_pos = m_top + i * (m_h + m_gap)
        c = add_card(s10, Inches(0.8), top_pos, left_w, m_h, bg_color=C_CARD, border_color=C_CARD_BORDER)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.22)
        tf.margin_right = Inches(0.22)
        tf.margin_top = Inches(0.15)

        p1 = tf.paragraphs[0]
        p1.text = m_tag
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(11.5)
        p1.font.bold = True
        p1.font.color.rgb = C_SIGNAL_RED
        p1.space_after = Pt(2)

        p2 = tf.add_paragraph()
        p2.text = f"File: {m_path}"
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(9.5)
        p2.font.bold = True
        p2.font.color.rgb = C_SILVER_WHITE
        p2.space_after = Pt(4)

        p3 = tf.add_paragraph()
        p3.text = m_desc
        p3.font.name = FONT_FAMILY
        p3.font.size = Pt(9.5)
        p3.font.color.rgb = C_SILVER_LIGHT

    # Right: Multimodal Rate Card Container (width = 4.6 Inches)
    right_card = add_card(s10, Inches(7.9), Inches(2.12), Inches(4.6), Inches(4.75), bg_color=C_CARD_ALT, border_color=C_CARD_BORDER)
    rtf = right_card.text_frame
    rtf.word_wrap = True
    rtf.margin_left = Inches(0.25)
    rtf.margin_right = Inches(0.25)
    rtf.margin_top = Inches(0.18)

    rp1 = rtf.paragraphs[0]
    rp1.text = "MULTIMODAL ARTIFACT INGESTION"
    rp1.font.name = FONT_FAMILY
    rp1.font.size = Pt(12)
    rp1.font.bold = True
    rp1.font.color.rgb = C_SIGNAL_RED_LIGHT
    rp1.space_after = Pt(2)

    rp2 = rtf.add_paragraph()
    rp2.text = "Sample Table Card: FD_Interest_Rates_2026.png"
    rp2.font.name = FONT_FAMILY
    rp2.font.size = Pt(9.5)
    rp2.font.color.rgb = C_SILVER_MUTED
    rp2.space_after = Pt(6)

    # Embed sample table card image
    fd_img_path = DOCS_DIR / "FD_Interest_Rates_2026.png"
    if fd_img_path.exists():
        s10.shapes.add_picture(str(fd_img_path), Inches(8.15), Inches(2.95), Inches(4.1), Inches(2.9))

    # Caption Box below image
    cap_box = s10.shapes.add_textbox(Inches(8.15), Inches(6.0), Inches(4.1), Inches(0.75))
    ctf = cap_box.text_frame
    ctf.word_wrap = True
    ctf.margin_left = ctf.margin_right = ctf.margin_top = ctf.margin_bottom = 0
    cp = ctf.paragraphs[0]
    cp.text = "Ingested via Gemini Vision API: Accurately preserves tenor tiers (7 days to 10 years), standard rates, and senior citizen bonus spreads without text flattening."
    cp.font.name = FONT_FAMILY
    cp.font.size = Pt(9)
    cp.font.color.rgb = C_SILVER_LIGHT

    # =========================================================
    # SLIDE 11: RESULTS AND EVALUATION
    # =========================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "10 · Experimental Validation", "Results & Empirical Evaluation",
               "Governance Verification & Benchmark Scenario Results Across Regulated Test Cases", 11)

    # Top KPI Metrics Cards
    metrics = [
        ("100%", "Supersession Accuracy", "Zero legacy 2024/2025 policies leaked into inference context"),
        ("0.0%", "Hallucination Rate", "Strictly fails closed on unverified or out-of-scope inquiries"),
        ("< 120ms", "Retrieval Latency", "End-to-end vector cosine + BM25 score fusion on embedded engine"),
        ("12 / 12", "Policies Governed", "10 verified active policies, 2 quarantined legacy policies")
    ]

    metric_w = Inches(2.78)
    metric_gap = Inches(0.19)
    metric_top = Inches(2.12)
    metric_h = Inches(1.15)

    for i, (val, label, sub) in enumerate(metrics):
        m_left = Inches(0.8) + i * (metric_w + metric_gap)
        bg = C_CARD_RED_TINT if i == 0 else C_CARD
        border = C_RED_BORDER if i == 0 else C_CARD_BORDER

        c = add_card(s11, m_left, metric_top, metric_w, metric_h, bg_color=bg, border_color=border)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.2)
        tf.margin_top = Inches(0.12)

        p_v = tf.paragraphs[0]
        p_v.text = val
        p_v.font.name = FONT_FAMILY
        p_v.font.size = Pt(21)
        p_v.font.bold = True
        p_v.font.color.rgb = C_SIGNAL_RED if i == 0 else C_SILVER_WHITE
        p_v.space_after = Pt(2)

        p_l = tf.add_paragraph()
        p_l.text = label
        p_l.font.name = FONT_FAMILY
        p_l.font.size = Pt(10.5)
        p_l.font.bold = True
        p_l.font.color.rgb = C_SILVER_LIGHT

        p_s = tf.add_paragraph()
        p_s.text = sub
        p_s.font.name = FONT_FAMILY
        p_s.font.size = Pt(8.5)
        p_s.font.color.rgb = C_SILVER_MUTED

    # Bottom Left: Benchmark Scenarios Table (width = 6.4 Inches)
    tbl_top = Inches(3.42)
    tbl_w = Inches(6.5)
    tbl_h = Inches(3.45)

    scenarios = [
        ("Benchmark Test Query", "Governance Action", "Status"),
        ("Lounge access rules for Signature/Infinite cards?",
         "2024/2025 blocked; retrieves active 2026 circular.",
         "PASSED (100%)"),
        ("Max unsecured Letter of Credit (LC) for MSMEs?",
         "Retrieves Corporate_LC_Limits_2024.pdf (₹50L cap).",
         "PASSED (100%)"),
        ("KYC documents required for NRI onboarding?",
         "Resolves multi-hop :REQUIRES edges for NRI segment.",
         "PASSED (100%)"),
        ("Interest rate for spacecraft loans on Mars?",
         "Fails closed: STRICT_NO_ANSWER output.",
         "PASSED (Zero Halluc.)")
    ]

    table_shape = s11.shapes.add_table(len(scenarios), 3, Inches(0.8), tbl_top, tbl_w, tbl_h)
    tbl = table_shape.table
    tbl.columns[0].width = Inches(2.7)
    tbl.columns[1].width = Inches(2.5)
    tbl.columns[2].width = Inches(1.3)

    for r_idx, row in enumerate(scenarios):
        for c_idx, cell in enumerate(row):
            tc = tbl.cell(r_idx, c_idx)
            tc.fill.solid()
            if r_idx == 0:
                tc.fill.fore_color.rgb = C_SIGNAL_RED_DARK
            else:
                tc.fill.fore_color.rgb = C_CARD if r_idx % 2 == 1 else C_CARD_ALT

            tf = tc.text_frame
            tf.word_wrap = True
            tf.margin_left = Inches(0.1)
            tf.margin_right = Inches(0.1)
            tf.margin_top = Inches(0.08)
            tf.margin_bottom = Inches(0.08)
            p = tf.paragraphs[0]
            p.text = cell
            p.font.name = FONT_FAMILY
            p.font.size = Pt(9) if r_idx > 0 else Pt(9.5)
            p.font.bold = True if (r_idx == 0 or c_idx == 2) else False
            if r_idx == 0:
                p.font.color.rgb = C_SILVER_WHITE
            elif c_idx == 2:
                p.font.color.rgb = C_SIGNAL_RED_LIGHT
            else:
                p.font.color.rgb = C_SILVER_LIGHT

    # Bottom Right: Embed Generated Chart Image (width = 4.9 Inches)
    chart_img_path = ASSETS_DIR / "results_comparison_chart.png"
    if chart_img_path.exists():
        s11.shapes.add_picture(str(chart_img_path), Inches(7.6), tbl_top, Inches(4.9), tbl_h)

    # =========================================================
    # SLIDE 12: CONCLUSION
    # =========================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "11 · Summary & Impact", "Conclusion: What Sentinel Achieves",
               "Transforming Regulatory Document Governance into a Sovereign, Hallucination-Free Asset", 12)

    conclusions = [
        ("01", "Defeated Regulatory Policy Churn",
         "Demonstrated that coupling Knowledge Graph topology with a mathematical SUPERSEDES firewall solves the fatal flaw of flat vector search, ensuring only currently valid banking circulars govern customer advice."),

        ("02", "Preserved Visual & Tabular Fidelity",
         "Integrated multimodal vision-language extraction (PyMuPDF + Gemini Vision) to accurately parse complex interest rate cards and tiered tax deduction schedules without losing spatial alignment or footnote caveats."),

        ("03", "Zero-Setup Enterprise Portability",
         "Delivered a production-ready dual-engine architecture capable of running in scalable enterprise Neo4j environments or completely offline via embedded NetworkX + SQLite with zero runtime prerequisites."),

        ("04", "Auditable, Explainable Decision Support",
         "Provided banking officers, compliance auditors, and clients with a grounded conversational co-pilot that includes complete evidence provenance, customer eligibility, and strict fail-closed security.")
    ]

    card_h = Inches(1.05)
    card_gap = Inches(0.18)
    start_top = Inches(2.12)

    for i, (num, title, body) in enumerate(conclusions):
        top_pos = start_top + i * (card_h + card_gap)
        c = add_card(s12, Inches(0.8), top_pos, Inches(11.7), card_h, bg_color=C_CARD, border_color=C_CARD_BORDER)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.3)
        tf.margin_right = Inches(0.3)
        tf.margin_top = Inches(0.18)

        p = tf.paragraphs[0]
        p.text = f"{num}  ·  {title}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_SIGNAL_RED if i == 0 else C_SILVER_WHITE
        p.space_after = Pt(4)

        p_b = tf.add_paragraph()
        p_b.text = body
        p_b.font.name = FONT_FAMILY
        p_b.font.size = Pt(10.5)
        p_b.font.color.rgb = C_SILVER_LIGHT

    # =========================================================
    # SLIDE 13: FUTURE SCOPE
    # =========================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13)
    add_header(s13, "12 · Future Roadmap", "Future Scope: Scaling Sentinel to Global Banking",
               "Strategic Roadmap for Enterprise Scalability, Autonomous Action & Cross-Border Compliance", 13)

    future_cards = [
        ("01", "Cross-Jurisdiction Harmonization",
         "Extend ontology to map multi-jurisdictional financial compliance (RBI, SEC, FCA, Basel III accords, and GDPR privacy norms)."),

        ("02", "Chunk-Level Visual PDF Deep-Linking",
         "Implement real-time visual PDF bounding-box highlighting in the UI so auditors can inspect the exact source sentence with one click."),

        ("03", "Multi-Tenant Role-Based Access (RBAC)",
         "Add cryptographic tenant isolation to partition policies by business unit (Retail Banking, Wealth Management, Corporate Treasury)."),

        ("04", "Human-in-the-Loop Review Portal",
         "Provide an executive compliance officer review queue where newly detected supersession links must be cryptographically signed before activation."),

        ("05", "Autonomous Agentic Action Execution",
         "Empower the Co-Pilot to trigger downstream core banking workflows, such as auto-populating KYC onboarding packets or drafting LC agreements."),

        ("06", "Core Banking API Connectors",
         "Build native bidirectional webhooks for enterprise core banking platforms (Finacle, Temenos Transact, Mambu, and FIS Global).")
    ]

    card_w = Inches(3.72)
    card_gap = Inches(0.28)
    card_h = Inches(2.25)

    for i, (num, title, desc) in enumerate(future_cards):
        col = i % 3
        row = i // 3
        c_left = Inches(0.8) + col * (card_w + card_gap)
        c_top = Inches(2.12) + row * Inches(2.45)

        c = add_card(s13, c_left, c_top, card_w, card_h, bg_color=C_CARD, border_color=C_CARD_BORDER)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.22)
        tf.margin_right = Inches(0.22)
        tf.margin_top = Inches(0.18)

        p_num = tf.paragraphs[0]
        p_num.text = f"ROADMAP {num}"
        p_num.font.name = FONT_FAMILY
        p_num.font.size = Pt(10)
        p_num.font.bold = True
        p_num.font.color.rgb = C_SIGNAL_RED
        p_num.space_after = Pt(2)

        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = C_SILVER_WHITE
        p_t.space_after = Pt(6)

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = C_SILVER_LIGHT

    # =========================================================
    # SLIDE 14: REFERENCES
    # =========================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14)
    add_header(s14, "13 · Literature & Standards", "Key References, Standards & Documentation",
               "Academic Research, Regulatory Mandates, and Foundational Open-Source Frameworks", 14)

    references = [
        ("01", "Edge, D., et al. (2024)",
         "From Local to Global: A Graph RAG Approach to Query-Focused Summarization.",
         "Microsoft Research. Demonstrates hierarchical knowledge graph generation for global sense-making over dense document corpora."),

        ("02", "Lewis, P., et al. (2020)",
         "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.",
         "Advances in Neural Information Processing Systems (NeurIPS 2020). Foundational methodology establishing RAG architecture for parametric-nonparametric memory."),

        ("03", "Reserve Bank of India (RBI) Regulatory Circulars (2024–2026)",
         "Master Directions on KYC, AML Compliance, NRI Banking Accounts, and Lending Norms.",
         "Official financial supervisory publications governing baseline deposit limits, foreign exchange compliance, and credit card fee disclosures."),

        ("04", "Neo4j Inc. (2025)",
         "Neo4j Enterprise Graph Database & Cypher Query Language Manual.",
         "Documentation on Graph Data Science (GDS), vector indexing (policy_embeddings), and Lucene full-text indices for hybrid semantic retrieval."),

        ("05", "Reimers, N., & Gurevych, I. (2019)",
         "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks.",
         "EMNLP 2019. Underpins the all-MiniLM-L6-v2 sentence transformer utilized for dense 384-dimensional cosine similarity evaluation."),

        ("06", "Pydantic & FastAPI Documentation (2024)",
         "Pydantic v2: Data Validation and Settings Management & FastAPI Asynchronous Web Framework.",
         "Technical specifications for high-performance schema validation, JSON serialization, and OpenAPI REST endpoint architecture.")
    ]

    card_h = Inches(0.7)
    card_gap = Inches(0.12)
    start_top = Inches(2.12)

    for i, (num, auth, title, note) in enumerate(references):
        top_pos = start_top + i * (card_h + card_gap)
        c = add_card(s14, Inches(0.8), top_pos, Inches(11.7), card_h, bg_color=C_CARD, border_color=C_CARD_BORDER)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_top = Inches(0.08)

        p = tf.paragraphs[0]
        p.text = f"[{num}]  {auth}:  "
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = C_SIGNAL_RED if i == 0 else C_SILVER_WHITE

        r_title = p.add_run()
        r_title.text = f'"{title}" '
        r_title.font.name = FONT_FAMILY
        r_title.font.size = Pt(10.5)
        r_title.font.bold = True
        r_title.font.color.rgb = C_SILVER_LIGHT

        r_note = p.add_run()
        r_note.text = f"- {note}"
        r_note.font.name = FONT_FAMILY
        r_note.font.size = Pt(9.5)
        r_note.font.bold = False
        r_note.font.color.rgb = C_SILVER_MUTED

    # =========================================================
    # SLIDE 15: THANK YOU
    # =========================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15)

    # Center card container
    center_card = add_card(s15, Inches(1.5), Inches(0.9), Inches(10.333), Inches(5.7), bg_color=C_CARD, border_color=C_CARD_BORDER)
    ctf = center_card.text_frame
    ctf.word_wrap = True
    ctf.margin_left = Inches(0.5)
    ctf.margin_right = Inches(0.5)
    ctf.margin_top = Inches(0.4)

    # Top Tag
    p_tag = ctf.paragraphs[0]
    p_tag.text = "14 · QUESTIONS & DISCUSSION"
    p_tag.font.name = FONT_FAMILY
    p_tag.font.size = Pt(11.5)
    p_tag.font.bold = True
    p_tag.font.color.rgb = C_SIGNAL_RED
    p_tag.alignment = PP_ALIGN.CENTER
    p_tag.space_after = Pt(10)

    # Big Thank You
    p_ty = ctf.add_paragraph()
    p_ty.text = "THANK YOU"
    p_ty.font.name = FONT_FAMILY
    p_ty.font.size = Pt(46)
    p_ty.font.bold = True
    p_ty.font.color.rgb = C_SILVER_WHITE
    p_ty.alignment = PP_ALIGN.CENTER
    p_ty.space_after = Pt(6)

    # Project Title
    p_proj = ctf.add_paragraph()
    p_proj.text = "AI-Powered Banking Document Intelligence & Regulatory GraphRAG"
    p_proj.font.name = FONT_FAMILY
    p_proj.font.size = Pt(16)
    p_proj.font.bold = True
    p_proj.font.color.rgb = C_SIGNAL_RED_LIGHT
    p_proj.alignment = PP_ALIGN.CENTER
    p_proj.space_after = Pt(26)

    # Team Members credits
    p_team = ctf.add_paragraph()
    p_team.text = "A. Sankara Rao (23341A4210)    •    K. Laxminarayana (23341A4253)"
    p_team.font.name = FONT_FAMILY
    p_team.font.size = Pt(12.5)
    p_team.font.bold = True
    p_team.font.color.rgb = C_SILVER_WHITE
    p_team.alignment = PP_ALIGN.CENTER
    p_team.space_after = Pt(4)

    p_team2 = ctf.add_paragraph()
    p_team2.text = "K. Ramu (23341A4250)    •    G. Lokesh (24345A4211)"
    p_team2.font.name = FONT_FAMILY
    p_team2.font.size = Pt(12.5)
    p_team2.font.bold = True
    p_team2.font.color.rgb = C_SILVER_WHITE
    p_team2.alignment = PP_ALIGN.CENTER
    p_team2.space_after = Pt(14)

    p_guide = ctf.add_paragraph()
    p_guide.text = "Guided by: Dr. / Prof. Faculty Mentor & Project Guide  |  Dept. of Computer Science & Engineering (AI & ML)"
    p_guide.font.name = FONT_FAMILY
    p_guide.font.size = Pt(11)
    p_guide.font.color.rgb = C_SILVER_MUTED
    p_guide.alignment = PP_ALIGN.CENTER
    p_guide.space_after = Pt(16)

    p_invite = ctf.add_paragraph()
    p_invite.text = "Questions, Feedback & Interactive System Demonstration Welcomed!"
    p_invite.font.name = FONT_FAMILY
    p_invite.font.size = Pt(12)
    p_invite.font.bold = True
    p_invite.font.color.rgb = C_SILVER_LIGHT
    p_invite.alignment = PP_ALIGN.CENTER

    # Save presentation
    prs.save(OUTPUT_FILE)
    print(f"Presentation successfully created and saved to: {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    build_full_deck()
