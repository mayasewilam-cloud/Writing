"""
Rubric & Heuristic Auditing Engine for BT_301 Research Proposals.
Supports cellular hosts, cell-free diagnostics, nanotechnology, and environmental matrices.
Evaluates student proposals against the 11-point rubric (85 raw marks -> 10 GPA).
"""

import re
from typing import Dict, List, Any
from core.impact_novelty_engine import (
    audit_gap_statement,
    audit_novelty_and_soundness,
    audit_competitor_matrix_and_usp
)


def audit_title(title: str, system: str = "", tool: str = "", chassis: str = "") -> Dict[str, Any]:
    """
    Rubric Item 1: Title (2% All or None).
    Must describe molecular mechanism, experimental system/matrix, target metric, and application.
    """
    system = system or chassis
    title_clean = title.strip()
    words = title_clean.split()
    word_count = len(words)
    
    issues = []
    strengths = []
    awarded_marks = 0.0

    if not title_clean:
        return {
            "score": 0.0,
            "max": 2.0,
            "passed": False,
            "issues": ["Title is empty."],
            "strengths": [],
            "feedback": "A proposal title is evaluated as All-or-None (0% vs 2%). Provide a complete descriptive scientific title."
        }

    if word_count < 6:
        issues.append(f"Title is too brief ({word_count} words). Academic grant titles typically contain 12-24 words.")
    elif word_count > 32:
        issues.append(f"Title is overly lengthy ({word_count} words). Aim for under 28 words.")
    else:
        strengths.append(f"Appropriate academic length ({word_count} words).")

    # Cliché check
    vague_patterns = [r"^study of\b", r"^a study on\b", r"^research on\b", r"^investigation into\b"]
    for pat in vague_patterns:
        if re.search(pat, title_clean, re.IGNORECASE):
            issues.append(f"Avoid colloquial academic fillers like '{re.search(pat, title_clean, re.IGNORECASE).group(0)}'. Lead directly with the molecular mechanism or technology.")

    # Experimental System / Model / Chassis check
    system_found = False
    if system and system.lower() in title_clean.lower():
        system_found = True
        strengths.append(f"Experimental system/model explicitly named ('{system}').")
    elif any(term in title_clean.lower() for term in [
        "coli", "pastoris", "putida", "aestivum", "arabidopsis", "human", "murine",
        "isolates", "yeast", "plant", "bacterium", "nanoparticle", "cell-free",
        "biosensor", "hydrogel", "liposome", "effluent", "wastewater", "clea", "in silico", "membrane"
    ]):
        system_found = True
        strengths.append("Experimental system, host, or diagnostic matrix recognized in title.")
    else:
        issues.append("Experimental system, host organism, or delivery matrix is missing. Reviewers need to know your experimental model immediately.")

    # Tool / mechanism check
    tool_found = False
    if tool and tool.lower() in title_clean.lower():
        tool_found = True
        strengths.append(f"Molecular tool or mechanism explicitly named ('{tool}').")
    elif any(term in title_clean.lower() for term in [
        "crispr", "cas12", "cas9", "base edit", "petase", "promoter", "recombinant",
        "enzyme", "sirna", "aptamer", "biosensor", "hydrolase", "isothermal", "laccase", "clea", "scaffold"
    ]):
        tool_found = True
        strengths.append("Molecular mechanism, enzyme, or molecular intervention recognized.")
    else:
        issues.append("Specific molecular tool, enzyme, or intervention is missing.")

    # Metric / Outcome check
    metric_found = False
    metric_indicators = ["enhance", "elevate", "reduce", "degrade", "yield", "tolerance", "detection", "limit of", "rate", "efficiency", "resistance", "inhibition", "clearing", "removal"]
    if any(ind in title_clean.lower() for ind in metric_indicators):
        metric_found = True
        strengths.append("Target functional outcome or performance metric specified.")
    else:
        issues.append("Target functional outcome or metric is missing (e.g. 'to enhance foliar salinity tolerance' or 'for rapid femtomolar detection').")

    # All or None scoring rule
    if system_found and tool_found and metric_found and word_count >= 8:
        awarded_marks = 2.0
        passed = True
        feedback = "Title conforms to standard grant formula ([Mechanism] in [Experimental System] to [Target Metric] for [Application])."
    else:
        awarded_marks = 0.0
        passed = False
        feedback = "0% Awarded (All or None Rule). The title must explicitly name the molecular mechanism, experimental system/matrix, and quantifiable objective."

    return {
        "score": awarded_marks,
        "max": 2.0,
        "passed": passed,
        "issues": issues,
        "strengths": strengths,
        "feedback": feedback
    }


