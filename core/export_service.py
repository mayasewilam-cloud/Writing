"""
Portfolio & Proposal Export Service for BT_301.
Generates submission-ready Microsoft Word (.docx) and Markdown (.md) documents
featuring the complete proposal draft and the authentic "Proof-of-Process" audit trail.
"""

import io
from typing import Dict, Any
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def _set_cell_background(cell, hex_color: str):
    """Sets background shading of a docx table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tc_pr.append(shd)


def generate_markdown_portfolio(data: Dict[str, Any], audit_results: Dict[str, Any] = None) -> str:
    """
    Generates a full Markdown Proof-of-Process portfolio.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    title = data.get("title", "Untitled Proposal")
    chassis = data.get("chassis", "N/A")
    tool = data.get("tool", "N/A")
    target = data.get("target", "N/A")
    student_name = data.get("student_name", "BT_301 Student / Team")

    md = []
    md.append(f"# {title}")
    md.append(f"**Course**: BT_301 (Introduction to Biotechnology - Fundable Research Proposals)")
    md.append(f"**Author / Team**: {student_name}")
    md.append(f"**Date Generated**: {timestamp}")
    md.append(f"**Target Agency Alignment**: STDF / ICGEB Grant Proposal Standard")
    md.append(f"**Academic Framework & System Architects**: Maya Abdelrazek & Youssef Aboulkheir")
    md.append("\n---\n")

    # Abstract
    md.append("## Structured Abstract")
    md.append(data.get("abstract", "*No abstract provided.*"))
    md.append("\n---\n")

    # Proof of Process
    md.append("## I. Proof-of-Process & Literature Audit Trail")
    md.append("### 1.1 The 3 Magic Nouns (Topic Formulation)")
    md.append(f"- **Biological Chassis**: `{chassis}`")
    md.append(f"- **Molecular Tool / Enzyme**: `{tool}`")
    md.append(f"- **Target Problem / Villain**: `{target}`\n")

    md.append("### 1.2 Boolean Search Query Used")
    search_q = data.get("search_query", f'"{chassis}" AND "{tool}" AND "{target}"')
    md.append(f"```text\n{search_q}\n```\n")

    md.append("### 1.3 4-Color Evidence Extraction Matrix")
    matrix = data.get("matrix", {})
    md.append("| Color / Category | Extracted Primary Literature Evidence | Metric / Baseline |")
    md.append("| :--- | :--- | :--- |")
    md.append(f"| **🟡 Yellow: Crisis Burden** | {matrix.get('yellow', 'N/A')} | Hard number/prevalence |")
    md.append(f"| **🔵 Blue: Current Tool** | {matrix.get('blue', 'N/A')} | Existing baseline |")
    md.append(f"| **🟢 Green: Knowledge Gap** | {matrix.get('green', 'N/A')} | Critical bottleneck |")
    md.append(f"| **🔴 Red: Target Milestone** | {matrix.get('red', 'N/A')} | Target quantitative threshold |")
    md.append("\n---\n")

    # Proposal Body
    md.append("## II. Research Grant Proposal")
    
    md.append("### 1. Background & Inverted Funnel Rationale (Rubric: 20%)")
    funnel = data.get("funnel", {})
    md.append(f"**1.1 Global / National Burden**:\n{funnel.get('tier1', '')}\n")
    md.append(f"**1.2 Current Scientific Benchmark**:\n{funnel.get('tier2', '')}\n")
    md.append(f"**1.3 The Explicit Knowledge Gap**:\n{funnel.get('tier3', '')}\n")
    md.append(f"**1.4 Project Hypothesis & Primary Project Aim**:\n{funnel.get('tier4', '')}\n")

    md.append("### 2. Specific Aims (Rubric: 5%)")
    aims = data.get("aims", {})
    md.append(f"- **Aim 1**: {aims.get('aim1', 'N/A')}")
    md.append(f"- **Aim 2**: {aims.get('aim2', 'N/A')}")
    md.append(f"- **Aim 3**: {aims.get('aim3', 'N/A')}\n")

    md.append("### 3. Methodology & Experimental Controls (Rubric: 15% + Future Tense)")
    md.append(data.get("methodology", "*No methodology submitted.*") + "\n")

    md.append("### 4. Expected Outcomes & Long-Term Impact (Section 10 / Rubric: 10%)")
    md.append(f"**Deliverables & Key Figures**:\n{data.get('expected_outcomes', '*No deliverables submitted.*')}\n")
    md.append(f"**Long-Term Impact & Significance (Why Results Matter)**:\n{data.get('impact', '*No impact statement submitted.*')}\n")

    md.append("### 5. Research Landscape & Comparative Position (Rubric: 5%)")
    comp = data.get("competitor_data", {})
    if comp:
        md.append("#### Research Landscape & Comparative Position Matrix")
        md.append("| Dimension | Established approach [Published Evidence] | Recent approach [Published Evidence] | Proposed research [Target / Hypothesis] |")
        md.append("| :--- | :--- | :--- | :--- |")
        p_est = comp.get("principle_established") or comp.get("incumbent_name", "Standard Benchmark")
        p_rec = comp.get("principle_recent") or comp.get("emerging_name", "Recent Alternative")
        p_prop = comp.get("principle_proposed") or comp.get("proposed_name", data.get("tool", "Proposed Solution"))
        md.append(f"| **Principle / technology** | {p_est} | {p_rec} | {p_prop} |")

        s_est = comp.get("strength_established", "Broad adoption, established clinical data")
        s_rec = comp.get("strength_recent", "Higher laboratory turnover or sensitivity")
        s_prop = comp.get("strength_proposed", "Combines high efficiency with stability")
        md.append(f"| **Main strength** | {s_est} | {s_rec} | {s_prop} |")

        l_est = comp.get("limitation_established", "Slow turnaround, high cost, or invasiveness")
        l_rec = comp.get("limitation_recent", "Thermally unstable, matrix interference")
        l_prop = comp.get("limitation_proposed", "Requires optimization under real-world conditions")
        md.append(f"| **Key limitation** | {l_est} | {l_rec} | {l_prop} |")

        perf_est = comp.get("performance_established") or comp.get("incumbent_speed", "Standard baseline metric")
        perf_rec = comp.get("performance_recent") or comp.get("emerging_speed", "Published benchmark")
        perf_prop = comp.get("performance_proposed") or comp.get("proposed_speed", "Target milestone")
        md.append(f"| **Performance** | {perf_est} | {perf_rec} | {perf_prop} |")

        c_est = comp.get("cost_established") or comp.get("incumbent_cost", "High CapEx, centralized ($$$)")
        c_rec = comp.get("cost_recent") or comp.get("emerging_cost", "Moderate cost ($$)")
        c_prop = comp.get("cost_proposed") or comp.get("proposed_cost", "Low cost, decentralized ($)")
        md.append(f"| **Cost / resources** | {c_est} | {c_rec} | {c_prop} |")

        saf_est = comp.get("safety_established") or comp.get("incumbent_safety", "Standard compliance")
        saf_rec = comp.get("safety_recent") or comp.get("emerging_safety", "Regulatory hurdle or containment needed")
        saf_prop = comp.get("safety_proposed") or comp.get("proposed_safety", "Non-toxic, sustainable profile")
        md.append(f"| **Safety / sustainability** | {saf_est} | {saf_rec} | {saf_prop} |")

        e_est = comp.get("evidence_established", "Decades of commercial / clinical literature")
        e_rec = comp.get("evidence_recent", "Single published in vitro proof-of-concept")
        e_prop = comp.get("evidence_proposed", "Rigorous experimental plan with controls")
        md.append(f"| **Evidence available** | {e_est} | {e_rec} | {e_prop} |")

        g_est = comp.get("gap_established", "High cost and delay block decentralized use")
        g_rec = comp.get("gap_recent", "Rapid inactivation in operational matrix")
        g_prop = comp.get("gap_proposed", "Addressable limitation driving this proposal")
        md.append(f"| **Unresolved gap** | {g_est} | {g_rec} | {g_prop} |")

        contrib_prop = comp.get("contribution_proposed") or data.get("usps", "Direct novel contribution")
        md.append(f"| **Contribution of proposed study** | — | — | {contrib_prop} |\n")

    md.append(f"**Unique Selling Proposition (USP)**:\n{data.get('usps', '*No USPs submitted.*')}\n")

    md.append("### 6. SWOT & PESTEL Analyses (Rubric: 10%)")
    swot = data.get("swot", {})
    md.append("#### SWOT Analysis")
    md.append(f"- **Strengths**: {swot.get('strengths', 'N/A')}")
    md.append(f"- **Weaknesses (Biochemical/Bioprocess)**: {swot.get('weaknesses', 'N/A')}")
    md.append(f"- **Opportunities**: {swot.get('opportunities', 'N/A')}")
    md.append(f"- **Threats**: {swot.get('threats', 'N/A')}\n")

    pestel = data.get("pestel", {})
    md.append("#### PESTEL Dimensions")
    for key, val in pestel.items():
        md.append(f"- **{key.capitalize()}**: {val}")
    md.append("\n")

    md.append("### 7. Time Plan & Go/No-Go Decision Gates (Rubric: 5%)")
    gs = data.get("gantt_schedule", {})
    tot_m = gs.get("total_months", 18)
    md.append(f"**Total Staged Project Duration**: {tot_m} Months\n")
    custom_tasks = gs.get("tasks", [])
    if custom_tasks and isinstance(custom_tasks, list):
        for t in custom_tasks:
            name = t.get("name", "Task")
            s = t.get("start", 1)
            e = t.get("end", tot_m)
            gate = f" (Go/No-Go Gate: {t.get('gate')})" if t.get("gate") else ""
            md.append(f"- **{name}**: Months {s}–{e}{gate}")
        md.append("\n")
    elif gs:
        wp1_g = f" (Go/No-Go Gate: {gs.get('wp1_gate')})" if gs.get('wp1_gate') else ""
        wp2_g = f" (Go/No-Go Gate: {gs.get('wp2_gate')})" if gs.get('wp2_gate') else ""
        wp3_g = f" (Go/No-Go Gate: {gs.get('wp3_gate')})" if gs.get('wp3_gate') else ""
        md.append(f"- **Work Package 1**: Months {gs.get('wp1_start', 1)}–{gs.get('wp1_end', 6)}{wp1_g}")
        md.append(f"- **Work Package 2**: Months {gs.get('wp2_start', 5)}–{gs.get('wp2_end', 12)}{wp2_g}")
        md.append(f"- **Work Package 3**: Months {gs.get('wp3_start', 10)}–{gs.get('wp3_end', tot_m)}{wp3_g}\n")
    if data.get("time_plan"):
        md.append(data.get("time_plan") + "\n")

    md.append("### 8. Tabulated Bill of Materials & Funding Breakdown (Rubric: 5%)")
    materials = data.get("budget_materials", [])
    if materials:
        md.append("| Material / Reagent / Item | Manufacturer / Vendor | Catalog # | Category | Qty | Unit ($) | Total ($) |")
        md.append("| :--- | :--- | :--- | :--- | :---: | ---: | ---: |")
        grand_total = 0.0
        for mat in materials:
            q = int(mat.get("qty", 1))
            c = float(mat.get("unit_cost", 0))
            sub = q * c
            grand_total += sub
            cat_name = str(mat.get("category", "Consumables")).capitalize()
            md.append(f"| {mat.get('item', 'Item')} | {mat.get('vendor', '—')} | {mat.get('catalog', '—')} | {cat_name} | {q} | ${c:,.2f} | ${sub:,.2f} |")
        md.append(f"| **TOTAL FUNDING REQUESTED** | — | — | — | — | — | **${grand_total:,.2f}** |\n")
    elif data.get("budget_items"):
        bi = data.get("budget_items", {})
        md.append("| Budget Category | Allocation ($) |")
        md.append("| :--- | ---: |")
        md.append(f"| 1. Consumables & Reagents | ${float(bi.get('consumables', 0)):,.2f} |")
        md.append(f"| 2. Personnel Incentives | ${float(bi.get('personnel', 0)):,.2f} |")
        md.append(f"| 3. Utilities & Overhead | ${float(bi.get('utilities', 0)):,.2f} |")
        md.append(f"| 4. Specialized Equipment | ${float(bi.get('equipment', 0)):,.2f} |")
        tot = sum([float(bi.get(k, 0)) for k in ['consumables', 'personnel', 'utilities', 'equipment']])
        md.append(f"| **TOTAL REQUESTED** | **${tot:,.2f}** |\n")

    if data.get("budget"):
        md.append(f"**Budget Justification Notes**:\n{data.get('budget')}\n")

    md.append("### 9. References (Rubric: 5%)")
    refs = data.get("references", "")
    md.append(refs if refs else "*No references entered.*")
    md.append("\n---\n")

    # Section 3: Socratic Rubric Audit
    if audit_results:
        md.append("## III. Faculty Socratic Audit & Evaluation Report")
        raw = audit_results.get("raw_total", 0)
        gpa = audit_results.get("gpa_score", 0)
        md.append(f"**Total Raw Score**: `{raw} / 85.0 marks`  ")
        md.append(f"**Estimated BT_301 GPA Grade**: `{gpa} / 10.0 GPA`\n")

    md.append("\n---\n")
    md.append("### Protected Intellectual Property & Academic Framework")
    md.append("© BioWriter Studio • Research Proposal & Proof-of-Process Learning Architecture  ")
    md.append("Designed & Authored by **Maya Abdelrazek & Youssef Aboulkheir**. All rights reserved.\n")

    return "\n".join(md)


