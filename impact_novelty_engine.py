"""
Impact, Novelty, Gap Taxonomy & Competitor Analysis Engine.
Implements pedagogical diagnostics for:
1. Scientific Gap Taxonomy & Contrast Phrasing.
2. Novelty & Originality Assessment (Host-Swap Trap Detector).
3. Scientific Soundness & Falsifiability Checks.
4. "Search for Significance" Query Generator (DALYs, Economic Burden, WHO/FAO).
5. 10-Node End-to-End Proposal Logic Chain Evaluator:
   Problem → Gap → Solution → Objectives → Methodology → Results → Impact → Work plan → Budget → References
6. Competitor Analysis Matrix & Rock-Solid USP Synthesizer.
"""

import re
import urllib.parse
from typing import Dict, List, Any


# 5 Recognized Scientific Gap Categories
GAP_TAXONOMY = {
    "mechanistic": {
        "title": "1. Mechanistic / Biophysical Knowledge Gap",
        "definition": "The biological effect or macroscopic phenotype is documented, but the underlying molecular mechanism, catalytic pathway, or structural interaction remains unknown.",
        "indicator_phrases": [
            "molecular mechanism", "structural basis", "biophysical pathway",
            "catalytic mechanism", "allosteric regulation", "pathway remains",
            "structural interaction", "conformational", "binding affinity",
            "active site architecture"
        ],
        "example": "While wild-type PETase cleaves ester bonds, the structural mechanism governing acid-induced denaturation at pH < 5.0 remains unresolved."
    },
    "performance": {
        "title": "2. Performance / Biophysical Ceiling Gap",
        "definition": "Existing enzymes, vectors, or organisms hit an intrinsic biological limitation (e.g. low thermal unfolding Tm, product inhibition, proteolytic degradation, low turnover kcat).",
        "indicator_phrases": [
            "low thermal stability", "product inhibition", "inactivation", "low catalytic efficiency",
            "poor yield", "cleavage efficiency", "thermal denaturation", "thermolability",
            "denaturation", "turnover rate", "degradation rate", "tm <", "unfolding",
            "thermal", "thermostab", "proteolytic", "half-life", "catalytic rate"
        ],
        "example": "Industrial adoption is critically constrained by enzyme thermolability (Tm < 48°C), causing irreversible denaturation within 12 hours of operation."
    },
    "methodological": {
        "title": "3. Methodological / Technical Deployability Gap",
        "definition": "Current methods require costly, centralized machinery, cold chains, or multi-day culture times, preventing decentralized, low-resource, or real-time deployment.",
        "indicator_phrases": [
            "centralized equipment", "delayed turnaround", "cold-chain", "precludes point-of-care",
            "cost-prohibitive", "culture window", "labor-intensive", "turnaround time",
            "point-of-care", "instrumentation", "specialized machinery", "costly diagnostic"
        ],
        "example": "Standard broth microdilution requires 24–48 hours, delaying clinical interventions during acute bacteremia and septic episodes."
    },
    "matrix": {
        "title": "4. Environmental / Clinical Matrix Gap",
        "definition": "A tool functions well in clean buffer or model lab strains, but fails or experiences severe inhibition in complex real-world matrices (e.g. whole blood, industrial sludge, hypersaline soil).",
        "indicator_phrases": [
            "complex matrices", "inhibitors in whole blood", "hypersaline", "crude effluent",
            "soil microenvironment", "matrix interference", "whole blood", "matrix inhibition",
            "environmental matrix", "real-world matrix", "interfering substance", "inhibitory matrix"
        ],
        "example": "Although Cas12a operates robustly in synthetic oligonucleotides, humic acids and heavy metals in industrial effluent inhibit Cas12a collateral cleavage by >85%."
    },
    "translational": {
        "title": "5. Translational / Scale-Up Gap",
        "definition": "An intervention succeeds at 1 mL bench scale, but encounters mass transfer, oxygen limitation, metabolic burden, or genetic instability when scaled to 500 L bioreactors.",
        "indicator_phrases": [
            "bioreactor scale", "mass transfer limitation", "metabolic burden", "genetic drift",
            "downstream processing", "pilot scale", "scale-up", "scale up", "fermentation volume",
            "plasmid loss", "bioreactor", "aeration limit", "shear stress"
        ],
        "example": "High plasmid copy numbers impose severe metabolic burden, precipitating plasmid loss and a 70% drop in recombinant yield during fed-batch fermentation."
    }
}