def audit_abstract(abstract: str) -> Dict[str, Any]:
    """
    Rubric Item 2: Abstract (5% Scaled).
    Strict 250-word ceiling.
    Balances Problem (2%), Methodology (2%), Expected Outcomes (1%).
    """
    abstract_clean = abstract.strip()
    words = abstract_clean.split()
    word_count = len(words)
    
    issues = []
    strengths = []

    if not abstract_clean:
        return {
            "score": 0.0,
            "max": 5.0,
            "word_count": 0,
            "issues": ["Abstract is empty."],
            "strengths": [],
            "feedback": "Abstract required (250-word maximum)."
        }

    penalty = 0.0
    if word_count > 250:
        penalty = min(2.0, (word_count - 250) * 0.05)
        issues.append(f"Abstract exceeds the 250-word ceiling ({word_count} words). Shorten by {word_count - 250} words.")
    elif word_count < 90:
        penalty = 1.5
        issues.append(f"Abstract is too brief ({word_count} words). Standard grant abstracts require 180-240 words.")
    else:
        strengths.append(f"Word count ({word_count} words) conforms to the 250-word limit.")

    # 1. Problem / burden keywords (2%)
    problem_kw = ["crisis", "challenge", "burden", "mortality", "economic", "resistance", "loss", "prevalence", "cases", "million", "billion", "contaminat", "pathogen", "threat", "pollution"]
    problem_hits = sum(1 for kw in problem_kw if kw in abstract_clean.lower())
    problem_score = 2.0 if problem_hits >= 2 else (1.0 if problem_hits == 1 else 0.5)

    # 2. Methodology keywords (2%)
    method_kw = ["will be", "cloned", "expressed", "assay", "construct", "screen", "transform", "measure", "quantif", "spectrophotometr", "pcr", "crispr", "sequenc", "engineer", "culture", "synthes", "formulat", "carrier", "sensor"]
    method_hits = sum(1 for kw in method_kw if kw in abstract_clean.lower())
    method_score = 2.0 if method_hits >= 2 else (1.0 if method_hits == 1 else 0.5)

    # 3. Expected outcomes & significance (1%)
    outcome_kw = ["expect", "anticipate", "milestone", "achieve", "yield", "fold", "improve", "benchmark", "provide a scalable", "enable", "demonstrate"]
    outcome_hits = sum(1 for kw in outcome_kw if kw in abstract_clean.lower())
    outcome_score = 1.0 if outcome_hits >= 1 else 0.0

    raw = problem_score + method_score + outcome_score - penalty
    score = round(max(0.0, min(5.0, raw)), 1)

    return {
        "score": score,
        "max": 5.0,
        "word_count": word_count,
        "issues": issues,
        "strengths": strengths,
        "feedback": f"Structured Abstract scored {score}/5.0 (Word count: {word_count})."
    }