def generate_docx_portfolio(data: Dict[str, Any], audit_results: Dict[str, Any] = None) -> io.BytesIO:
    """
    Builds a professional Microsoft Word (.docx) portfolio using python-docx.
    """
    doc = Document()

    # Core Properties / Intellectual Property Metadata
    doc.core_properties.author = "Maya Abdelrazek & Youssef Aboulkheir"
    doc.core_properties.comments = "BioWriter Studio Academic Framework. Designed by Maya Abdelrazek & Youssef Aboulkheir."

    # Page Margins: 1 inch & Footer Watermark
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
        # Document Footer Watermark
        footer = section.footer
        footer_p = footer.paragraphs[0]
        footer_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        footer_run = footer_p.add_run("BioWriter Studio | Academic Architects: Maya Abdelrazek & Youssef Aboulkheir")
        footer_run.font.size = Pt(8.5)
        footer_run.font.italic = True
        footer_run.font.color.rgb = RGBColor(148, 163, 184)

    # Title
    title = data.get("title", "Untitled Research Grant Proposal")
    title_p = doc.add_paragraph()
    title_run = title_p.add_run(title)
    title_run.font.size = Pt(20)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(26, 54, 93) # Navy blue
    title_p.paragraph_format.space_after = Pt(6)

    # Subtitle / Metadata
    sub_p = doc.add_paragraph()
    sub_run = sub_p.add_run("BT_301: Writing Fundable Scientific Research Proposals\n")
    sub_run.font.size = Pt(11)
    sub_run.font.bold = True
    sub_run.font.color.rgb = RGBColor(74, 85, 104)

    student = data.get("student_name", "BT_301 Student / Team")
    date_str = datetime.now().strftime("%B %d, %Y")
    meta_run = sub_p.add_run(f"Principal Investigator(s): {student} | Date: {date_str} | Agency Standard: STDF / ICGEB\n")
    meta_run.font.size = Pt(10)
    meta_run.font.italic = True

    author_mark_run = sub_p.add_run("Framework Architects & IP: Maya Abdelrazek & Youssef Aboulkheir")
    author_mark_run.font.size = Pt(9)
    author_mark_run.font.bold = True
    author_mark_run.font.color.rgb = RGBColor(100, 116, 139)
    sub_p.paragraph_format.space_after = Pt(18)

    # Abstract Section Box
    doc.add_heading("Structured Abstract", level=1)
    abstract_text = data.get("abstract", "No abstract provided.")
    ab_p = doc.add_paragraph()
    ab_run = ab_p.add_run(abstract_text)
    ab_run.font.size = Pt(10.5)
    ab_p.paragraph_format.space_after = Pt(14)

    # Proof of Process Header
    doc.add_heading("I. Proof-of-Process & Literature Extraction Matrix", level=1)
    
    # 3 Pillars Table
    table_p = doc.add_table(rows=4, cols=2)
    table_p.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_p.autofit = True
    
    headers = [
        ("Parameter", "Student Extracted Value"),
        ("Biological Chassis (Host)", data.get("chassis", "N/A")),
        ("Molecular Tool / Enzyme", data.get("tool", "N/A")),
        ("Target Problem / Metric", data.get("target", "N/A"))
    ]
    for row_idx, (col1, col2) in enumerate(headers):
        r = table_p.rows[row_idx]
        r.cells[0].text = col1
        r.cells[1].text = col2
        if row_idx == 0:
            _set_cell_background(r.cells[0], "1A365D")
            _set_cell_background(r.cells[1], "1A365D")
            r.cells[0].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            r.cells[1].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            r.cells[0].paragraphs[0].runs[0].font.bold = True
            r.cells[1].paragraphs[0].runs[0].font.bold = True
        else:
            _set_cell_background(r.cells[0], "F7FAFC")

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # 4-Color Matrix Table
    doc.add_heading("4-Color Extraction Sheet", level=2)
    matrix_table = doc.add_table(rows=5, cols=2)
    matrix_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    m_data = data.get("matrix", {})
    m_rows = [
        ("Evidence Category", "Extracted Primary Literature Evidence"),
        ("🟡 Yellow: Crisis Burden", m_data.get("yellow", "N/A")),
        ("🔵 Blue: Current Standard", m_data.get("blue", "N/A")),
        ("🟢 Green: Knowledge Gap", m_data.get("green", "N/A")),
        ("🔴 Red: Target Metric", m_data.get("red", "N/A"))
    ]
    for idx, (c1, c2) in enumerate(m_rows):
        row = matrix_table.rows[idx]
        row.cells[0].text = c1
        row.cells[1].text = c2
        if idx == 0:
            _set_cell_background(row.cells[0], "2D3748")
            _set_cell_background(row.cells[1], "2D3748")
            row.cells[0].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            row.cells[1].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            row.cells[0].paragraphs[0].runs[0].font.bold = True
            row.cells[1].paragraphs[0].runs[0].font.bold = True
        else:
            _set_cell_background(row.cells[0], "EDF2F7")

    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # Proposal Body
    doc.add_heading("II. Full Research Proposal Draft", level=1)

    # Background
    doc.add_heading("1. Background & Inverted Funnel (Rubric: 20%)", level=2)
    funnel = data.get("funnel", {})
    sections = [
        ("1.1 Global and National Burden", funnel.get("tier1", "")),
        ("1.2 Current Scientific Benchmark & Baseline", funnel.get("tier2", "")),
        ("1.3 Critical Knowledge Gap", funnel.get("tier3", "")),
        ("1.4 Project Hypothesis & Primary Project Objectives", funnel.get("tier4", ""))
    ]
    for stitle, stext in sections:
        p = doc.add_paragraph()
        run_h = p.add_run(stitle + "\n")
        run_h.bold = True
        run_h.font.size = Pt(11)
        run_t = p.add_run(stext if stext else "[Pending draft]")
        run_t.font.size = Pt(10.5)
        p.paragraph_format.space_after = Pt(8)

    # Specific Aims
    doc.add_heading("2. Specific Aims Blueprint (Rubric: 5%)", level=2)
    aims = data.get("aims", {})
    for i in range(1, 4):
        aim_key = f"aim{i}"
        ap = doc.add_paragraph(style='List Bullet')
        r_aim = ap.add_run(f"Aim {i}: ")
        r_aim.bold = True
        ap.add_run(aims.get(aim_key, f"Specific Aim {i} not specified."))

    # Methodology
    doc.add_heading("3. Methodology & Experimental Controls (Rubric: 15% + Future Tense)", level=2)
    mp = doc.add_paragraph()
    mp.add_run(data.get("methodology", "[No methodology drafted]"))
    mp.paragraph_format.space_after = Pt(10)

    # Expected Outcomes & Long-Term Impact
    doc.add_heading("4. Expected Outcomes & Long-Term Impact (Section 10 / Rubric: 10%)", level=2)
    p_deliv = doc.add_paragraph()
    p_deliv.add_run("Anticipated Deliverables & Key Visual Figures:\n").bold = True
    p_deliv.add_run(data.get("expected_outcomes", "[No outcomes drafted]"))
    p_deliv.paragraph_format.space_after = Pt(6)

    p_imp = doc.add_paragraph()
    p_imp.add_run("Expected Impact & Significance (Why Results Matter):\n").bold = True
    p_imp.add_run(data.get("impact", "[No long-term impact statement drafted]"))
    p_imp.paragraph_format.space_after = Pt(10)

    # Research Landscape & Comparative Position
    doc.add_heading("5. Research Landscape & Comparative Position (Rubric: 5%)", level=2)
    comp = data.get("competitor_data", {})
    if comp:
        doc.add_paragraph("Research Landscape & Comparative Position Matrix:").runs[0].bold = True
        comp_table = doc.add_table(rows=10, cols=4)
        comp_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        comp_rows = [
            ("Dimension", "Established approach\n[Published Evidence]", "Recent approach\n[Published Evidence]", "Proposed research\n[Target / Hypothesis]"),
            ("Principle / technology", comp.get("principle_established") or comp.get("incumbent_name", "Standard Benchmark"), comp.get("principle_recent") or comp.get("emerging_name", "Recent Alternative"), comp.get("principle_proposed") or comp.get("proposed_name", data.get("tool", "Proposed Solution"))),
            ("Main strength", comp.get("strength_established", "Broad adoption, established clinical data"), comp.get("strength_recent", "Higher laboratory turnover or sensitivity"), comp.get("strength_proposed", "Combines high efficiency with stability")),
            ("Key limitation", comp.get("limitation_established", "Slow turnaround, high cost, or invasiveness"), comp.get("limitation_recent", "Thermally unstable, matrix interference"), comp.get("limitation_proposed", "Requires optimization under real-world conditions")),
            ("Performance", comp.get("performance_established") or comp.get("incumbent_speed", "Standard baseline metric"), comp.get("performance_recent") or comp.get("emerging_speed", "Published benchmark"), comp.get("performance_proposed") or comp.get("proposed_speed", "Target milestone")),
            ("Cost / resources", comp.get("cost_established") or comp.get("incumbent_cost", "High CapEx ($$$)"), comp.get("cost_recent") or comp.get("emerging_cost", "Moderate cost ($$)"), comp.get("cost_proposed") or comp.get("proposed_cost", "Low cost, decentralized ($)")),
            ("Safety / sustainability", comp.get("safety_established") or comp.get("incumbent_safety", "Standard compliance"), comp.get("safety_recent") or comp.get("emerging_safety", "Regulatory hurdle"), comp.get("safety_proposed") or comp.get("proposed_safety", "Non-toxic, sustainable profile")),
            ("Evidence available", comp.get("evidence_established", "Decades of commercial literature"), comp.get("evidence_recent", "Single published in vitro proof-of-concept"), comp.get("evidence_proposed", "Rigorous experimental plan with controls")),
            ("Unresolved gap", comp.get("gap_established", "High cost/delay blocks decentralization"), comp.get("gap_recent", "Rapid inactivation in operational matrix"), comp.get("gap_proposed", "Addressable limitation driving this proposal")),
            ("Contribution of proposed study", "—", "—", comp.get("contribution_proposed") or data.get("usps", "Direct novel contribution"))
        ]
        for idx, r_data in enumerate(comp_rows):
            r = comp_table.rows[idx]
            for c_idx in range(4):
                r.cells[c_idx].text = str(r_data[c_idx])
            if idx == 0:
                for c_idx in range(4):
                    _set_cell_background(r.cells[c_idx], "1A365D")
                    r.cells[c_idx].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
                    r.cells[c_idx].paragraphs[0].runs[0].font.bold = True
            else:
                _set_cell_background(r.cells[0], "F7FAFC")
                _set_cell_background(r.cells[3], "F0FDF4") # soft green highlight for proposed solution
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    p_usp = doc.add_paragraph()
    p_usp.add_run("Unique Selling Proposition (USP):\n").bold = True
    p_usp.add_run(data.get("usps", "[No USPs drafted]"))
    p_usp.paragraph_format.space_after = Pt(10)

    # SWOT & PESTEL
    doc.add_heading("6. SWOT & PESTEL Analyses (Rubric: 10%)", level=2)
    swot = data.get("swot", {})
    pestel = data.get("pestel", {})
    sp = doc.add_paragraph()
    sp.add_run("Strengths: ").bold = True
    sp.add_run(swot.get("strengths", "N/A") + "\n")
    sp.add_run("Weaknesses (Biochemical): ").bold = True
    sp.add_run(swot.get("weaknesses", "N/A") + "\n")
    sp.add_run("Opportunities: ").bold = True
    sp.add_run(swot.get("opportunities", "N/A") + "\n")
    sp.add_run("Threats: ").bold = True
    sp.add_run(swot.get("threats", "N/A") + "\n")

    # Time Plan & Go/No-Go Decision Gates
    doc.add_heading("7. Time Plan & Go/No-Go Decision Gates (Rubric: 5%)", level=2)
    gs = data.get("gantt_schedule", {})
    tot_m = gs.get("total_months", 18)
    p_dur = doc.add_paragraph()
    p_dur.add_run(f"Total Staged Project Duration: {tot_m} Months\n").bold = True
    custom_tasks = gs.get("tasks", [])
    if custom_tasks and isinstance(custom_tasks, list):
        for t in custom_tasks:
            name = t.get("name", "Task")
            s = t.get("start", 1)
            e = t.get("end", tot_m)
            gate = f" | Go/No-Go Gate: {t.get('gate')}" if t.get("gate") else ""
            p_wp = doc.add_paragraph(style='List Bullet')
            p_wp.add_run(f"{name} (Months {s}–{e}){gate}")
    elif gs:
        wp_list = [
            ("WP1: Construction & Preparation", gs.get("wp1_start", 1), gs.get("wp1_end", 6), gs.get("wp1_gate", "")),
            ("WP2: Functional Testing & Evaluation", gs.get("wp2_start", 5), gs.get("wp2_end", 12), gs.get("wp2_gate", "")),
            ("WP3: Real-World Validation & Performance", gs.get("wp3_start", 10), gs.get("wp3_end", tot_m), gs.get("wp3_gate", ""))
        ]
        for wp_title, s, e, gate in wp_list:
            p_wp = doc.add_paragraph(style='List Bullet')
            gate_text = f" | Go/No-Go Gate: {gate}" if gate else ""
            p_wp.add_run(f"{wp_title} (Months {s}–{e}){gate_text}")

    if data.get("time_plan"):
        tp = doc.add_paragraph()
        tp.add_run(data.get("time_plan"))
        tp.paragraph_format.space_after = Pt(8)

    # Tabulated Bill of Materials & Funding Breakdown
    doc.add_heading("8. Tabulated Bill of Materials & Funding Breakdown (Rubric: 5%)", level=2)
    materials = data.get("budget_materials", [])
    if materials:
        mat_table = doc.add_table(rows=len(materials) + 2, cols=7)
        mat_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        headers = ["Material / Reagent / Item", "Manufacturer", "Cat #", "Category", "Qty", "Unit ($)", "Subtotal ($)"]
        r_head = mat_table.rows[0]
        for c_idx, h in enumerate(headers):
            r_head.cells[c_idx].text = h
            _set_cell_background(r_head.cells[c_idx], "1A365D")
            r_head.cells[c_idx].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            r_head.cells[c_idx].paragraphs[0].runs[0].font.bold = True

        grand_total = 0.0
        for idx, mat in enumerate(materials, 1):
            r_row = mat_table.rows[idx]
            q = int(mat.get("qty", 1))
            c = float(mat.get("unit_cost", 0))
            sub = q * c
            grand_total += sub
            r_row.cells[0].text = str(mat.get("item", "Item"))
            r_row.cells[1].text = str(mat.get("vendor", "—"))
            r_row.cells[2].text = str(mat.get("catalog", "—"))
            r_row.cells[3].text = str(mat.get("category", "Consumables")).capitalize()
            r_row.cells[4].text = str(q)
            r_row.cells[5].text = f"${c:,.2f}"
            r_row.cells[6].text = f"${sub:,.2f}"
            if idx % 2 == 0:
                for c_idx in range(7):
                    _set_cell_background(r_row.cells[c_idx], "F7FAFC")

        # Total Row
        r_tot = mat_table.rows[-1]
        r_tot.cells[0].text = "TOTAL FUNDING REQUESTED"
        r_tot.cells[1].text = "—"
        r_tot.cells[2].text = "—"
        r_tot.cells[3].text = "—"
        r_tot.cells[4].text = "—"
        r_tot.cells[5].text = "—"
        r_tot.cells[6].text = f"${grand_total:,.2f}"
        for c_idx in range(7):
            _set_cell_background(r_tot.cells[c_idx], "FEF3C7")
            if len(r_tot.cells[c_idx].paragraphs[0].runs) > 0:
                r_tot.cells[c_idx].paragraphs[0].runs[0].font.bold = True
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    elif data.get("budget_items"):
        bi = data.get("budget_items", {})
        bi_table = doc.add_table(rows=6, cols=2)
        bi_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        bi_table.rows[0].cells[0].text = "Budget Category"
        bi_table.rows[0].cells[1].text = "Allocation ($)"
        _set_cell_background(bi_table.rows[0].cells[0], "1A365D")
        _set_cell_background(bi_table.rows[0].cells[1], "1A365D")
        bi_table.rows[0].cells[0].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        bi_table.rows[0].cells[1].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cats = [
            ("1. Consumables & Reagents", bi.get("consumables", 0)),
            ("2. Personnel Incentives", bi.get("personnel", 0)),
            ("3. Utilities & Overhead", bi.get("utilities", 0)),
            ("4. Specialized Equipment", bi.get("equipment", 0))
        ]
        tot = 0.0
        for idx, (c_name, c_amt) in enumerate(cats, 1):
            amt = float(c_amt)
            tot += amt
            bi_table.rows[idx].cells[0].text = c_name
            bi_table.rows[idx].cells[1].text = f"${amt:,.2f}"
        bi_table.rows[5].cells[0].text = "TOTAL REQUESTED"
        bi_table.rows[5].cells[1].text = f"${tot:,.2f}"
        _set_cell_background(bi_table.rows[5].cells[0], "FEF3C7")
        _set_cell_background(bi_table.rows[5].cells[1], "FEF3C7")
        bi_table.rows[5].cells[0].paragraphs[0].runs[0].font.bold = True
        bi_table.rows[5].cells[1].paragraphs[0].runs[0].font.bold = True
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    if data.get("budget"):
        bp = doc.add_paragraph()
        bp.add_run("Budget Justification Notes:\n").bold = True
        bp.add_run(data.get("budget"))
        bp.paragraph_format.space_after = Pt(10)

    # References
    doc.add_heading("8. Literature References (Rubric: 5%)", level=2)
    rp = doc.add_paragraph()
    rp.add_run(data.get("references", "[No references submitted]"))

    # Audit Scorecard Appendix
    if audit_results:
        doc.add_page_break()
        doc.add_heading("III. Faculty Socratic Audit Scorecard", level=1)
        raw = audit_results.get("raw_total", 0)
        gpa = audit_results.get("gpa_score", 0)
        
        score_p = doc.add_paragraph()
        s_run = score_p.add_run(f"Cumulative Score: {raw} / 85.0 Raw Marks  ➔  Estimated GPA: {gpa} / 10.0\n")
        s_run.bold = True
        s_run.font.size = Pt(13)
        s_run.font.color.rgb = RGBColor(197, 48, 48)

    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return output