# 4 Required Competitive Advantage Categories (from Proposal Field Guide)
ADVANTAGE_CATEGORIES = {
    "performance": {
        "label": "Performance & Catalytic Advantage",
        "metric_examples": ["3-fold higher kcat", "elevated Tm >= 65°C", "limit of detection <= 5 copies/uL", "95% substrate conversion"]
    },
    "novelty": {
        "label": "Novelty & Intellectual Property (IP)",
        "metric_examples": ["Unpublished dual-action chimeric fusion", "novel allosteric switch", "proprietary guide-RNA architecture"]
    },
    "access": {
        "label": "Access & Portability (Point-of-Care / Field)",
        "metric_examples": ["Isothermal 37°C operation (no thermocycler)", "ambient stable lyophilized reagents", "15-minute sample-to-answer"]
    },
    "cost": {
        "label": "Economic & Cost-Efficiency Advantage",
        "metric_examples": ["60% reduction in enzyme synthesis cost", "eliminates capital expenditure", "cheaper alternative substrate"]
    }
}


def audit_gap_statement(gap_text: str, selected_gap_type: str = "") -> Dict[str, Any]:
    """
    Audits the scientific knowledge gap according to STDF / ICGEB and BT_301 rubric standards.
    Checks for:
    - Explicit contrast transitions ('However,', 'Despite this,', 'Critically constrained by')
    - Sourced quantitative failure bottleneck
    - Gap taxonomy classification
    - Strawman warning (e.g. 'no one has ever studied X' with zero citations)
    """
    text = gap_text.strip()
    if not text or len(text.split()) < 8:
        return {
            "status": "incomplete",
            "score": 0.0,
            "passed": False,
            "gap_type": selected_gap_type if selected_gap_type in GAP_TAXONOMY else "unknown",
            "gap_title": GAP_TAXONOMY.get(selected_gap_type, {}).get("title", "Custom Scientific Gap"),
            "has_contrast_pivot": False,
            "has_metric": False,
            "is_strawman": False,
            "issues": ["Gap statement is too short or empty. Must state the explicit unresolved bottleneck."],
            "recommendations": ["Start with an explicit pivot: 'However, widespread deployment remains critically constrained by [precise biophysical flaw]...'"]
        }

    issues = []
    recommendations = []
    score = 5.0  # Out of 5.0 marks for Rubric Item 3 Stage 3

    # Check for explicit contrast pivot
    contrast_markers = [
        "however", "despite this", "critically constrained", "remains unresolved",
        "suffers from", "precludes deployment", "limiting factor", "drawback",
        "bottleneck", "nevertheless", "yet to date", "fundamentally limited"
    ]
    has_contrast = any(re.search(r"\b" + re.escape(m) + r"\b", text.lower()) for m in contrast_markers)
    if not has_contrast:
        score -= 2.0
        issues.append("Missing explicit contrast pivot. Reviewers look for 'However,' or 'Despite this,' to anchor the gap.")
        recommendations.append("Add a formal transition: 'However, current commercial technologies remain fundamentally constrained by...'")

    # Check for quantitative or biophysical metric
    metric_patterns = [
        r"\b\d+(\.\d+)?\s*(%|°c|c|mg|ug|g|l|ml|ul|nm|um|mm|min|h|hours?|kd|kcat|tm|fold|copies)\b",
        r"\b(thermal|denaturation|aggregation|inactivation|instability|inhibition|toxicity|loss|yield|degradation)\b"
    ]
    has_metric = any(re.search(p, text.lower()) for p in metric_patterns)
    if not has_metric:
        score -= 1.5
        issues.append("Gap lacks a quantified bottleneck or biophysical failure mode.")
        recommendations.append("State the exact biophysical reason (e.g. 'unfolds at temperatures exceeding 48°C' or 'suffers product inhibition above 5 mM').")

    # Check for Strawman Gap ("no research exists", "no one has ever studied", "little is known")
    strawman_phrases = ["no one has ever", "nobody has studied", "never been researched", "no literature exists", "little is known"]
    is_strawman = any(sp in text.lower() for sp in strawman_phrases)
    if is_strawman:
        score -= 1.5
        issues.append("Strawman Gap warning: Claiming 'no one has ever studied this' invites immediate reviewer skepticism.")
        recommendations.append("Acknowledge prior work first, then state why their specific approach failed: 'While [Author] developed [X], their system suffered from [Y]'.")

    # Identify Gap Taxonomy Type
    matched_type = "unclassified"
    best_match_count = 0
    for gtype, ginfo in GAP_TAXONOMY.items():
        count = sum(1 for phrase in ginfo["indicator_phrases"] if phrase in text.lower())
        if count > best_match_count:
            best_match_count = count
            matched_type = gtype

    if matched_type == "unclassified" and selected_gap_type in GAP_TAXONOMY:
        matched_type = selected_gap_type

    final_score = max(0.0, round(score, 1))
    passed = final_score >= 3.5

    return {
        "status": "audited",
        "score": final_score,
        "passed": passed,
        "gap_type": matched_type,
        "gap_title": GAP_TAXONOMY.get(matched_type, {}).get("title", "Custom Scientific Gap"),
        "has_contrast_pivot": has_contrast,
        "has_metric": has_metric,
        "is_strawman": is_strawman,
        "issues": issues,
        "recommendations": recommendations,
        "feedback": "Strong, evidenced knowledge gap." if passed else "Needs explicit contrast and quantified biophysical bottleneck."
    }