def audit_funnel_background(tier1: str, tier2: str, tier3: str, tier4: str) -> Dict[str, Any]:
    """
    Rubric Item 3: Background & Funnel (20% Scaled).
    Tier 1: Problem Significance & Epidemiological Burden (5%)
    Tier 2: Current Scientific Benchmark & Methodological Baselines (5%)
    Tier 3: Critical Scientific Knowledge Gap & Mechanistic Flaw (5%)
    Tier 4: Primary Project Aim, Mechanistic Hypothesis & Objectives (5%)
    """
    tier_reports = []

    # Tier 1 Audit: Burden (5%)
    t1_score = 0.0
    t1_issues = []
    t1_strengths = []
    if not tier1.strip():
        t1_issues.append("Tier 1 is missing.")
    else:
        has_number = bool(re.search(r"\b\d+(\.\d+)?\b", tier1))
        has_citation = bool(re.search(r"\[[0-9,\s-]+\]|\([A-Za-z]+(?:\s+et\s+al\.)?,\s*\d{4}\)", tier1))
        if has_number:
            t1_score += 2.5
            t1_strengths.append("Contains quantified burden metric (statistics, percentages, or monetary metrics).")
        else:
            t1_issues.append("Missing an empirical quantified statistic (e.g. annual metric tons, incidence rate, financial cost).")
        if has_citation:
            t1_score += 1.5
            t1_strengths.append("Includes literature citation.")
        else:
            t1_issues.append("Missing peer-reviewed citation for the problem burden statement.")
        if len(tier1.split()) >= 20:
            t1_score += 1.0
    t1_score = min(5.0, t1_score)
    tier_reports.append({"tier": 1, "name": "Epidemiological & Global Burden", "score": t1_score, "max": 5.0, "issues": t1_issues, "strengths": t1_strengths})

    # Tier 2 Audit: Current Literature & Baseline (5%)
    t2_score = 0.0
    t2_issues = []
    t2_strengths = []
    if not tier2.strip():
        t2_issues.append("Tier 2 is missing.")
    else:
        has_current_terms = any(term in tier2.lower() for term in ["conventional", "currently", "standard", "traditionally", "existing", "rely on", "developed by", "gold standard"])
        has_citation = bool(re.search(r"\[[0-9,\s-]+\]|\([A-Za-z]+(?:\s+et\s+al\.)?,\s*\d{4}\)", tier2))
        if has_current_terms:
            t2_score += 2.5
            t2_strengths.append("Documents current scientific benchmark methodology.")
        else:
            t2_issues.append("Clearly state existing baseline solutions or what current standard protocols achieve.")
        if has_citation:
            t2_score += 1.5
            t2_strengths.append("Cites primary literature.")
        else:
            t2_issues.append("Missing citation for current scientific benchmark.")
        if len(tier2.split()) >= 20:
            t2_score += 1.0
    t2_score = min(5.0, t2_score)
    tier_reports.append({"tier": 2, "name": "Current Scientific Benchmark & Baseline", "score": t2_score, "max": 5.0, "issues": t2_issues, "strengths": t2_strengths})

    # Tier 3 Audit: Knowledge Gap & Flaw (5%)
    t3_score = 0.0
    t3_issues = []
    t3_strengths = []
    if not tier3.strip():
        t3_issues.append("Tier 3 is missing.")
    else:
        gap_words = ["however", "nevertheless", "yet", "critically constrained", "remains limited", "fails to", "bottleneck", "lack", "inability", "drawback", "limitation", "shortcoming"]
        has_gap = any(gw in tier3.lower() for gw in gap_words)
        if has_gap:
            t3_score += 3.0
            t3_strengths.append("Uses effective disjunctive transition signaling the scientific bottleneck ('However...').")
        else:
            t3_issues.append("Missing an explicit knowledge gap transition (use 'However, widespread deployment remains limited by...').")
        if len(tier3.split()) >= 20:
            t3_score += 2.0
    t3_score = min(5.0, t3_score)
    tier_reports.append({"tier": 3, "name": "Scientific Knowledge Gap & Bottleneck", "score": t3_score, "max": 5.0, "issues": t3_issues, "strengths": t3_strengths})

    # Tier 4 Audit: Primary Aim & Hypothesis (5%)
    t4_score = 0.0
    t4_issues = []
    t4_strengths = []
    if not tier4.strip():
        t4_issues.append("Tier 4 is missing.")
    else:
        has_hypothesis = "hypothes" in tier4.lower() or "aim" in tier4.lower() or "propose" in tier4.lower() or "objective" in tier4.lower()
        has_mechanistic_link = any(ml in tier4.lower() for ml in ["because", "by introducing", "through", "via", "mediated by", "driven by"])
        if has_hypothesis:
            t4_score += 2.5
            t4_strengths.append("States project hypothesis / primary objective.")
        else:
            t4_issues.append("Clearly state your primary project hypothesis.")
        if has_mechanistic_link:
            t4_score += 2.5
            t4_strengths.append("Provides explicit mechanistic rationale.")
        else:
            t4_issues.append("Include explicit mechanistic rationale ('because...' or 'via [mechanism]...').")
    t4_score = min(5.0, t4_score)
    tier_reports.append({"tier": 4, "name": "Project Hypothesis & Primary Objectives", "score": t4_score, "max": 5.0, "issues": t4_issues, "strengths": t4_strengths})

    total_score = sum(r["score"] for r in tier_reports)
    return {
        "score": round(total_score, 1),
        "max": 20.0,
        "tiers": tier_reports,
        "feedback": f"Background Funnel scored {round(total_score, 1)}/20.0."
    }


def audit_aims_independence(aim1: str, aim2: str, aim3: str) -> Dict[str, Any]:
    """
    Audits the 3 Specific Objectives (Specific Aims) against the Domino Collapse Trap.
    Objective 2 must not depend completely on Objective 1 achieving 100% success.
    """
    aims = [("Specific Objective 1", aim1.strip()), ("Specific Objective 2", aim2.strip()), ("Specific Objective 3", aim3.strip())]
    issues = []
    strengths = []

    populated = [a for a in aims if a[1]]
    if len(populated) < 3:
        issues.append(f"Only {len(populated)} of 3 Specific Objectives provided. Standard grant proposals require 3 distinct objectives.")
        return {
            "score": len(populated) * 1.5,
            "max": 5.0,
            "issues": issues,
            "strengths": strengths,
            "feedback": "Provide all 3 Specific Objectives."
        }

    domino_phrases = ["if aim 1 works", "following successful completion of aim 1", "pending positive results in aim 1", "if objective 1 succeeds", "if successful"]
    has_domino = False
    for name, content in aims[1:]:
        for dp in domino_phrases:
            if dp in content.lower():
                has_domino = True
                issues.append(f"DOMINO COLLAPSE RISK in {name}: Found conditional dependency ('{dp}'). If Objective 1 experiences technical delays, {name} collapses. Provide an active parallel baseline.")

    if not has_domino:
        strengths.append("Objectives exhibit parallel, decoupled feasibility (passes the Domino Collapse Test).")

    milestones_count = 0
    for name, content in aims:
        has_milestone = any(kw in content.lower() for kw in ["milestone", "benchmark", "threshold", "yield", "≥", ">", "<", "%", "kd", "od", "u/mg", "mg/l", "lod", "nm", "fold"])
        if has_milestone:
            milestones_count += 1
            strengths.append(f"{name} specifies a measurable Go/No-Go milestone.")
        else:
            issues.append(f"{name} lacks a quantitative Go/No-Go milestone.")

    raw_score = 2.0 + (1.0 if not has_domino else 0.0) + (milestones_count * 0.66)
    score = round(min(5.0, raw_score), 1)

    return {
        "score": score,
        "max": 5.0,
        "issues": issues,
        "strengths": strengths,
        "has_domino_risk": has_domino,
        "milestones_found": milestones_count,
        "feedback": f"Specific Objectives scored {score}/5.0."
    }


