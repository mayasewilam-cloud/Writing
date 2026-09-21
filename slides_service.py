"""
PowerPoint Defense Slide Deck Generator for BT_301.
Utilizes python-pptx to generate a professional 16:9 widescreen presentation
for the Week 10 Mock Review Panel / Viva Voce and Oral Defense.
"""

import io
from typing import Dict, Any
from datetime import datetime
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor


# Professional Academic Palette
NAVY_DEEP = RGBColor(15, 23, 42)     # #0F172A
BLUE_ACCENT = RGBColor(37, 99, 235)  # #2563EB
SLATE_TEXT = RGBColor(71, 85, 105)   # #475569
WHITE = RGBColor(255, 255, 255)
GOLD_ACCENT = RGBColor(217, 119, 6)  # #D97706
BG_LIGHT = RGBColor(248, 250, 252)   # #F8FAFC


def _apply_card_background(shape, fill_color):
    """Sets shape solid fill color."""
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.color.rgb = RGBColor(226, 232, 240)


def create_defense_presentation(data: Dict[str, Any], audit: Dict[str, Any] = None) -> io.BytesIO:
    """
    Builds a 16:9 widescreen slide deck using python-pptx.
    """
    prs = Presentation()
    prs.core_properties.author = "Maya Abdelrazek & Youssef Aboulkheir"
    prs.core_properties.comments = "BioWriter Studio Defense Deck. Designed by Maya Abdelrazek & Youssef Aboulkheir."
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    title_text = data.get("title") or "Untitled Biotechnology Research Grant Proposal"
    student_name = data.get("student_name") or "BT_301 Principal Investigator"
    funnel = data.get("funnel", {})
    aims = data.get("aims", {})
    swot = data.get("swot", {})
    pestel = data.get("pestel", {})

    def add_header(slide, section_tag: str, main_title: str):
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        p_tag = tf.paragraphs[0]
        p_tag.text = section_tag.upper()
        p_tag.font.size = Pt(11)
        p_tag.font.bold = True
        p_tag.font.color.rgb = BLUE_ACCENT

        p_main = tf.add_paragraph()
        p_main.text = main_title
        p_main.font.size = Pt(22)
        p_main.font.bold = True
        p_main.font.color.rgb = NAVY_DEEP

        # Watermark footer on content slides
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(6.85), Inches(11.7), Inches(0.4))
        ftf = footer_box.text_frame
        ftf.word_wrap = True
        fp = ftf.paragraphs[0]
        fp.text = "BioWriter Studio | Academic Architects & IP: Maya Abdelrazek & Youssef Aboulkheir"
        fp.font.size = Pt(9)
        fp.font.italic = True
        fp.font.color.rgb = RGBColor(148, 163, 184)

    # -------------------------------------------------------------
    # SLIDE 1: Title Slide
    # -------------------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY_DEEP
    bg1.line.color.rgb = NAVY_DEEP

    tbox1 = slide1.shapes.add_textbox(Inches(1.2), Inches(1.6), Inches(11.0), Inches(4.2))
    tf1 = tbox1.text_frame
    tf1.word_wrap = True

    p_sub1 = tf1.paragraphs[0]
    p_sub1.text = "BT_301: SCIENTIFIC RESEARCH GRANT PROPOSAL DEFENSE"
    p_sub1.font.size = Pt(13)
    p_sub1.font.bold = True
    p_sub1.font.color.rgb = GOLD_ACCENT

    p_title1 = tf1.add_paragraph()
    p_title1.text = title_text
    p_title1.font.size = Pt(28)
    p_title1.font.bold = True
    p_title1.font.color.rgb = WHITE

    p_meta1 = tf1.add_paragraph()
    p_meta1.text = (
        f"\nPrincipal Investigator(s): {student_name}\n"
        f"Target Agency Benchmark: STDF / ICGEB Format | Date: {datetime.now().strftime('%B %Y')}\n"
        f"Academic Framework Architects: Maya Abdelrazek & Youssef Aboulkheir"
    )
    p_meta1.font.size = Pt(12)
    p_meta1.font.color.rgb = RGBColor(203, 213, 225)

    # -------------------------------------------------------------
    # SLIDE 2: Problem Significance & Epidemiological Burden
    # -------------------------------------------------------------
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "1. Background & Significance", "Global & National Burden of the Target Problem")
    card2 = slide2.shapes.add_shape(1, Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.0))
    _apply_card_background(card2, BG_LIGHT)
    tf2 = card2.text_frame
    tf2.word_wrap = True
    p2_1 = tf2.paragraphs[0]
    p2_1.text = "The Quantified Challenge:"
    p2_1.font.size = Pt(16)
    p2_1.font.bold = True
    p2_1.font.color.rgb = NAVY_DEEP
    p2_2 = tf2.add_paragraph()
    p2_2.text = funnel.get("tier1") or "Detail the global or national burden with specific statistics, annual tonnage, mortality, or economic costs."
    p2_2.font.size = Pt(14)
    p2_2.font.color.rgb = SLATE_TEXT

    # -------------------------------------------------------------
    # SLIDE 3: Current Scientific Benchmark & Baseline
    # -------------------------------------------------------------
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "2. Literature Review", "Current Scientific Benchmark & Methodological Baselines")
    card3 = slide3.shapes.add_shape(1, Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.0))
    _apply_card_background(card3, BG_LIGHT)
    tf3 = card3.text_frame
    tf3.word_wrap = True
    p3_1 = tf3.paragraphs[0]
    p3_1.text = "Existing Golden Standards & Empirical Performance:"
    p3_1.font.size = Pt(16)
    p3_1.font.bold = True
    p3_1.font.color.rgb = NAVY_DEEP
    p3_2 = tf3.add_paragraph()
    p3_2.text = funnel.get("tier2") or "Summarize the primary methods currently utilized in industry or clinics and their baseline yield/kinetics."
    p3_2.font.size = Pt(14)
    p3_2.font.color.rgb = SLATE_TEXT

    # -------------------------------------------------------------
    # SLIDE 4: Critical Knowledge Gap & Bottleneck
    # -------------------------------------------------------------
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "3. The Rationale", "The Unresolved Scientific Bottleneck & Knowledge Gap")
    card4 = slide4.shapes.add_shape(1, Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.0))
    _apply_card_background(card4, RGBColor(254, 242, 242)) # Soft red
    card4.line.color.rgb = RGBColor(252, 165, 165)
    tf4 = card4.text_frame
    tf4.word_wrap = True
    p4_1 = tf4.paragraphs[0]
    p4_1.text = "Why Conventional Solutions Fail (The Mechanistic Flaw):"
    p4_1.font.size = Pt(16)
    p4_1.font.bold = True
    p4_1.font.color.rgb = RGBColor(185, 28, 28)
    p4_2 = tf4.add_paragraph()
    p4_2.text = funnel.get("tier3") or "State the exact biophysical failure mode (e.g. low thermal unfolding Tm, off-target cleavage, product inhibition)."
    p4_2.font.size = Pt(14)
    p4_2.font.color.rgb = SLATE_TEXT

    # -------------------------------------------------------------
    # SLIDE 5: Primary Project Aim & Mechanistic Hypothesis
    # -------------------------------------------------------------
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "4. Central Rationale", "Primary Project Aim & Mechanistic Hypothesis")
    card5 = slide5.shapes.add_shape(1, Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.0))
    _apply_card_background(card5, RGBColor(240, 253, 244)) # Soft green
    card5.line.color.rgb = RGBColor(134, 239, 172)
    tf5 = card5.text_frame
    tf5.word_wrap = True
    p5_1 = tf5.paragraphs[0]
    p5_1.text = "Central Scientific Hypothesis:"
    p5_1.font.size = Pt(16)
    p5_1.font.bold = True
    p5_1.font.color.rgb = RGBColor(21, 128, 61)
    p5_2 = tf5.add_paragraph()
    p5_2.text = (data.get("overarching_aim") or funnel.get("tier4")) or "We hypothesize that introducing [engineered mechanism] will overcome [bottleneck] because..."
    p5_2.font.size = Pt(14)
    p5_2.font.color.rgb = SLATE_TEXT

    # -------------------------------------------------------------
    # SLIDE 6: Specific Objectives (Aims 1, 2, 3)
    # -------------------------------------------------------------
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "5. Project Execution", "The 3 Specific Objectives & Quantitative Milestones")
    for i, aim_key in enumerate(["aim1", "aim2", "aim3"], 1):
        box_w = Inches(3.6)
        box_x = Inches(0.8 + (i - 1) * 4.0)
        card_aim = slide6.shapes.add_shape(1, box_x, Inches(1.6), box_w, Inches(5.0))
        _apply_card_background(card_aim, BG_LIGHT)
        tf_aim = card_aim.text_frame
        tf_aim.word_wrap = True
        p_h = tf_aim.paragraphs[0]
        p_h.text = f"Objective {i}"
        p_h.font.size = Pt(16)
        p_h.font.bold = True
        p_h.font.color.rgb = BLUE_ACCENT
        p_b = tf_aim.add_paragraph()
        p_b.text = aims.get(aim_key) or f"Specific Objective {i} work package and milestone threshold."
        p_b.font.size = Pt(12.5)
        p_b.font.color.rgb = SLATE_TEXT

    # -------------------------------------------------------------
    # SLIDE 7: Methodology & Experimental Controls
    # -------------------------------------------------------------
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "6. Experimental Plan", "Methodology, Assays & Essential Controls")
    card7 = slide7.shapes.add_shape(1, Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.0))
    _apply_card_background(card7, BG_LIGHT)
    tf7 = card7.text_frame
    tf7.word_wrap = True
    p7_1 = tf7.paragraphs[0]
    p7_1.text = "Experimental Work Packages & Controls:"
    p7_1.font.size = Pt(16)
    p7_1.font.bold = True
    p7_1.font.color.rgb = NAVY_DEEP
    p7_2 = tf7.add_paragraph()
    p7_2.text = data.get("methodology") or "Detail the experimental protocols (future tense), analytical assays, and positive/negative controls."
    p7_2.font.size = Pt(13.5)
    p7_2.font.color.rgb = SLATE_TEXT

    # -------------------------------------------------------------
    # SLIDE 8: Expected Deliverables & Visual Figures
    # -------------------------------------------------------------
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "7. Expected Outcomes", "Target Deliverables & Conceptual Figure Concepts")
    card8 = slide8.shapes.add_shape(1, Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.0))
    _apply_card_background(card8, BG_LIGHT)
    tf8 = card8.text_frame
    tf8.word_wrap = True
    p8_1 = tf8.paragraphs[0]
    p8_1.text = "Anticipated Results & Key Visual Figures:"
    p8_1.font.size = Pt(16)
    p8_1.font.bold = True
    p8_1.font.color.rgb = NAVY_DEEP
    p8_2 = tf8.add_paragraph()
    p8_2.text = data.get("expected_outcomes") or "Figure 1: Vector construct schematic & SDS-PAGE gel.\nFigure 2: Kinetic degradation curve vs wild-type."
    p8_2.font.size = Pt(14)
    p8_2.font.color.rgb = SLATE_TEXT

    # -------------------------------------------------------------
    # SLIDE 8B: Section 10: Expected Impact ("Why Results Matter")
    # -------------------------------------------------------------
    slide_imp = prs.slides.add_slide(blank_layout)
    add_header(slide_imp, "8. Expected Impact", "Why Do The Results Matter? (Academic, Economic & Societal)")
    card_imp = slide_imp.shapes.add_shape(1, Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.0))
    _apply_card_background(card_imp, RGBColor(240, 253, 244)) # Soft green
    card_imp.line.color.rgb = RGBColor(134, 239, 172)
    tf_imp = card_imp.text_frame
    tf_imp.word_wrap = True
    p_imp1 = tf_imp.paragraphs[0]
    p_imp1.text = "The 3-Tier Long-Term Impact Framework:"
    p_imp1.font.size = Pt(16)
    p_imp1.font.bold = True
    p_imp1.font.color.rgb = RGBColor(21, 128, 61)
    p_imp2 = tf_imp.add_paragraph()
    p_imp2.text = data.get("impact") or (
        "• Academic & Fundamental Impact: Unravels structural mechanisms and establishes open-access kinetic datasets.\n"
        "• Economic & Translational Impact: Reduces bioprocess costs by >40% and provides patentable IP for industrial partners.\n"
        "• Societal & Environmental Impact: Clears tons of environmental pollutants and directly aligns with Egypt Vision 2030 & UN SDGs."
    )
    p_imp2.font.size = Pt(14)
    p_imp2.font.color.rgb = SLATE_TEXT

    # -------------------------------------------------------------
    # SLIDE 8C: Competitor Landscape & Unique Selling Proposition (USP)
    # -------------------------------------------------------------
    slide_comp = prs.slides.add_slide(blank_layout)
    add_header(slide_comp, "9. Competitive Advantage", "Competitor Landscape Analysis & Unique Selling Proposition")
    card_comp = slide_comp.shapes.add_shape(1, Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.0))
    _apply_card_background(card_comp, BG_LIGHT)
    tf_comp = card_comp.text_frame
    tf_comp.word_wrap = True
    p_comp1 = tf_comp.paragraphs[0]
    p_comp1.text = "Competitor Comparison Matrix:"
    p_comp1.font.size = Pt(16)
    p_comp1.font.bold = True
    p_comp1.font.color.rgb = BLUE_ACCENT
    
    comp_obj = data.get("competitor_data", {})
    inc_name = comp_obj.get("incumbent_name", "Standard Commercial Incumbent")
    emg_name = comp_obj.get("emerging_name", "Academic Peer Technology")
    p_comp2 = tf_comp.add_paragraph()
    p_comp2.text = (
        f"• Current Standard ({inc_name}): Constrained by high cost, centralized machinery, and 24-48h turnaround.\n"
        f"• Emerging Alternative ({emg_name}): Offers moderate improvements but suffers from low stability or regulatory hurdles.\n"
        f"• Proposed Innovation: Combines engineered molecular tools to deliver high throughput at low unit cost.\n\n"
        f"Unique Selling Proposition (USP):\n{data.get('usps') or 'Unlike existing commercial benchmarks, our platform delivers 4-fold higher catalytic activity under ambient conditions, cutting operational expenditures by 60%.'}"
    )
    p_comp2.font.size = Pt(13)
    p_comp2.font.color.rgb = SLATE_TEXT
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "8. Risk Management", "Biotechnology SWOT Analysis (Anticipating Biological Failure)")
    swot_boxes = [
        ("Strengths", swot.get("strengths", "N/A"), Inches(0.8), Inches(1.6), RGBColor(240, 253, 244)),
        ("Weaknesses (Biochemical)", swot.get("weaknesses", "N/A"), Inches(6.8), Inches(1.6), RGBColor(254, 242, 242)),
        ("Opportunities", swot.get("opportunities", "N/A"), Inches(0.8), Inches(4.2), RGBColor(239, 246, 255)),
        ("Threats (Biological/Market)", swot.get("threats", "N/A"), Inches(6.8), Inches(4.2), RGBColor(255, 251, 235))
    ]
    for stitle, stext, bx, by, bcolor in swot_boxes:
        c_shape = slide9.shapes.add_shape(1, bx, by, Inches(5.7), Inches(2.4))
        _apply_card_background(c_shape, bcolor)
        tf_sw = c_shape.text_frame
        tf_sw.word_wrap = True
        psw1 = tf_sw.paragraphs[0]
        psw1.text = stitle
        psw1.font.size = Pt(14)
        psw1.font.bold = True
        psw1.font.color.rgb = NAVY_DEEP
        psw2 = tf_sw.add_paragraph()
        psw2.text = stext
        psw2.font.size = Pt(12)
        psw2.font.color.rgb = SLATE_TEXT

    # -------------------------------------------------------------
    # SLIDE 10: Timeline & Budget Breakdown
    # -------------------------------------------------------------
    slide10 = prs.slides.add_slide(blank_layout)
    add_header(slide10, "9. Feasibility", "Time Plan (Go/No-Go Gates) & Tabulated Budget")
    card10_1 = slide10.shapes.add_shape(1, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.0))
    _apply_card_background(card10_1, BG_LIGHT)
    tf10_1 = card10_1.text_frame
    tf10_1.word_wrap = True
    p10_1 = tf10_1.paragraphs[0]
    p10_1.text = "Gantt Timeline & Decision Gates:"
    p10_1.font.size = Pt(16)
    p10_1.font.bold = True
    p10_1.font.color.rgb = NAVY_DEEP
    p10_2 = tf10_1.add_paragraph()
    p10_2.text = data.get("time_plan") or "Months 1-6: Synthesis & cloning [Go/No-Go Gate: expression confirmed]\nMonths 7-12: Characterization\nMonths 13-18: Translational trial"
    p10_2.font.size = Pt(13)
    p10_2.font.color.rgb = SLATE_TEXT

    card10_2 = slide10.shapes.add_shape(1, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.0))
    _apply_card_background(card10_2, BG_LIGHT)
    tf10_2 = card10_2.text_frame
    tf10_2.word_wrap = True
    p10_3 = tf10_2.paragraphs[0]
    p10_3.text = "Tabulated Budget Breakdown:"
    p10_3.font.size = Pt(16)
    p10_3.font.bold = True
    p10_3.font.color.rgb = NAVY_DEEP
    p10_4 = tf10_2.add_paragraph()
    p10_4.text = data.get("budget") or "1. Consumables\n2. Personnel\n3. Utilities/Overhead\n4. Equipment\nTotal requested funds with justification."
    p10_4.font.size = Pt(13)
    p10_4.font.color.rgb = SLATE_TEXT

    # -------------------------------------------------------------
    # SLIDE 11: Oral Defense (Viva Voce) Anticipated Questions
    # -------------------------------------------------------------
    slide11 = prs.slides.add_slide(blank_layout)
    add_header(slide11, "10. Defense Preparation", "Anticipated Study Section Cross-Examination Inquiries")
    card11 = slide11.shapes.add_shape(1, Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.0))
    _apply_card_background(card11, RGBColor(253, 244, 255))
    card11.line.color.rgb = RGBColor(240, 171, 252)
    tf11 = card11.text_frame
    tf11.word_wrap = True
    p11_1 = tf11.paragraphs[0]
    p11_1.text = "Key Questions to Defend in Mock Review Panel:"
    p11_1.font.size = Pt(16)
    p11_1.font.bold = True
    p11_1.font.color.rgb = RGBColor(134, 25, 143)
    p11_2 = tf11.add_paragraph()
    p11_2.text = (
        "1. Experimental Model Justification: Why this host/system over standard lab controls?\n"
        "2. Technical Contingency (ACP Technique): How will you rescue inclusion bodies or low yield?\n"
        "3. Milestone Independence: Does Objective 2 survive if Objective 1 experiences biological delays?\n"
        "4. Regulatory Realism: What biosafety, containment, or ethical approvals govern translation?"
    )
    p11_2.font.size = Pt(13.5)
    p11_2.font.color.rgb = SLATE_TEXT

    output = io.BytesIO()
    prs.save(output)
    output.seek(0)
    return output