def audit_novelty_and_soundness(
    title: str = "",
    chassis: str = "",
    tool: str = "",
    target: str = "",
    hypothesis: str = "",
    methodology: str = ""
) -> Dict[str, Any]:
    """
    Evaluates proposal novelty and scientific soundness:
    1. Host-Swap Trap: Merely changing host organism without biochemical rationale.
    2. Inventive Step / Engineering Mechanism.
    3. Falsifiability & Experimental Controls.
    """
    issues = []
    strengths = []
    risk_level = "low"
    is_host_swap_trap = False

    combined_text = f"{title} {hypothesis} {methodology}".lower()

    # 1. Host-Swap Trap Check:
    # If the student simply states "We will express [Tool] in [Chassis]" without naming an engineering modification
    common_hosts = ["escherichia coli", "e. coli", "pichia pastoris", "saccharomyces cerevisiae", "bacillus subtilis", "pseudomonas putida"]
    has_common_host = any(h in chassis.lower() for h in common_hosts)
    
    engineering_markers = [
        "disulfide", "salt bridge", "rational design", "directed evolution", "mutation",
        "fusion", "chimeric", "promoter engineering", "codon optimiz", "knockout",
        "isothermal", "aptamer", "surface display", "crrna", "guide rna", "rnp"
    ]
    has_engineering = any(em in combined_text for em in engineering_markers)

    if has_common_host and not has_engineering:
        is_host_swap_trap = True
        risk_level = "high"
        issues.append(
            "POTENTIAL 'HOST-SWAP TRAP': Merely moving a known enzyme/gene into a different host without an engineered modification "
            "(e.g. rational mutation, fusion, promoter tuning) represents an incremental student exercise rather than fundable scientific novelty."
        )
    elif has_engineering:
        strengths.append("Contains explicit molecular engineering intervention (rational design / catalytic modification).")

    # 2. Controls & Falsifiability Check:
    has_neg_control = any(nc in methodology.lower() for nc in ["negative control", "empty vector", "vehicle control", "wild-type", "untransformed"])
    has_pos_control = any(pc in methodology.lower() for pc in ["positive control", "commercial enzyme", "reference standard", "purified benchmark"])

    if not has_neg_control:
        issues.append("Missing negative experimental control (e.g. empty vector or vehicle buffer) to prove biological causality.")
    else:
        strengths.append("Explicit negative control specified.")

    if not has_pos_control:
        issues.append("Missing positive / benchmark control (e.g. wild-type enzyme or commercial gold standard) to benchmark performance.")
    else:
        strengths.append("Validated positive / benchmark control specified.")

    # 3. Mechanistic Hypothesis Check:
    has_because_clause = any(bc in hypothesis.lower() for bc in ["because", "due to", "mediated by", "through conformational", "via electrostatic", "thereby preventing"])
    if not has_because_clause:
        issues.append("Hypothesis is descriptive rather than mechanistic. It must explain WHY the solution will work (e.g. 'because salt bridges will stabilize the flexible beta-sheet').")
    else:
        strengths.append("Hypothesis provides a mechanistic 'because...' biophysical rationale.")

    # Scientific Soundness Score (0 - 100)
    soundness_score = 100
    soundness_score -= len(issues) * 18
    soundness_score = max(20, min(100, soundness_score))

    return {
        "soundness_score": soundness_score,
        "is_novel": bool(has_engineering and not is_host_swap_trap),
        "is_host_swap_trap": is_host_swap_trap,
        "risk_level": risk_level,
        "has_controls": bool(has_neg_control and has_pos_control),
        "issues": issues,
        "strengths": strengths,
        "verdict": "Scientifically Sound & Novel" if soundness_score >= 75 else "Requires Mechanistic Novelty & Control Validation"
    }