def audit_methodology_tense(methodology: str) -> Dict[str, Any]:
    text = methodology.strip()
    if not text:
        return {
            "score": 0.0,
            "max": 15.0,
            "tense_mark": 0.0,
            "issues": ["Methodology text is empty."],
            "strengths": [],
            "feedback": "Methodology required (15% total marks)."
        }

    issues = []
    strengths = []
    future_markers = len(re.findall(r"\b(will be|shall be|will undergo|will evaluate|will construct|will measure|will quantify|will synthesize|will isolate|will test|will assess|will determine|will compare|will serve)\b", text, re.IGNORECASE))
    past_markers = re.findall(r"\b(was [a-z]+ed|were [a-z]+ed|we [a-z]+ed|was incubated|were inoculated|was performed|were collected|was added|were analyzed|was measured|was observed|were observed|we incubated|we measured|we performed|we analyzed|we observed|we tested|we collected|we cultured)\b", text, re.IGNORECASE)
    past_count = len(past_markers)

    if future_markers >= 2 and past_count == 0:
        strengths.append(f"Adheres to future tense ({future_markers} future tense auxiliary verbs identified).")
        tense_mark = 1.0
    elif future_markers >= 1 and past_count == 0:
        strengths.append("Adheres to future tense (add more 'will be' auxiliary markers to strengthen).")
        tense_mark = 0.8
    elif past_count > 0 and future_markers > past_count:
        tense_mark = 0.5
        issues.append(f"Mixed tense detected. Found {past_count} past-tense phrases (e.g. '{past_markers[0]}'). Proposals describe FUTURE work; change to 'will be...'.")
    elif past_count > 0:
        tense_mark = 0.0
        sample = past_markers[0]
        issues.append(f"Methodology appears to be written in past tense ('{sample}'). Rewrite in future tense ('will be incubated', 'will be assayed').")
    else:
        tense_mark = 0.3
        issues.append("Methodology lacks future-tense auxiliary verbs (e.g. 'will be constructed', 'will be analyzed').")

    has_controls = any(ctrl in text.lower() for ctrl in ["positive control", "negative control", "vehicle control", "mock control", "wild-type", "untransformed", "blank control", "baseline control"])
    if has_controls:
        strengths.append("Experimental controls (positive/negative/vehicle) specified.")
        control_score = 4.0
    else:
        issues.append("Missing explicit positive and negative experimental controls.")
        control_score = 2.0

    assays = any(assay in text.lower() for assay in ["sanger", "pcr", "sds-page", "hplc", "mass spec", "fluorescence", "absorbance", "od600", "elisa", "qpcr", "western blot", "spectrophotometr", "dsc", "tem", "sem", "flow cytometry", "chromatograph", "purif", "sequenc"])
    assay_score = 5.0 if assays else 2.5
    if assays:
        strengths.append("Recognized analytical assays and laboratory instrumentation specified.")

    total_method_score = round(min(15.0, control_score + assay_score + 4.0), 1)

    return {
        "score": total_method_score,
        "max": 15.0,
        "tense_mark": tense_mark,
        "tense_max": 1.0,
        "past_violations": past_markers[:5],
        "issues": issues,
        "strengths": strengths,
        "feedback": f"Methodology scored {total_method_score}/15.0."
    }


