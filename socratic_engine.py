"""
Socratic Coaching & Anti-Cheating Engine for BT_301.
Enforces the "Scaffold, Don't Solve" pedagogical policy:
- Refuses to ghostwrite or output full drafts.
- Diagnoses weaknesses, vague assertions, and missing biochemical mechanisms.
- Generates Socratic counter-questions and oral defense (Viva Voce) cross-examinations.
"""

import re
from typing import Dict, List, Any


def analyze_student_draft(section_name: str, draft_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Evaluates a drafted section with Socratic critique without rewriting the text.
    """
    text = draft_text.strip()
    if not text:
        return {
            "status": "empty",
            "message": f"Enter your draft for {section_name}. I will critique your logic and scientific rigor without writing it for you."
        }

    # Anti-cheating guard: detect if student is asking the tool to write for them
    cheating_prompts = [
        r"^write (me )?a (proposal|background|abstract|methodology)",
        r"^generate (a )?(paper|proposal|aims)",
        r"^can you write",
        r"^give me a paragraph",
        r"^do this for me"
    ]
    for cp in cheating_prompts:
        if re.search(cp, text, re.IGNORECASE):
            return {
                "status": "refusal",
                "message": (
                    "⚠️ Pedagogical Firewall Triggered: As your BT_301 scientific writing mentor, "
                    "I do not generate proposal text for you. Submitting AI-generated prose violates the course "
                    "plagiarism/AI ceiling (≤25%) and leaves you vulnerable in the oral defense. "
                    "Instead, use the Mad-Libs sentence starters or input your raw experimental ideas, and I will coach you through refining them!"
                )
            }

    critiques = []
    socratic_questions = []
    praise = []

    # 1. Vague vocabulary scan
    vague_terms = {
        "very good": "What is the exact quantitative kinetic rate or percent yield?",
        "many studies": "Which specific authors or landmark papers? Cite at least two with years.",
        "huge problem": "What is the quantified global burden (e.g. annual metric tons, economic loss in USD)?",
        "miraculous": "Maintain objective, restrained scientific tone. Express efficacy through measured data.",
        "cheaper and faster": "State the baseline cost vs. your projected cost, and hours saved.",
        "various enzymes": "Which specific enzyme families, EC numbers, or bacterial strains?",
        "improve health": "What specific physiological or molecular marker is being measured?"
    }

    for term, question in vague_terms.items():
        if term in text.lower():
            critiques.append(f"Vague phrase detected: '{term}'.")
            socratic_questions.append(question)

    # 2. Check for passive vs. active or unsupported generalizations
    if "everyone knows that" in text.lower() or "it is obvious that" in text.lower():
        critiques.append("Avoid conversational assumptions like 'everyone knows' or 'it is obvious'. In grant proposals, every assertion must be supported by empirical literature.")

    # 3. Citation density check
    citations = re.findall(r"\[[0-9,\s-]+\]|\([A-Za-z]+(?:\s+et\s+al\.)?,\s*\d{4}\)", text)
    if len(text.split()) > 60 and len(citations) == 0:
        critiques.append("No in-text citations detected in this paragraph.")
        socratic_questions.append("Which peer-reviewed paper supports the biological baseline or quantitative metrics you described?")
    elif len(citations) >= 1:
        praise.append(f"Good attribution: {len(citations)} literature citation(s) recognized.")

    # 4. Section-specific diagnostics
    if section_name.lower() == "background":
        if "however" not in text.lower() and "nevertheless" not in text.lower() and "constrained" not in text.lower():
            socratic_questions.append("Where is your explicit pivot from the 'Current Standard' to the 'Knowledge Gap'? Use a transition phrase like 'However, widespread deployment remains limited by...'")
        if "hypothes" not in text.lower():
            socratic_questions.append("Does your background conclude with your proposed hypothesis and molecular mechanism?")

    elif section_name.lower() == "methodology":
        if "control" not in text.lower():
            socratic_questions.append("What positive and negative controls will you include to validate that your assay is functioning properly?")
        if "will be" not in text.lower() and "shall be" not in text.lower():
            critiques.append("Methods should be written in future tense ('will be incubated', 'will be cloned').")

    # If no major issues found
    if not critiques and len(text.split()) >= 30:
        praise.append("Strong academic flow and clear scientific register.")
        socratic_questions.append("How would you defend this section if a reviewer asked: 'What is the primary biological failure risk of this approach?'")

    return {
        "status": "analyzed",
        "word_count": len(text.split()),
        "praise": praise,
        "critiques": critiques,
        "socratic_questions": socratic_questions,
        "action_item": (
            "Review the Socratic questions on the right. Revise your draft directly to address these questions "
            "before advancing to the next rubric checkpoint."
        )
    }


def generate_viva_defense_questions(proposal_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generates 3-5 authentic oral defense cross-examination questions tailored
    to the student's project to prepare them for the Week 10 Mock Review Panel / Viva Voce.
    """
    chassis = proposal_data.get("chassis", "the host organism")
    tool = proposal_data.get("tool", "the molecular tool/enzyme")
    target = proposal_data.get("target", "the target problem")
    
    questions = [
        {
            "id": 1,
            "category": "Chassis Justification & Physiology",
            "question": f"Why did your team select {chassis} as your production or deployment chassis instead of standard lab models (like E. coli or Pichia pastoris)? What specific post-translational modifications, codon biases, or growth advantages does it provide?",
            "eval_criteria": "Student must articulate biological rationale (e.g. secretory pathway, endotoxin-free, tolerance to high osmolarity) rather than just saying 'it was in the paper'.",
            "hint": "Reference doubling time, secretion signals, disulfide bond isomerization, or native metabolic pathways."
        },
        {
            "id": 2,
            "category": "Experimental Controls & Rigor",
            "question": f"In your testing of {tool}, what is your exact negative control, and what quantitative threshold separates a true biological effect from background noise or abiotic variation?",
            "eval_criteria": "Student must identify vehicle/mock-treated controls, dead enzyme (catalytic mutant), or untransformed host strain.",
            "hint": "For enzyme degradation: heat-inactivated enzyme control. For CRISPR: non-targeting guide RNA control."
        },
        {
            "id": 3,
            "category": "Biological Failure Modes (ACP Defense)",
            "question": f"Suppose your recombinant construct yields insoluble inclusion bodies when expressed in {chassis}. What is your immediate technical contingency plan to rescue soluble, active protein?",
            "eval_criteria": "Student applies the Acknowledge-Clarify-Pivot (ACP) technique and offers a realistic bioprocess pivot.",
            "hint": "Lower induction temperature to 16°C, fuse solubility tags (MBP/GST/SUMO), or switch to an Origami/chaperone-coexpressing strain."
        },
        {
            "id": 4,
            "category": "Aim Independence & Milestone Risk",
            "question": f"If Aim 1 yields 40% lower expression than your target milestone, how does that compromise Aim 2 and Aim 3? Did you engineer a parallel baseline or alternative candidate?",
            "eval_criteria": "Proves project does not suffer from Domino Collapse.",
            "hint": "Explain that Aim 2 utilizes commercially purchased wild-type enzyme as an active parallel baseline while Aim 1 mutants are being optimized."
        },
        {
            "id": 5,
            "category": "Translation & Regulatory Reality (PESTEL)",
            "question": f"Addressing {target} in a laboratory is vastly different from real-world environmental or clinical deployment. What specific biosafety level (BSL) or national regulatory framework governs your project?",
            "eval_criteria": "Student demonstrates awareness of containment, Cartagena Protocol, or local regulatory approval processes.",
            "hint": "Mention BSL-1/BSL-2 containment, kill-switch biocontainment for GMO release, or ethics committee approvals."
        }
    ]

    return questions
