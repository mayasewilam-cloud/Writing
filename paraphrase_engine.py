"""
The RHEV Paraphrase Laboratory & Anti-Plagiarism Engine.
Implements the RHEV Protocol (Read, Hide, Explain from memory, Verify)
from the BT_301 Instructor Manual.
Detects verbatim n-gram runs, the 'Thesaurus Swap Trap', and calculates
Turnitin similarity risk to teach authentic academic writing.
"""

import re
from typing import Dict, List, Any


def tokenize_words(text: str) -> List[str]:
    """Tokenizes text into clean lowercase words without punctuation."""
    return re.findall(r"\b[a-zA-Z0-9_-]+\b", text.lower())


def extract_ngrams(tokens: List[str], n: int = 3) -> List[str]:
    """Extracts consecutive word n-grams."""
    if len(tokens) < n:
        return []
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def audit_paraphrase_rhev(original_text: str, student_draft: str) -> Dict[str, Any]:
    """
    Analyzes student draft against original text according to the RHEV Protocol.
    """
    orig_clean = original_text.strip()
    draft_clean = student_draft.strip()

    if not orig_clean or not draft_clean:
        return {
            "status": "incomplete",
            "similarity_score": 0.0,
            "risk_level": "none",
            "verbatim_runs": [],
            "thesaurus_trap": False,
            "feedback": "Please enter both the original source sentence and your paraphrased draft."
        }

    orig_tokens = tokenize_words(orig_clean)
    draft_tokens = tokenize_words(draft_clean)

    if not orig_tokens or not draft_tokens:
        return {
            "status": "incomplete",
            "similarity_score": 0.0,
            "risk_level": "none",
            "verbatim_runs": [],
            "thesaurus_trap": False,
            "feedback": "Text contains insufficient alphabetic words."
        }

    # Extract 3-grams and 4-grams
    orig_3grams = set(extract_ngrams(orig_tokens, 3))
    draft_3grams = set(extract_ngrams(draft_tokens, 3))

    shared_3grams = orig_3grams.intersection(draft_3grams)

    # Calculate Jaccard similarity of vocabulary
    orig_vocab = set(orig_tokens)
    draft_vocab = set(draft_tokens)
    jaccard_vocab = len(orig_vocab.intersection(draft_vocab)) / len(orig_vocab.union(draft_vocab)) if orig_vocab.union(draft_vocab) else 0.0

    # Check for consecutive verbatim runs
    verbatim_runs = []
    # Find contiguous overlapping sequences >= 3 words
    for i in range(len(draft_tokens) - 2):
        for length in range(len(draft_tokens) - i, 2, -1):
            sub_seq = " ".join(draft_tokens[i:i + length])
            if sub_seq in orig_clean.lower():
                if not any(sub_seq in existing for existing in verbatim_runs):
                    verbatim_runs.append(sub_seq)
                break

    # Detect Thesaurus Swap Trap:
    # High structural sentence similarity (similar sentence length and word order)
    # but low verbatim overlap (swapped words with synonyms)
    word_len_ratio = len(draft_tokens) / len(orig_tokens) if len(orig_tokens) else 1.0
    thesaurus_trap = False
    if 0.85 <= word_len_ratio <= 1.15 and len(verbatim_runs) <= 1 and jaccard_vocab < 0.35:
        # Check if punctuation / clause structure is identical
        orig_commas = orig_clean.count(",")
        draft_commas = draft_clean.count(",")
        if orig_commas == draft_commas and orig_commas >= 1:
            thesaurus_trap = True

    # Similarity Score (0 - 100%)
    ngram_sim = len(shared_3grams) / len(draft_3grams) if draft_3grams else 0.0
    combined_sim = round(((ngram_sim * 0.7) + (jaccard_vocab * 0.3)) * 100, 1)

    # Risk Level assessment
    if combined_sim > 45.0 or len(verbatim_runs) >= 2 or any(len(vr.split()) >= 6 for vr in verbatim_runs):
        risk_level = "high"
        passed = False
        verdict = "❌ High Plagiarism Risk (Turnitin Flagged)"
        advice = "You copied 3 or more consecutive words directly from the paper. Hide the original text completely, explain the scientific finding from memory without looking, and then rewrite."
    elif combined_sim > 25.0 or len(verbatim_runs) == 1 or thesaurus_trap:
        risk_level = "medium"
        passed = False
        verdict = "⚠️ Moderate Similarity / Potential Synonym Swap"
        if thesaurus_trap:
            advice = "Thesaurus Swap Trap Detected: You kept the exact sentence syntax of the author and swapped words. Change the rhetorical order: lead with the experimental outcome or the quantitative finding first."
        else:
            advice = "Noticeable overlap with original text. Rephrase the scientific concept using your own sentence architecture."
    else:
        risk_level = "low"
        passed = True
        verdict = "✅ Authentic Academic Paraphrase (Safe)"
        advice = "Excellent. You captured the core scientific finding using independent phrasing and distinct grammatical structure."

    return {
        "status": "audited",
        "passed": passed,
        "similarity_score": combined_sim,
        "risk_level": risk_level,
        "verdict": verdict,
        "verbatim_runs": verbatim_runs,
        "thesaurus_trap": thesaurus_trap,
        "shared_ngrams_count": len(shared_3grams),
        "advice": advice,
        "rhev_checklist": [
            {"step": "Read", "done": True, "note": "Read the original sentence carefully."},
            {"step": "Hide", "done": True, "note": "Hide the source text from view."},
            {"step": "Explain", "done": bool(draft_clean), "note": "Explain the biological finding from memory."},
            {"step": "Verify", "done": passed, "note": "Verify against verbatim n-gram overlap."}
        ]
    }