def audit_swot_pestel(swot_data: Dict[str, str], pestel_data: Dict[str, str]) -> Dict[str, Any]:
    issues = []
    strengths = []
    swot_score = 0.0

    student_cliches = ["we are students", "lack of experience", "not enough time", "budget might run out", "we are beginners", "limited knowledge"]
    weaknesses = swot_data.get("weaknesses", "").lower()
    threats = swot_data.get("threats", "").lower()

    found_cliche = False
    for cl in student_cliches:
        if cl in weaknesses or cl in threats:
            found_cliche = True
            issues.append(f"Avoid student cliché: '{cl}'. Reviewers expect biochemical/technical failure modes.")

    biotech_failure_modes = ["insolub", "inclusion bod", "off-target", "substrate inhibit", "toxicity", "immunogenicity", "degrade", "protease", "yield", "mutation", "stability", "aggregation", "denaturation", "matrix interference"]
    has_biotech_risk = any(fm in weaknesses or fm in threats for fm in biotech_failure_modes)

    if has_biotech_risk:
        strengths.append("SWOT includes authentic biochemical or technical failure modes.")
        swot_score += 2.5

    quadrants_filled = sum(1 for q in ["strengths", "weaknesses", "opportunities", "threats"] if swot_data.get(q, "").strip())
    swot_score += (quadrants_filled / 4.0) * 2.5
    if found_cliche:
        swot_score = max(1.0, swot_score - 1.5)
    swot_score = round(min(5.0, swot_score), 1)

    letters = ["political", "economic", "social", "technological", "environmental", "legal"]
    filled_letters = sum(1 for l in letters if pestel_data.get(l, "").strip())
    pestel_score = round((filled_letters / 6.0) * 5.0, 1)

    return {
        "score": round(swot_score + pestel_score, 1),
        "max": 10.0,
        "swot_score": swot_score,
        "pestel_score": pestel_score,
        "issues": issues,
        "strengths": strengths,
        "feedback": f"SWOT & PESTEL scored {round(swot_score + pestel_score, 1)}/10.0."
    }


def calculate_full_rubric_audit(proposal_data: Dict[str, Any]) -> Dict[str, Any]:
    system_val = proposal_data.get("system") or proposal_data.get("chassis", "")
    title_res = audit_title(
        proposal_data.get("title", ""),
        system_val,
        proposal_data.get("tool", "")
    )
    abstract_res = audit_abstract(proposal_data.get("abstract", ""))
    
    funnel = proposal_data.get("funnel", {})
    funnel_res = audit_funnel_background(
        funnel.get("tier1", ""),
        funnel.get("tier2", ""),
        funnel.get("tier3", ""),
        funnel.get("tier4", "")
    )
    
    method_res = audit_methodology_tense(proposal_data.get("methodology", ""))
    
    aims = proposal_data.get("aims", {})
    aims_res = audit_aims_independence(
        aims.get("aim1", ""),
        aims.get("aim2", ""),
        aims.get("aim3", "")
    )
    
    swot_res = audit_swot_pestel(
        proposal_data.get("swot", {}),
        proposal_data.get("pestel", {})
    )

    outcomes_text = proposal_data.get("expected_outcomes", "").strip()
    impact_text = proposal_data.get("impact", "").strip()
    # Expected Outcomes & Long-Term Impact (10.0 marks total)
    # Deliverables (5.0) + Section 10 Impact / Why Results Matter (5.0)
    deliverables_score = 5.0 if len(outcomes_text) > 50 else (2.5 if outcomes_text else 0.0)
    impact_score = 5.0 if len(impact_text) > 40 else (2.5 if impact_text or len(outcomes_text) > 100 else 0.0)
    outcomes_total = round(min(10.0, deliverables_score + impact_score), 1)

    # Competitive Advantage & USPs (Phase 9: 5% marks)
    competitor_data = proposal_data.get("competitor_data", {})
    usp_text = proposal_data.get("usps", "")
    competitor_res = audit_competitor_matrix_and_usp(competitor_data, usp_text)
    usps_score = competitor_res["score"]

    # Gap and Novelty diagnostic
    gap_res = audit_gap_statement(funnel.get("tier3", ""))
    novelty_res = audit_novelty_and_soundness(
        title=proposal_data.get("title", ""),
        chassis=system_val,
        tool=proposal_data.get("tool", ""),
        target=proposal_data.get("target", ""),
        hypothesis=funnel.get("tier4", ""),
        methodology=proposal_data.get("methodology", "")
    )

    timeline_text = proposal_data.get("time_plan", "").strip()
    timeline_score = 4.0 if len(timeline_text) > 30 else (2.0 if timeline_text else 0.0)

    budget_text = proposal_data.get("budget", "").strip()
    budget_score = 4.0 if len(budget_text) > 30 else (2.0 if budget_text else 0.0)

    refs = proposal_data.get("references", "")
    refs_count = len(refs.split("\n")) if refs else 0
    refs_score = min(5.0, round(refs_count * 1.0, 1))

    structure_score = 2.0 + method_res.get("tense_mark", 0.0)

    raw_total = (
        title_res["score"] +
        abstract_res["score"] +
        funnel_res["score"] +
        method_res["score"] +
        outcomes_total +
        usps_score +
        swot_res["score"] +
        aims_res["score"] +
        timeline_score +
        budget_score +
        refs_score +
        structure_score
    )
    raw_total = round(min(85.0, max(0.0, raw_total)), 1)
    gpa_score = round((raw_total / 85.0) * 10.0, 2)

    return {
        "raw_total": raw_total,
        "max_raw": 85.0,
        "gpa_score": gpa_score,
        "max_gpa": 10.0,
        "breakdown": {
            "title": {"score": title_res["score"], "max": 2.0, "report": title_res},
            "abstract": {"score": abstract_res["score"], "max": 5.0, "report": abstract_res},
            "background": {"score": funnel_res["score"], "max": 20.0, "report": funnel_res, "gap_audit": gap_res},
            "methodology": {"score": method_res["score"], "max": 15.0, "report": method_res},
            "aims_independence": {"score": aims_res["score"], "max": 5.0, "report": aims_res},
            "swot_pestel": {"score": swot_res["score"], "max": 10.0, "report": swot_res},
            "expected_outcomes": {"score": outcomes_total, "max": 10.0, "impact_included": bool(impact_text)},
            "competitive_advantage": {"score": usps_score, "max": 5.0, "report": competitor_res},
            "novelty_soundness": {"score": novelty_res["soundness_score"], "max": 100.0, "report": novelty_res},
            "time_plan": {"score": timeline_score, "max": 5.0},
            "budget": {"score": budget_score, "max": 5.0},
            "references": {"score": refs_score, "max": 5.0},
            "structure": {"score": structure_score, "max": 3.0}
        }
    }