def build_significance_search_queries(chassis: str, tool: str, target: str, project_modality: str = "cellular") -> Dict[str, Any]:
    """
    Generates tailored search queries for finding economic burden, health statistics (DALYs),
    global annual loss, and market indicators across PubMed, Google, WHO, and FAO.
    """
    chassis_clean = chassis.strip() or "Biotechnology"
    target_clean = target.strip() or "Environmental Crisis"

    queries = {
        "health_burden_pubmed": f'("{target_clean}") AND ("mortality" OR "DALYs" OR "incidence" OR "economic burden" OR "annual cost")',
        "market_and_industry_google": f'"{target_clean}" market size CAGR "USD million" OR "billion" report 2023..2026',
        "global_loss_fao_who": f'site:who.int OR site:fao.org OR site:worldbank.org "{target_clean}" burden OR loss OR statistics',
        "standards_and_guidelines": f'("{target_clean}") AND ("regulatory threshold" OR "maximum residue limit" OR "EPA" OR "clinical standard")'
    }

    encoded_links = {
        "pubmed_burden": f"https://pubmed.ncbi.nlm.nih.gov/?term={urllib.parse.quote_plus(queries['health_burden_pubmed'])}",
        "google_market": f"https://www.google.com/search?q={urllib.parse.quote_plus(queries['market_and_industry_google'])}",
        "global_orgs": f"https://www.google.com/search?q={urllib.parse.quote_plus(queries['global_loss_fao_who'])}"
    }

    return {
        "queries": queries,
        "links": encoded_links,
        "guidance": "Use these specific Boolean strings to find the 'Scary Crisis Numbers' (annual metric tons, hospitalizations, USD loss) needed for Tier 1 of your Background and Section 10 Impact."
    }


