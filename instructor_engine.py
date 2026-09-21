"""
Faculty Grading & Rapid Feedback Comment Bank Engine.
Implements the official BT_301 Comment Bank from Section 5 of the
Faculty Teaching & Studio Facilitation Manual.
Provides 1-click corrective feedback across all 11 rubric criteria.
"""

from typing import Dict, List, Any


def get_rapid_comment_bank() -> Dict[str, List[Dict[str, str]]]:
    """
    Returns curated rubric comments organized by criterion code.
    """
    return {
        "title": [
            {
                "code": "T-01",
                "label": "Vague Title (All-or-None 0%)",
                "comment": "Title is overly vague and fails the 4-anchor formula. Rephrase as: [Mechanism] in [Experimental System] to [Target Metric] for [Application]. Awarded: 0%."
            },
            {
                "code": "T-02",
                "label": "Missing System / Chassis",
                "comment": "Title lacks experimental system, biological host organism, or delivery matrix. Specify the exact experimental model."
            },
            {
                "code": "T-03",
                "label": "Strong Descriptive Title",
                "comment": "Concise, descriptive, and accurately conveys molecular mechanism, host, and application. Awarded: 2%."
            }
        ],
        "abstract": [
            {
                "code": "AB-01",
                "label": "Exceeds 250 Words",
                "comment": "Abstract exceeds the strict 250-word ceiling. Edit down concisely to prevent editorial desk rejection."
            },
            {
                "code": "AB-02",
                "label": "Unbalanced Components",
                "comment": "Abstract must balance 4 distinct components: Problem burden (2%), brief methodology (2%), expected findings (1%), and concluding impact statement."
            }
        ],
        "background": [
            {
                "code": "BG-01",
                "label": "Missing Quantified Burden",
                "comment": "Tier 1 problem statement lacks an empirical quantified statistic (annual metric tons, incidence rate, or monetary loss). Replace general assertions with hard numbers."
            },
            {
                "code": "BG-02",
                "label": "Missing Knowledge Gap Pivot",
                "comment": "Missing an explicit pivot from existing literature to your knowledge gap. Use a formal transition ('However, widespread deployment remains critically constrained by...')."
            },
            {
                "code": "BG-03",
                "label": "Hypothesis Lacks Mechanism",
                "comment": "Hypothesis is descriptive rather than mechanistic. Include 'because...' followed by the specific biophysical or biochemical rationale."
            }
        ],
        "aims": [
            {
                "code": "AIM-01",
                "label": "Domino Collapse Trap",
                "comment": "FATAL REVIEWER FLAW: Objective 2 completely depends on Objective 1 succeeding with 100% yield. Establish an active parallel baseline so work continues if Objective 1 faces technical delays."
            },
            {
                "code": "AIM-02",
                "label": "Missing Quantitative Milestone",
                "comment": "Each objective must conclude with a measurable Go/No-Go milestone (e.g. expression yield, Kd, Tm elevation, % clearance)."
            }
        ],
        "methodology": [
            {
                "code": "METH-01",
                "label": "Past Tense Penalty (Rubric 11)",
                "comment": "Methodology is written in past tense ('was performed', 'were inoculated'). Proposals describe FUTURE work: rewrite strictly in future tense ('will be incubated', 'will be assayed'). Penalty: -1.0 mark."
            },
            {
                "code": "METH-02",
                "label": "Missing Experimental Controls",
                "comment": "Missing explicit positive, negative, and vehicle controls. State what negative control separates biological activity from abiotic background noise."
            }
        ],
        "swot": [
            {
                "code": "SW-01",
                "label": "Student Cliché in Weaknesses",
                "comment": "AVOID STUDENT COP-OUT: 'We are students' or 'lack of time' loses marks. Weaknesses must address authentic biological failure modes (e.g. inclusion bodies, off-target cleavage, proteolytic degradation)."
            },
            {
                "code": "SW-02",
                "label": "Incomplete PESTEL",
                "comment": "Ensure all 6 PESTEL dimensions are addressed with genuine biotechnology context (e.g. Cartagena Protocol for Legal, reagent tariffs for Economic)."
            }
        ]
    }


def compile_instructor_feedback_report(student_data: Dict[str, Any], selected_comment_codes: List[str], manual_comments: str = "") -> Dict[str, Any]:
    """
    Compiles an official faculty evaluation feedback memo.
    """
    bank = get_rapid_comment_bank()
    flat_comments = {}
    for cat, items in bank.items():
        for item in items:
            flat_comments[item["code"]] = item

    applied_notes = []
    for code in selected_comment_codes:
        if code in flat_comments:
            applied_notes.append(flat_comments[code])

    memo_text = f"FACULTY REVIEW & FACILITATION AUDIT MEMO\n"
    memo_text += f"Project: {student_data.get('title', 'Untitled')}\n"
    memo_text += f"Student / Team: {student_data.get('student_name', 'Student')}\n"
    memo_text += f"Course: BT_301 Introduction to Biotechnology\n"
    memo_text += f"=================================================================\n\n"
    memo_text += "RAPID AUDIT NOTES:\n"
    for note in applied_notes:
        memo_text += f"• [{note['code']} - {note['label']}]: {note['comment']}\n"

    if manual_comments.strip():
        memo_text += f"\nFACULTY INSTRUCTOR NOTES:\n{manual_comments.strip()}\n"

    return {
        "applied_notes": applied_notes,
        "memo_text": memo_text
    }
