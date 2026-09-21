"""
Scholarly Reference & DOI Resolution Service for BT_301.
Resolves DOIs via CrossRef REST API and PMIDs via NCBI E-utilities.
Audits bibliography recency against the >= 60% (2021-2026) rubric rule.
"""

import re
import requests
from typing import Dict, List, Any
from datetime import datetime


def fetch_doi_metadata(doi_string: str) -> Dict[str, Any]:
    """
    Fetches reference metadata from CrossRef public API given a DOI or URL.
    """
    doi_clean = doi_string.strip()
    # Clean standard prefixes
    doi_clean = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi_clean, flags=re.IGNORECASE)
    doi_clean = doi_clean.strip()

    if not doi_clean or "/" not in doi_clean:
        return {
            "success": False,
            "error": "Invalid DOI format. Expected format like: 10.1073/pnas.1718804115"
        }

    url = f"https://api.crossref.org/works/{doi_clean}"
    headers = {"User-Agent": "BioWriterStudio/1.0 (mailto:biowriter@university.edu)"}

    try:
        resp = requests.get(url, headers=headers, timeout=6.0)
        if resp.status_code == 200:
            data = resp.json().get("message", {})
            title = data.get("title", ["Unknown Title"])[0]
            
            # Authors
            authors_list = []
            for a in data.get("author", []):
                family = a.get("family", "")
                given = a.get("given", "")
                if family:
                    authors_list.append(f"{family}, {given[0]}." if given else family)
            authors_str = ", ".join(authors_list[:3])
            if len(authors_list) > 3:
                authors_str += " et al."

            # Publication Year
            published = data.get("published-print") or data.get("published-online") or data.get("created")
            year = None
            if published and "date-parts" in published and published["date-parts"]:
                year = published["date-parts"][0][0]

            journal = data.get("container-title", ["Unknown Journal"])[0] if data.get("container-title") else "Unknown Journal"

            is_recent = bool(year and year >= 2021)
            formatted_citation = f"{authors_str} ({year or 'n.d.'}). {title}. {journal}. DOI: {doi_clean}"

            return {
                "success": True,
                "doi": doi_clean,
                "title": title,
                "authors": authors_str,
                "year": year,
                "journal": journal,
                "is_recent": is_recent,
                "formatted_citation": formatted_citation
            }
        else:
            return {
                "success": False,
                "error": f"CrossRef returned status {resp.status_code} for DOI: {doi_clean}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Connection error looking up DOI: {str(e)}"
        }


def audit_bibliography_recency(references_text: str) -> Dict[str, Any]:
    """
    Parses references text and calculates the percentage of citations
    published within the past 5 years (2021-2026).
    Rubric Item 10: At least 60% must be recent.
    """
    text = references_text.strip()
    if not text:
        return {
            "total_count": 0,
            "recent_count": 0,
            "recency_percentage": 0.0,
            "passed_rubric": False,
            "references": [],
            "feedback": "No references entered. Add peer-reviewed citations."
        }

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    parsed_refs = []
    recent_count = 0

    current_year = 2026
    cutoff_year = 2021

    for line in lines:
        # Find 4-digit years between 1970 and 2026
        years = [int(y) for y in re.findall(r"\b(19\d{2}|20[0-2]\d)\b", line)]
        ref_year = max(years) if years else None
        is_recent = bool(ref_year and cutoff_year <= ref_year <= current_year)
        if is_recent:
            recent_count += 1

        parsed_refs.append({
            "text": line,
            "year": ref_year,
            "is_recent": is_recent
        })

    total_count = len(parsed_refs)
    recency_pct = round((recent_count / total_count * 100), 1) if total_count > 0 else 0.0
    passed = bool(recency_pct >= 60.0 and total_count >= 3)

    if passed:
        feedback = f"✅ Passes Rubric Item 10: {recency_pct}% of references ({recent_count}/{total_count}) are from 2021–2026 (Requirement: ≥60%)."
    elif total_count < 3:
        feedback = f"⚠️ Insufficient references ({total_count} cited). A standard proposal requires at least 5-10 peer-reviewed papers."
    else:
        feedback = f"❌ Fails Rubric Item 10: Only {recency_pct}% of references are recent ({recent_count}/{total_count}). Update at least {int(total_count * 0.6) - recent_count} more citations to 2021–2026."

    return {
        "total_count": total_count,
        "recent_count": recent_count,
        "recency_percentage": recency_pct,
        "passed_rubric": passed,
        "references": parsed_refs,
        "feedback": feedback
    }