def evaluate_proposal_logic_chain(proposal_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates the complete 10-node scientific proposal logic chain:
    Problem → Gap → Solution → Objectives → Methodology → Results → Impact → Work plan → Budget → References
    Checks for semantic coherence and ensures the thread is maintained throughout.
    """
    funnel = proposal_data.get("funnel", {})
    aims = proposal_data.get("aims", {})
    methodology = proposal_data.get("methodology", "")
    outcomes = proposal_data.get("expected_outcomes", "")
    impact = proposal_data.get("impact", "") or proposal_data.get("usps", "")
    time_plan = proposal_data.get("time_plan", "")
    budget = proposal_data.get("budget", "")
    references = proposal_data.get("references", "")

    nodes = [
        {"id": "problem", "name": "1. Problem", "filled": bool(funnel.get("tier1")), "text": funnel.get("tier1", "")},
        {"id": "gap", "name": "2. Gap", "filled": bool(funnel.get("tier3")), "text": funnel.get("tier3", "")},
        {"id": "solution", "name": "3. Solution", "filled": bool(funnel.get("tier4")), "text": funnel.get("tier4", "")},
        {"id": "objectives", "name": "4. Objectives", "filled": bool(aims.get("aim1") and aims.get("aim2")), "text": f"{aims.get('aim1', '')} | {aims.get('aim2', '')}"},
        {"id": "methodology", "name": "5. Methodology", "filled": bool(len(methodology.split()) > 20), "text": methodology[:120]},
        {"id": "results", "name": "6. Results", "filled": bool(outcomes), "text": outcomes[:120]},
        {"id": "impact", "name": "7. Impact", "filled": bool(impact), "text": impact[:120]},
        {"id": "work_plan", "name": "8. Work Plan", "filled": bool(time_plan), "text": time_plan[:120]},
        {"id": "budget", "name": "9. Budget", "filled": bool(budget), "text": budget[:120]},
        {"id": "references", "name": "10. References", "filled": bool(references), "text": references[:120]}
    ]

    filled_count = sum(1 for n in nodes if n["filled"])
    chain_health_pct = round((filled_count / 10.0) * 100, 1)

    # Narrative Coherence Warnings
    warnings = []
    if funnel.get("tier1") and not funnel.get("tier3"):
        warnings.append("Broken Link: You defined a Problem (Tier 1) but have not stated the specific Knowledge Gap (Tier 3) preventing its solution.")

    if funnel.get("tier3") and not funnel.get("tier4"):
        warnings.append("Broken Link: You stated a Knowledge Gap (Tier 3) but have not provided your team's Proposed Solution/Hypothesis (Tier 4).")

    if aims.get("aim1") and not outcomes:
        warnings.append("Broken Link: You listed Specific Objectives but have not detailed the anticipated Deliverables / Expected Results.")

    if outcomes and not impact:
        warnings.append("Broken Link: You specified Expected Results but have not explained the Long-Term Impact ('Why do the results matter?').")

    return {
        "chain_health_pct": chain_health_pct,
        "filled_nodes": filled_count,
        "total_nodes": 10,
        "nodes": nodes,
        "warnings": warnings,
        "is_complete": filled_count == 10
    }


def audit_competitor_matrix_and_usp(competitor_data: Dict[str, Any], usp_text: str = "") -> Dict[str, Any]:
    """
    Audits Phase 9: Competitive Advantage & USPs (5% marks).
    Ensures:
    1. A real, specific competing technology/incumbent is named (avoids the 'traditional methods' strawman).
    2. At least one of the 4 advantage categories is explicitly declared.
    3. The USP sentence follows the winning formula:
       'Unlike [competitor], our [tool] [specifically does what better], which means [concrete benefit to user].'
    """
    usp_clean = usp_text.strip()
    incumbent = (competitor_data.get("principle_established") or competitor_data.get("incumbent_name", "")).strip()
    emerging = (competitor_data.get("principle_recent") or competitor_data.get("emerging_name", "")).strip()

    issues = []
    strengths = []
    score = 5.0 # Max 5 marks (2.5% Advantage paragraph + 2.5% USPs)

    # Check for strawman competitor
    strawman_competitors = ["traditional methods", "conventional approaches", "current ways", "old methods", "standard technique"]
    if any(sc in incumbent.lower() for sc in strawman_competitors) or any(sc in usp_clean.lower() for sc in strawman_competitors):
        score -= 1.5
        issues.append("Strawman Competitor Warning: Reviewers penalize vague phrases like 'Unlike traditional methods'. Name the real commercial machine, gold standard assay, or published benchmark (e.g. 'Unlike broth microdilution AST' or 'Unlike wild-type PETase').")
    elif incumbent:
        strengths.append(f"Names specific real-world incumbent standard: '{incumbent}'.")

    # Check for Advantage Category
    found_category = False
    for cat_key, cat_data in ADVANTAGE_CATEGORIES.items():
        if cat_key in usp_clean.lower() or any(term in usp_clean.lower() for term in ["cost", "yield", "speed", "portable", "isothermal", "sdn-1", "novel", "thermostab"]):
            found_category = True
            break

    if not found_category:
        score -= 1.0
        issues.append("USP should explicitly highlight at least one recognized category: Performance, Novelty/IP, Access/Portability, or Cost.")

    # Check for Concrete User Benefit ("which means...", "delivering...", "enabling...")
    benefit_markers = ["which means", "enabling", "allowing", "delivering", "providing", "reducing cost by", "shortening turnaround to"]
    has_benefit = any(bm in usp_clean.lower() for bm in benefit_markers)
    if not has_benefit:
        score -= 1.0
        issues.append("USP must link the technical feature to a concrete end-user benefit (e.g. '...which means hospital triage clinicians receive resistance profiles in under 30 minutes').")
    else:
        strengths.append("Includes clear end-user benefit payoff.")

    final_score = max(0.0, round(score, 1))
    passed = final_score >= 3.5

    return {
        "status": "audited",
        "score": final_score,
        "passed": passed,
        "incumbent_named": bool(incumbent),
        "emerging_named": bool(emerging),
        "issues": issues,
        "strengths": strengths,
        "feedback": "Outstanding competitive advantage & USP articulation." if passed else "Refine USP to name a specific competitor and end-user payoff."
    }