def audit_all_writing_sections(proposal_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive Writing Audit covering all 9 drafted sections of the proposal:
    1. Title & Research Anchors
    2. Abstract / Executive Summary
    3. Background Funnel Tiers 1-4 (Burden, Current Scientific Benchmark, Knowledge Gap, Hypothesis)
    4. Central Aim & 3 Specific Objectives (Domino Collapse check)
    5. Experimental Methodology (Strict future tense & essential controls)
    6. Expected Outcomes & Long-Term Impact (Academic, Economic, Societal)
    7. Competitor Analysis & Unique Selling Proposition (USP)
    8. Biotech SWOT & Feasibility (Biochemical failure modes)
    9. Peer-Reviewed References & Recency (>=60% 2021-2026)
    """
    sections = []

    # 1. Title & Research Anchors
    title = proposal_data.get("title", "")
    chassis = proposal_data.get("chassis") or proposal_data.get("system", "")
    tool = proposal_data.get("tool", "")
    t_rep = audit_title(title, system=chassis, tool=tool)
    t_status = "pass" if t_rep["passed"] else ("warning" if title.strip() else "incomplete")
    sections.append({
        "id": "sec_title",
        "name": "1. Proposal Title & Research Anchors",
        "status": t_status,
        "badge": "✅ Robust" if t_status == "pass" else ("⚠️ Needs Refinement" if t_status == "warning" else "❌ Incomplete"),
        "excerpt": title if title.strip() else "No title provided yet.",
        "strengths": t_rep.get("strengths", []),
        "issues": t_rep.get("issues", []),
        "action_recommendation": "Ensure title specifies: [Molecular Mechanism] in [Experimental Host/Matrix] to [Target Metric] for [Application]." if t_status != "pass" else "Title conforms to grant and publication guidelines."
    })

    # 2. Abstract
    abstract = proposal_data.get("abstract", "")
    a_rep = audit_abstract(abstract)
    a_status = "pass" if a_rep["score"] >= 3.5 else ("warning" if abstract.strip() else "incomplete")
    sections.append({
        "id": "sec_abstract",
        "name": "2. Abstract / Executive Summary",
        "status": a_status,
        "badge": "✅ Robust" if a_status == "pass" else ("⚠️ Needs Refinement" if a_status == "warning" else "❌ Incomplete"),
        "excerpt": abstract[:160] + "..." if len(abstract) > 160 else (abstract if abstract.strip() else "No abstract provided yet."),
        "strengths": a_rep.get("strengths", []),
        "issues": a_rep.get("issues", []),
        "action_recommendation": f"Target 200–250 words structured into Problem (2%), Methodology (2%), and Expected Quantitative Milestones (1%). Current word count: {a_rep.get('word_count', 0)}."
    })

    # 3. Background Funnel Tiers 1-4
    funnel = proposal_data.get("funnel", {})
    t1 = funnel.get("tier1", "")
    t2 = funnel.get("tier2", "")
    t3 = funnel.get("tier3", "")
    t4 = funnel.get("tier4", "")
    f_rep = audit_funnel_background(t1, t2, t3, t4)
    gap_rep = audit_gap_statement(t3)
    f_status = "pass" if f_rep["score"] >= 14.0 and not gap_rep.get("is_strawman") else ("warning" if any([t1, t2, t3, t4]) else "incomplete")
    all_f_strengths = []
    all_f_issues = []
    for tr in f_rep.get("tiers", []):
        all_f_strengths.extend(tr.get("strengths", []))
        all_f_issues.extend(tr.get("issues", []))
    if gap_rep.get("is_strawman"):
        all_f_issues.append("STRAWMAN GAP DETECTED: Avoid claiming 'no one has ever studied this'. Frame the gap as a documented biophysical, performance, or matrix bottleneck.")
    sections.append({
        "id": "sec_funnel",
        "name": "3. Background Inverted Funnel (Tiers 1–4)",
        "status": f_status,
        "badge": "✅ Robust" if f_status == "pass" else ("⚠️ Needs Refinement" if f_status == "warning" else "❌ Incomplete"),
        "excerpt": f"Tier 1: {t1[:70]}... | Tier 3 Gap: {t3[:70]}..." if (t1 or t3) else "Funnel tiers not drafted yet.",
        "strengths": all_f_strengths[:4],
        "issues": all_f_issues,
        "action_recommendation": "Ensure Tier 1 includes quantified burden statistics, Tier 2 documents baseline yield/rates, Tier 3 identifies the biophysical mechanism of failure, and Tier 4 establishes your testable hypothesis."
    })

    # 4. Central Aim & 3 Specific Objectives
    aims_data = proposal_data.get("aims", {})
    aim_main = aims_data.get("overarching", "")
    aim1 = aims_data.get("aim1", "")
    aim2 = aims_data.get("aim2", "")
    aim3 = aims_data.get("aim3", "")
    aims_rep = audit_aims_independence(aim1, aim2, aim3)
    aims_status = "pass" if aims_rep["score"] >= 3.5 and not aims_rep.get("has_domino_risk") else ("warning" if (aim1 or aim2 or aim3) else "incomplete")
    sections.append({
        "id": "sec_aims",
        "name": "4. Central Aim & 3 Specific Objectives",
        "status": aims_status,
        "badge": "✅ Robust" if aims_status == "pass" else ("⚠️ Needs Refinement" if aims_status == "warning" else "❌ Incomplete"),
        "excerpt": f"Aim: {aim_main[:80]}... | Obj 1: {aim1[:60]}..." if (aim_main or aim1) else "Objectives not formulated yet.",
        "strengths": aims_rep.get("strengths", []),
        "issues": aims_rep.get("issues", []),
        "action_recommendation": "Decouple Specific Objectives into 3 parallel work packages (Synthesis/Engineering ➔ Characterization ➔ Validation) with explicit Go/No-Go milestones to avoid Domino Collapse."
    })

    # 5. Experimental Methodology & Controls
    method = proposal_data.get("methodology", "")
    m_rep = audit_methodology_tense(method)
    m_status = "pass" if m_rep["score"] >= 10.0 and m_rep.get("tense_mark", 0) >= 0.8 and not m_rep.get("past_violations") and not any("controls" in iss.lower() for iss in m_rep.get("issues", [])) else ("warning" if method.strip() else "incomplete")
    sections.append({
        "id": "sec_methodology",
        "name": "5. Experimental Methodology & Essential Controls",
        "status": m_status,
        "badge": "✅ Robust" if m_status == "pass" else ("⚠️ Needs Refinement" if m_status == "warning" else "❌ Incomplete"),
        "excerpt": method[:160] + "..." if len(method) > 160 else (method if method.strip() else "Methodology not drafted yet."),
        "strengths": m_rep.get("strengths", []),
        "issues": m_rep.get("issues", []),
        "action_recommendation": "Use strict FUTURE TENSE ('will be cloned', 'will be assayed') and explicitly designate both positive controls (wild-type, commercial standard) and negative controls (empty vector, vehicle buffer)."
    })

    # 6. Expected Outcomes & Long-Term Impact
    outcomes = proposal_data.get("expected_outcomes", "")
    impact = proposal_data.get("impact_data", {})
    impact_academic = impact.get("academic", "")
    impact_economic = impact.get("economic", "")
    impact_societal = impact.get("societal", "")
    has_impact = bool(impact_academic or impact_economic or impact_societal or outcomes)
    imp_issues = []
    imp_strengths = []
    if not has_impact:
        imp_status = "incomplete"
        imp_issues.append("Expected outcomes and impact statements are empty.")
    else:
        if impact_academic:
            imp_strengths.append("Documents Academic & Disciplinary impact (data, protocols, publications).")
        else:
            imp_issues.append("Missing Academic Impact: Specify deliverables like public sequencing data or open protocols.")
        if impact_economic:
            imp_strengths.append("Documents Economic & Translational impact (cost reductions, bioprocess yield).")
        else:
            imp_issues.append("Missing Economic Impact: Outline cost-per-reaction reduction or scalability advantages.")
        if impact_societal:
            imp_strengths.append("Documents Societal & Environmental impact (patients reached, sustainability).")
        else:
            imp_issues.append("Missing Societal Impact: Articulate long-term health, environmental, or community benefits.")
        imp_status = "pass" if len(imp_strengths) >= 2 else "warning"

    sections.append({
        "id": "sec_impact",
        "name": "6. Expected Outcomes & Long-Term Impact",
        "status": imp_status,
        "badge": "✅ Robust" if imp_status == "pass" else ("⚠️ Needs Refinement" if imp_status == "warning" else "❌ Incomplete"),
        "excerpt": f"Academic: {impact_academic[:60]}... | Economic: {impact_economic[:60]}..." if has_impact else "Impact statements not drafted yet.",
        "strengths": imp_strengths,
        "issues": imp_issues,
        "action_recommendation": "Answer 'Why do the results matter?' across all three tiers: Academic (scientific community), Economic (cost/market), and Societal (real-world patient or environmental benefit)."
    })

    # 7. Competitor Analysis & Unique Selling Proposition
    comp_data = proposal_data.get("competitor_data", {})
    usp = comp_data.get("usp", "")
    c_rep = audit_competitor_matrix_and_usp(comp_data)
    c_status = "pass" if c_rep["score"] >= 4.0 else ("warning" if (usp or comp_data.get("incumbent_name")) else "incomplete")
    sections.append({
        "id": "sec_competitors",
        "name": "7. Competitor Landscape & Unique Selling Proposition (USP)",
        "status": c_status,
        "badge": "✅ Robust" if c_status == "pass" else ("⚠️ Needs Refinement" if c_status == "warning" else "❌ Incomplete"),
        "excerpt": f"USP: {usp}" if usp else "Competitor matrix and USP not completed yet.",
        "strengths": c_rep.get("strengths", []),
        "issues": c_rep.get("issues", []),
        "action_recommendation": "Benchmark against real commercial incumbents (avoid vague strawmen like 'traditional methods') across Speed, Cost, LOD, and Portability, and crystallize your USP in 1 sentence."
    })

    # 8. Biotech SWOT & Feasibility
    swot = proposal_data.get("swot", {})
    pestel = proposal_data.get("pestel", {})
    swot_rep = audit_swot_pestel(swot, pestel)
    swot_status = "pass" if swot_rep["score"] >= 6.0 else ("warning" if any(swot.values()) else "incomplete")
    sections.append({
        "id": "sec_swot",
        "name": "8. Biotech SWOT & Feasibility Failure Modes",
        "status": swot_status,
        "badge": "✅ Robust" if swot_status == "pass" else ("⚠️ Needs Refinement" if swot_status == "warning" else "❌ Incomplete"),
        "excerpt": f"Weakness: {swot.get('w', '')[:60]}... | Threat: {swot.get('t', '')[:60]}..." if any(swot.values()) else "SWOT matrix not filled yet.",
        "strengths": swot_rep.get("strengths", []),
        "issues": swot_rep.get("issues", []),
        "action_recommendation": "Ensure Weaknesses reflect biochemical or biophysical bottlenecks (e.g., proteolytic degradation, low induction yield) rather than student clichés like 'lack of time'."
    })

    # 9. Peer-Reviewed References & Recency
    refs = proposal_data.get("references", "")
    from core.reference_service import audit_bibliography_recency
    r_rep = audit_bibliography_recency(refs)
    r_passed = r_rep.get("passed_rubric", False)
    r_status = "pass" if r_passed and r_rep.get("total_count", 0) >= 3 else ("warning" if refs.strip() else "incomplete")
    r_issues = [r_rep.get("feedback", "")] if not r_passed and refs.strip() else []
    r_strengths = [r_rep.get("feedback", "")] if r_passed else []
    sections.append({
        "id": "sec_references",
        "name": "9. Peer-Reviewed References & Recency Audit",
        "status": r_status,
        "badge": "✅ Robust" if r_status == "pass" else ("⚠️ Needs Refinement" if r_status == "warning" else "❌ Incomplete"),
        "excerpt": f"{r_rep.get('total_count', 0)} references detected. {r_rep.get('recent_count', 0)} recent ({r_rep.get('recency_percentage', 0.0)}%, Target ≥60% from 2021–2026).",
        "strengths": r_strengths,
        "issues": r_issues,
        "action_recommendation": "Include at least 5 primary citations formatted in APA style, with ≥60% published between 2021 and 2026."
    })

    # Summary
    passed_count = sum(1 for s in sections if s["status"] == "pass")
    warning_count = sum(1 for s in sections if s["status"] == "warning")
    incomplete_count = sum(1 for s in sections if s["status"] == "incomplete")
    total_count = len(sections)

    if passed_count >= 7 and incomplete_count == 0:
        overall_status = "Ready for Submission"
    elif passed_count >= 4:
        overall_status = "Revisions Recommended"
    else:
        overall_status = "Draft in Progress"

    overall_score_pct = round((passed_count / total_count) * 100.0, 1)

    return {
        "summary": {
            "passed_sections": passed_count,
            "warning_sections": warning_count,
            "incomplete_sections": incomplete_count,
            "total_sections": total_count,
            "overall_status": overall_status,
            "overall_score_pct": overall_score_pct
        },
        "sections": sections
    }

