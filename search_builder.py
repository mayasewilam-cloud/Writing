"""
Search Query Builder for BT_301 & Diverse Scientific Research Projects.
Supports cellular hosts, cell-free diagnostics, nanomaterials, environmental matrices,
and computational projects.
"""

import urllib.parse
from typing import Dict, List, Any


def build_boolean_query(system: str = "", tool: str = "", target: str = "", chassis: str = "", synonyms: Dict[str, List[str]] = None) -> Dict[str, Any]:
    """
    Build professional 3-Pillar Boolean search strings and direct deep-links.
    Pillar 1 (system/chassis): Living host, cell line, clinical specimen, diagnostic matrix, or nanoparticle carrier.
    Pillar 2 (tool): Enzyme, molecular probe, gene editor, therapeutic cargo, or algorithm.
    Pillar 3 (target): Target biomarker, pollutant, disease phenotype, or quantitative metric.
    """
    system = (system or chassis).strip()
    tool = tool.strip()
    target = target.strip()

    # Pillar 1: System / Context
    system_part = f'"{system}"' if " " in system and not system.startswith('"') else system
    
    # Pillar 2: Tool / Mechanism
    tool_terms = [tool]
    if synonyms and "tool" in synonyms:
        tool_terms.extend([s for s in synonyms["tool"] if s and s != tool])
    if len(tool_terms) > 1:
        tool_part = "(" + " OR ".join([f'"{t}"' if " " in t and not t.startswith('"') else t for t in tool_terms]) + ")"
    else:
        tool_part = f'"{tool}"' if " " in tool and not tool.startswith('"') else tool

    # Pillar 3: Target / Desired Outcome
    target_terms = [target]
    if synonyms and "target" in synonyms:
        target_terms.extend([s for s in synonyms["target"] if s and s != target])
    if len(target_terms) > 1:
        target_part = "(" + " OR ".join([f'"{t}"' if " " in t and not t.startswith('"') else t for t in target_terms]) + ")"
    else:
        target_part = f'"{target}"' if " " in target and not target.startswith('"') else target

    # Combined 3-Pillar query
    full_boolean = f"{system_part} AND {tool_part} AND {target_part}"
    tiab_boolean = f"({system_part}[Title/Abstract]) AND ({tool_part}[Title/Abstract]) AND ({target_part}[Title/Abstract])"

    # PubMed link
    pubmed_base = "https://pubmed.ncbi.nlm.nih.gov/?"
    pubmed_params = {
        "term": full_boolean,
        "filter": "simsearch1.fha,pubt.review,years.5"
    }
    pubmed_url = pubmed_base + urllib.parse.urlencode(pubmed_params)

    # Google Scholar link
    scholar_base = "https://scholar.google.com/scholar?"
    scholar_query = f'{system} {tool} {target} review'
    scholar_params = {
        "q": scholar_query,
        "as_ylo": "2021"
    }
    scholar_url = scholar_base + urllib.parse.urlencode(scholar_params)

    # Europe PMC link
    europe_base = "https://europepmc.org/search?"
    europe_params = {
        "query": f'({full_boolean}) AND (OPEN_ACCESS:Y) AND (SRC:MED)'
    }
    europe_url = europe_base + urllib.parse.urlencode(europe_params)

    return {
        "pillars": {
            "system": system,
            "tool": tool,
            "target": target
        },
        "query": full_boolean,
        "query_tiab": tiab_boolean,
        "links": {
            "pubmed": pubmed_url,
            "scholar": scholar_url,
            "europe_pmc": europe_url
        }
    }


def get_curated_examples() -> List[Dict[str, Any]]:
    """
    Returns curated, diverse biotechnology examples spanning different project models:
    cellular hosts, cell-free diagnostics, nanotechnology, environmental, and computation.
    """
    return [
        {
            "category": "Cell-Free Diagnostics (No Living Host)",
            "topic": "Rapid Paper-Based CRISPR-Cas12a Detection of Colistin Resistance in Hospital Effluents",
            "model_id": "cell_free",
            "system": "hospital wastewater effluent",
            "chassis": "hospital wastewater effluent",
            "tool": "CRISPR-Cas12a fluorescent reporter",
            "target": "mcr-1 colistin resistance gene",
            "synonyms": {
                "tool": ["Cas12a-crRNA", "RPA isothermal amplification"],
                "target": ["mcr-1 gene", "colistin resistance"]
            }
        },
        {
            "category": "Microbial Host Expression (White Biotech)",
            "topic": "Engineered Salt Bridges in PETase Expressed in Pseudomonas putida for Plastic Bioremediation",
            "model_id": "cellular",
            "system": "Pseudomonas putida",
            "tool": "engineered PETase",
            "target": "polyethylene terephthalate degradation",
            "synonyms": {
                "tool": ["PET hydrolase", "MHETase"],
                "target": ["PET plastic film", "depolymerization rate"]
            }
        },
        {
            "category": "Nanotechnology & Drug Delivery (No Living Host)",
            "topic": "Lipid Nanoparticle Delivery of siRNA for Targeted Oncogene Silencing in Triple-Negative Breast Cancer",
            "model_id": "nanotech",
            "system": "lipid nanoparticles",
            "tool": "siRNA cargo",
            "target": "triple-negative breast cancer silencing",
            "synonyms": {
                "tool": ["RNA interference", "LNP formulation"],
                "target": ["TNBC", "oncogene knockdown"]
            }
        },
        {
            "category": "Environmental & Biocatalysis (Immobilized System)",
            "topic": "Immobilized Laccase CLEAs for Continuous Degradation of Pharmaceutical Micropollutants",
            "model_id": "environmental",
            "system": "membrane bioreactor effluent",
            "tool": "cross-linked laccase aggregates",
            "target": "pharmaceutical micropollutant clearance",
            "synonyms": {
                "tool": ["CLEA", "immobilized biocatalyst"],
                "target": ["carbamazepine removal", "endocrine disruptor"]
            }
        },
        {
            "category": "Plant Gene Editing (Green Biotech)",
            "topic": "CRISPR Base Editing of the TaHKT1;5 Sodium Transporter for Wheat Salinity Tolerance",
            "model_id": "cellular",
            "system": "Triticum aestivum",
            "tool": "cytidine base editor",
            "target": "TaHKT1;5 foliar sodium exclusion",
            "synonyms": {
                "tool": ["base editor", "Cas9-cytidine deaminase"],
                "target": ["salinity stress", "salt tolerance"]
            }
        }
    ]
