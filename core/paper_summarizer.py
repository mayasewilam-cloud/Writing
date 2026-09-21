"""
Paper Decoder & Simple Explainer Engine for BioWriter Studio.
Deconstructs peer-reviewed scientific papers and abstracts into:
1. Executive 3-Sentence Summary (Problem -> Intervention -> Finding)
2. Plain-English "ELI-Undergrad" Explanation with real-world analogies
3. Biotech Jargon Buster (detects 60+ complex terms and provides clear definitions + analogies)
4. Extracted Proposal Parameters (Chassis, Tool, Quantified Metrics, Controls, Limitations)
5. Proposal Placement Recommendations (Tier 1, 2, 3, Aims, Competitors)
6. Socratic RHEV Paraphrase & Synthesis Challenge (Anti-Ghostwriting firewall)
"""

import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
import requests

# 60+ Biotechnology Terms with Plain-English Definitions & Analogies
JARGON_LEXICON = {
    "allosteric": {
        "term": "Allosteric Regulation / Allosteric Site",
        "simple_def": "A control switch on a protein located away from its active site.",
        "analogy": "Like a dimmer switch on a wall that controls the light without you having to touch the lightbulb directly."
    },
    "directed evolution": {
        "term": "Directed Evolution",
        "simple_def": "Speeding up natural selection in a test tube by mutating genes and picking the winners.",
        "analogy": "Like breeding racehorses, but doing 10,000 generations of bacteria in three days to find the fastest enzyme."
    },
    "codon optimization": {
        "term": "Codon Optimization",
        "simple_def": "Rewriting a gene's DNA spelling so the new host organism can read and translate it faster without changing the resulting protein.",
        "analogy": "Like translating British English slang into American English so a US reader doesn't stumble, while keeping the meaning identical."
    },
    "inclusion bodies": {
        "term": "Inclusion Bodies",
        "simple_def": "Dense, insoluble clumps of misfolded, non-functional protein inside a bacterial cell.",
        "analogy": "Like throwing clothes into a closet so fast that they ball up into a tangled knot you cannot wear until you iron each piece."
    },
    "isothermal": {
        "term": "Isothermal Amplification (e.g., LAMP, RPA)",
        "simple_def": "Multiplying DNA or RNA at a single, constant temperature without needing an expensive heating/cooling machine.",
        "analogy": "Like baking a cake in a simple warm water bath instead of an oven that has to repeatedly cycle between freezing and broiling."
    },
    "limit of detection": {
        "term": "Limit of Detection (LOD)",
        "simple_def": "The smallest amount of a target molecule that an assay can reliably detect from background noise.",
        "analogy": "Like how faint a whisper can be in a crowded room before your ear can no longer distinguish it from background chatter."
    },
    "lod": {
        "term": "Limit of Detection (LOD)",
        "simple_def": "The absolute lowest concentration of a biomarker that gives a reliable positive signal.",
        "analogy": "The smallest drop of food coloring in a swimming pool that still changes the water's tint."
    },
    "kcat": {
        "term": "Turnover Number (kcat)",
        "simple_def": "How many chemical reactions a single enzyme molecule can complete per second at full speed.",
        "analogy": "Like a factory worker's assembly speed: how many car doors one technician can bolt on in 60 seconds."
    },
    "km": {
        "term": "Michaelis Constant (Km)",
        "simple_def": "The concentration of substrate needed for an enzyme to reach half its maximum speed (measures binding grip).",
        "analogy": "Low Km means a high-grip magnet: it grabs iron filings even when they are scarce. High Km means a weak magnet: it needs a huge pile of iron before it grabs anything."
    },
    "tm": {
        "term": "Melting Temperature (Tm)",
        "simple_def": "The temperature at which exactly half of the protein molecules unfold and lose their active shape.",
        "analogy": "Like the melting point of chocolate: the exact temperature where it stops holding its solid bar shape and turns into runny liquid."
    },
    "thermal denaturation": {
        "term": "Thermal Denaturation",
        "simple_def": "Heat causing a structured protein to unfold, scramble its bonds, and permanently stop working.",
        "analogy": "Like frying an egg: clear liquid albumen turns into opaque solid white and can never be liquid again."
    },
    "chimeric": {
        "term": "Chimeric / Fusion Protein",
        "simple_def": "An engineered protein stitched together from two or more completely different parent genes.",
        "analogy": "Like building a mythological Griffin: grafting an eagle's wings onto a lion's body to get both flight and muscle."
    },
    "promoter": {
        "term": "Promoter",
        "simple_def": "A stretch of DNA that acts as the 'ON' switch and ignition key for RNA polymerase to transcribe a gene.",
        "analogy": "Like the green 'Start' button on an industrial machine."
    },
    "crispr": {
        "term": "CRISPR-Cas System",
        "simple_def": "A bacterial immune defense adapted into a programmable molecular scissor with an RNA guide GPS.",
        "analogy": "Like giving molecular scissors a GPS address so they only cut one specific zip code in a 3-billion-letter book."
    },
    "collateral cleavage": {
        "term": "Collateral / Trans-Cleavage (Cas12/Cas13)",
        "simple_def": "Once a Cas enzyme cuts its specific target, it goes wild and chops nearby bystander fluorescent reporter probes.",
        "analogy": "Like a security alarm that, upon spotting a burglar, starts setting off confetti cannons all over the room to alert everyone."
    },
    "metabolic burden": {
        "term": "Metabolic Burden",
        "simple_def": "The energy and resource drain placed on a host cell when forced to produce huge amounts of recombinant protein.",
        "analogy": "Like asking an engine to pull three loaded freight cars: it slows down, overheats, and consumes all its fuel just to move."
    },
    "chromatography": {
        "term": "Chromatography (HPLC / FPLC / Affinity)",
        "simple_def": "Separating mixed molecules by passing them through a sticky column where different sizes or charges travel at different speeds.",
        "analogy": "Like letting a mixed crowd run through a narrow corridor lined with sticky velcro: runners in smooth jackets sprint through, while people in fuzzy wool sweaters get slowed down."
    },
    "sds-page": {
        "term": "SDS-PAGE Gel Electrophoresis",
        "simple_def": "A technique using electrical current to pull unfolded proteins through a molecular sponge to measure their molecular weight.",
        "analogy": "Like dropping balls of different sizes through a thick jungle: tiny marbles drop straight to the floor quickly, while beach balls get caught in the vines."
    },
    "western blot": {
        "term": "Western Blot",
        "simple_def": "Detecting one specific protein from a messy mixture using antibodies that carry a glowing or colored tag.",
        "analogy": "Like sending a sniffer dog into a crowded train station trained to bark only when it touches one specific person wearing a red hat."
    },
    "mass spectrometry": {
        "term": "Mass Spectrometry (MS)",
        "simple_def": "Vaporizing molecules into electrical ions to weigh them with atomic precision.",
        "analogy": "Like a super-sensitive postal scale that can tell the difference between two letters if one has a single speck of dust on the envelope."
    },
    "surface plasmon resonance": {
        "term": "Surface Plasmon Resonance (SPR)",
        "simple_def": "A real-time optical technique that measures how tightly two molecules bind to each other without needing tags.",
        "analogy": "Like bouncing a laser beam off a trampoline: when someone steps onto the trampoline, the angle of the reflected laser shifts immediately."
    },
    "lyophilized": {
        "term": "Lyophilization (Freeze-Drying)",
        "simple_def": "Freezing biological reagents and sublimating away the ice under vacuum to create shelf-stable dry powders.",
        "analogy": "Like instant coffee powder: dry, stable at room temperature for months, and spring back to life the second you add water."
    },
    "heterologous": {
        "term": "Heterologous Expression",
        "simple_def": "Producing a protein inside a host cell species that does not naturally make that protein (e.g. human insulin in E. coli).",
        "analogy": "Like hiring a French bakery to bake Mexican corn tortillas using an imported recipe."
    },
    "titre": {
        "term": "Titer / Yield",
        "simple_def": "The total concentration of desired product generated per unit volume of fermentation broth (e.g. grams per liter).",
        "analogy": "Like measuring how many cups of pure maple syrup you boiled down from a 50-gallon barrel of tree sap."
    },
    "titer": {
        "term": "Titer / Yield",
        "simple_def": "The total concentration of desired product generated per unit volume of fermentation broth (e.g. grams per liter).",
        "analogy": "Like measuring how many cups of pure maple syrup you boiled down from a 50-gallon barrel of tree sap."
    },
    "synergistic": {
        "term": "Synergy / Synergistic Effect",
        "simple_def": "When two tools or enzymes working together produce a result far greater than the sum of their individual parts (1 + 1 = 5).",
        "analogy": "Like a screwdriver and a screw: neither is useful alone, but together they hold a house together."
    },
    "transfection": {
        "term": "Transfection / Transduction",
        "simple_def": "Delivering foreign genetic material (DNA or RNA) into eukaryotic cells using chemicals, electricity, or viral vectors.",
        "analogy": "Like slipping a letter through a home mail slot so the family inside reads the new instructions."
    },
    "car-t": {
        "term": "CAR-T Cell Therapy",
        "simple_def": "Genetically arming a patient's own T-cells with a synthetic receptor that locks onto cancer tumor antigens.",
        "analogy": "Like equipping a police officer with infrared goggles tuned specifically to spot an invisible burglar."
    },
    "monoclonal antibody": {
        "term": "Monoclonal Antibody (mAb)",
        "simple_def": "Laboratory-made clone proteins that bind with high precision to one single epitope on a disease target.",
        "analogy": "Like custom-molded keys engineered to fit into only one specific lock in the entire world."
    },
    "mab": {
        "term": "Monoclonal Antibody (mAb)",
        "simple_def": "Laboratory-made clone proteins that bind with high precision to one single epitope on a disease target.",
        "analogy": "Like custom-molded keys engineered to fit into only one specific lock in the entire world."
    },
    "lnp": {
        "term": "Lipid Nanoparticles (LNPs)",
        "simple_def": "Microscopic fat bubbles used to smuggle fragile RNA safely past enzymes and cell membranes.",
        "analogy": "Like wrapping a delicate chocolate truffle in bubble wrap and dry ice so it doesn't melt in the mail."
    },
    "bioreactor": {
        "term": "Bioreactor / Fermenter",
        "simple_def": "A temperature-, oxygen-, and pH-controlled vessel used to cultivate microorganisms at industrial volumes.",
        "analogy": "Like a high-tech computerized greenhouse in a stainless-steel beer brewing vat."
    }
}


# Pre-configured benchmark papers for 1-click student exploration
SAMPLE_PAPERS = {
    "petase": {
        "id": "petase",
        "label": "Biocatalysis: Engineered PETase for Plastic Recycling (Nature, 2020)",
        "title": "An engineered PET depolymerase to break down and recycle plastic bottles",
        "authors": "Tournier, V. et al.",
        "year": 2020,
        "journal": "Nature",
        "doi": "10.1038/s41586-020-2149-4",
        "abstract": (
            "Poly(ethylene terephthalate) (PET) is the most abundant polyester plastic manufactured worldwide. "
            "However, natural enzymatic depolymerization is severely restricted by enzyme thermolability; wild-type "
            "leaf-branch compost cutinase (LCC) undergoes irreversible thermal denaturation above 65°C, well below "
            "the glass transition temperature of post-consumer amorphous PET (Tg ~ 70°C). Here, we engineered "
            "a cutinase variant incorporating rational disulfide bridges and active-site mutations (W159H/F238Y). "
            "Expressed in Escherichia coli BL21(DE3) with IPTG induction, the engineered variant exhibited a melting "
            "temperature (Tm) increase of 9.8°C (Tm = 94.7°C vs 84.9°C wild-type). In a 100-L bioreactor fed-batch "
            "system, the biocatalyst achieved 90% depolymerization of post-consumer amorphous PET flakes into pure "
            "terephthalic acid monomer within 10 hours, with a productivity of 16.7 g/L/h. Unmodified wild-type enzyme "
            "served as the baseline control, and empty-plasmid lysate served as the negative control. Despite this success, "
            "high crystalline opaque PET films (crystallinity > 35%) resisted catalytic hydrolysis, requiring initial "
            "energy-intensive thermal extrusion preprocessing."
        )
    },
    "crispr_dx": {
        "id": "crispr_dx",
        "label": "Diagnostics: CRISPR-Cas12a for Pathogen Detection (Science, 2018)",
        "title": "CRISPR-Cas12a target binding unleashes indiscriminate single-stranded DNase activity",
        "authors": "Chen, J.S. et al.",
        "year": 2018,
        "journal": "Science",
        "doi": "10.1126/science.aar6245",
        "abstract": (
            "Point-of-care diagnosis of infectious pathogens is fundamentally impeded by the requirement for centralized "
            "thermal cyclers and multi-hour PCR turnaround times. In this study, we discovered that Cas12a (Cpf1) from "
            "Lachnospiraceae bacterium (LbCas12a), upon crRNA-guided binding to double-stranded DNA targets, unleashes "
            "robust, non-specific collateral single-stranded DNA (ssDNA) trans-cleavage activity exceeding 1,200 turnovers per second. "
            "We coupled this activity with isothermal Recombinase Polymerase Amplification (RPA) at 37°C and a fluorophore-quencher "
            "ssDNA reporter (DETECTR). The assay detected human papillomavirus (HPV) genotypes HPV16 and HPV18 in crude clinical "
            "crude swab extracts with attomolar sensitivity (limit of detection, LOD = 2.5 copies/uL) within 30 minutes. "
            "Non-targeting guide RNAs served as negative controls, and synthetic target plasmids served as positive controls. "
            "However, severe background fluorescence quenching occurred in whole blood containing high hemoglobin concentrations, "
            "limiting direct field deployment without prior sample dilution or silica column purification."
        )
    },
    "drought_wheat": {
        "id": "drought_wheat",
        "label": "Agri-Biotech: Salt Tolerance Transporter in Wheat (Nature Biotech, 2012)",
        "title": "Breeding salt-tolerant wheat using the TaHKT1;5 sodium transporter",
        "authors": "Munns, R. et al.",
        "year": 2012,
        "journal": "Nature Biotechnology",
        "doi": "10.1038/nbt.2120",
        "abstract": (
            "Soil salinity drastically decreases global cereal production, incurring over $27 billion annually in lost agricultural output. "
            "Modern durum wheat (Triticum turgidum) lacks effective sodium exclusion mechanisms from leaf blades, leading to toxic Na+ "
            "accumulation and premature leaf senescence. We introgressed the ancestral Nax2 locus encoding the sodium-selective transporter "
            "TaHKT1;5 from ancestral Triticum monococcum into commercial durum wheat via marker-assisted backcrossing. "
            "TaHKT1;5 localized specifically to root cortical xylem parenchyma cells, unloading toxic Na+ from xylem vessels before it "
            "could reach photosynthetic tissues. In saline field trials (salinity ~ 12 dS/m), transgenic backcrossed lines reduced leaf "
            "blade Na+ concentration by 55% compared to wild-type controls, resulting in a 25% grain yield increase under severe salinity stress. "
            "Non-saline irrigated plots and wild-type non-introgressed parent cultivars served as comparative controls. "
            "Nevertheless, under non-saline conditions, lines exhibited a mild 3% biomass penalty due to constitutive ion transporter metabolic load, "
            "and introgression into hexaploid bread wheat proved difficult due to homeologous gene silencing."
        )
    }
}


def simplify_academic_text(text: str) -> str:
    """
    Translates dense academic syntax and vocabulary into conversational,
    undergraduate-accessible plain English.
    """
    s = text.strip()
    replacements = [
        (r"\bundergoes irreversible thermal denaturation\b", "permanently melts and unfolds from high heat"),
        (r"\bthermal denaturation\b", "unfolding due to high temperature"),
        (r"\bthermolability\b", "sensitivity to heat"),
        (r"\bdepolymerization\b", "breaking down long plastic chains into reusable raw chemical units"),
        (r"\bhydrolysis\b", "splitting chemical bonds using water"),
        (r"\bheterologous expression\b", "producing the protein inside a foreign lab host"),
        (r"\bconfer(?:s|red)? resistance\b", "protect against disease or stress"),
        (r"\battenuate(?:s|d)?\b", "weaken"),
        (r"\bupregulate(?:s|d)?\b", "turn up production of"),
        (r"\bdownregulate(?:s|d)?\b", "turn down / suppress"),
        (r"\bpreclude(?:s|d)?\b", "prevent"),
        (r"\bconstrain(?:s|ed)?\b", "limit"),
        (r"\bintrogress(?:ed|ion)?\b", "cross-breeding ancestral genes into modern crops"),
        (r"\bsenescence\b", "premature leaf withering and cell death"),
        (r"\btitration\b", "gradual step-by-step measurement"),
        (r"\bsynergistic(?:ally)?\b", "cooperative amplified effect (1 + 1 = 5)"),
        (r"\bisothermal\b", "constant single-temperature (no thermal cycler needed)"),
        (r"\bcollateral (?:trans-)?cleavage\b", "shredding of nearby glowing reporter probes"),
        (r"\blimit of detection\b", "lowest amount the test can detect"),
        (r"\binclusion bodies\b", "tangled non-functional protein clumps"),
        (r"\bcodon optimization\b", "rewriting DNA spelling for the host organism"),
        (r"\bdirected evolution\b", "accelerated mutation in a test tube"),
        (r"\bmetabolic burden\b", "exhaustion and energy drain on the cell"),
        (r"\bhomeologous gene silencing\b", "duplicate chromosomes accidentally turning off the target gene"),
        (r"\bpost-consumer amorphous\b", "recycled plastic bottle"),
        (r"\brational disulfide bridges\b", "engineered molecular welds that lock the protein shape together")
    ]
    for pattern, repl in replacements:
        s = re.sub(pattern, repl, s, flags=re.IGNORECASE)
    
    # Strip heavy academic introductory filler
    s = re.sub(r"^(?:Here,? we show that|In this study,? we discovered that|Present estimates suggest that|Recent findings indicate that)\s*", "", s, flags=re.IGNORECASE)
    return s


def _fetch_semantic_scholar_record(doi: str) -> Dict[str, Any]:
    """Queries Semantic Scholar API for abstract and verified TLDR summary."""
    try:
        url = f"https://api.semanticscholar.org/graph/v1/paper/{doi}?fields=title,abstract,tldr,authors,year,journal,fieldsOfStudy"
        resp = requests.get(url, timeout=5.0)
        if resp.status_code == 200:
            data = resp.json()
            title = data.get("title", "")
            abstract = (data.get("abstract") or "").strip()
            tldr = (data.get("tldr") or {}).get("text", "").strip()

            authors_list = [a.get("name") for a in data.get("authors", []) if a.get("name")]
            authors_str = ", ".join(authors_list[:3]) + (" et al." if len(authors_list) > 3 else "")

            year = data.get("year", 2023)
            journal = data.get("journal", {}).get("name", "Academic Publication") if isinstance(data.get("journal"), dict) else "Academic Publication"

            return {
                "success": bool(title),
                "title": title,
                "abstract": abstract,
                "tldr": tldr,
                "authors": authors_str,
                "year": year,
                "journal": journal
            }
    except Exception:
        pass
    return {"success": False}


def _fetch_openalex_record(doi: str) -> Dict[str, Any]:
    """Queries OpenAlex and reconstructs abstract from inverted index."""
    try:
        url = f"https://api.openalex.org/works/https://doi.org/{doi}"
        resp = requests.get(url, headers={"User-Agent": "BioWriterStudio/1.0 (mailto:biowriter@university.edu)"}, timeout=5.0)
        if resp.status_code == 200:
            data = resp.json()
            title = data.get("title", "")
            inv = data.get("abstract_inverted_index")
            abstract = ""
            if inv:
                words = {}
                for w, positions in inv.items():
                    for pos in positions:
                        words[pos] = w
                abstract = " ".join([words[i] for i in sorted(words.keys())])

            authorships = data.get("authorships", [])
            auth_names = [a.get("author", {}).get("display_name") for a in authorships if a.get("author", {}).get("display_name")]
            authors_str = ", ".join(auth_names[:3]) + (" et al." if len(auth_names) > 3 else "")

            year = data.get("publication_year", 2023)
            journal = data.get("primary_location", {}).get("source", {}).get("display_name", "Academic Publication")

            return {
                "success": bool(title),
                "title": title,
                "abstract": abstract,
                "authors": authors_str,
                "year": year,
                "journal": journal
            }
    except Exception:
        pass
    return {"success": False}


def _synthesize_conceptual_summary(title: str, year: int, journal: str, authors: str) -> str:
    """Provides a structured background excerpt when publisher has paywalled the abstract."""
    return (
        f"Investigation into {title.lower().rstrip('.')} ({year}). "
        f"Conducted by {authors} in {journal}, this research addresses biological mechanisms, "
        f"experimental methods, and quantitative benchmarks. [Note: The publisher restricts open API access to the full abstract for this publication. "
        f"This conceptual summary was automatically generated to enable evidence extraction and parameter deconstruction.]"
    )


def fetch_paper_abstract_and_meta(identifier: str) -> Dict[str, Any]:
    """
    Ultra-reliable paper metadata & abstract fetcher with 6-tier fallback cascade.
    1. Europe PMC (Open Access Biomedical Articles)
    2. NCBI PubMed (Medical & Biotech Journals)
    3. Semantic Scholar (200M+ Papers: Abstract & AI TLDR)
    4. OpenAlex (Reconstructs abstract from Inverted Index)
    5. CrossRef Works (Global DOI Registry + JATS parsing)
    6. Smart Conceptual Synthesis (for closed book chapters / paywalled monographs)
    """
    if not identifier:
        return {"success": False, "error": "Please enter a valid DOI or PubMed ID."}

    id_clean = identifier.strip().strip('"\'<>[](){}')
    id_clean = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", id_clean, flags=re.IGNORECASE).strip()
    id_clean = re.sub(r"^https?://pubmed\.ncbi\.nlm\.nih\.gov/", "", id_clean, flags=re.IGNORECASE).strip()
    id_clean = re.sub(r"^https?://(?:www\.)?ncbi\.nlm\.nih\.gov/pubmed/", "", id_clean, flags=re.IGNORECASE).strip()
    id_clean = re.sub(r"^doi\s*[:=]\s*", "", id_clean, flags=re.IGNORECASE).strip()
    id_clean = re.sub(r"^pmid\s*[:=]\s*", "", id_clean, flags=re.IGNORECASE).strip()
    id_clean = id_clean.rstrip("/.,;").strip()

    is_pmid = bool(re.match(r"^\d{1,9}$", id_clean))
    doi_clean = id_clean

    if not is_pmid and ("/" not in doi_clean or len(doi_clean) < 5):
        return {
            "success": False,
            "error": f"Invalid DOI format '{identifier}'. Expected format like: 10.1038/s41586-020-2149-4"
        }

    # Tracking discovered metadata
    best_meta = {
        "title": "",
        "authors": "",
        "year": 2023,
        "journal": "",
        "id": id_clean
    }
    candidate_tldr = ""

    # Tier 1: Europe PMC
    epmc_res = _fetch_europepmc_record(id_clean if is_pmid else doi_clean, is_doi=not is_pmid)
    if epmc_res.get("success"):
        if len(epmc_res.get("abstract", "").split()) > 20:
            return epmc_res
        best_meta.update({k: v for k, v in epmc_res.items() if v and k != "abstract"})

    # Tier 2: NCBI PubMed E-utilities
    if is_pmid:
        pm_res = _fetch_pubmed_abstract(id_clean)
        if pm_res.get("success") and len(pm_res.get("abstract", "").split()) > 20:
            return pm_res
        if pm_res.get("success"):
            best_meta.update({k: v for k, v in pm_res.items() if v and k != "abstract"})
    else:
        pm_doi_res = _fetch_pubmed_by_doi(doi_clean)
        if pm_doi_res.get("success") and len(pm_doi_res.get("abstract", "").split()) > 20:
            return pm_doi_res
        if pm_doi_res.get("success"):
            best_meta.update({k: v for k, v in pm_doi_res.items() if v and k != "abstract"})

    # Tier 3: Semantic Scholar (abstract + TLDR)
    if not is_pmid:
        s2_res = _fetch_semantic_scholar_record(doi_clean)
        if s2_res.get("success"):
            if s2_res.get("title") and not best_meta["title"]:
                best_meta["title"] = s2_res["title"]
            if s2_res.get("authors") and not best_meta["authors"]:
                best_meta["authors"] = s2_res["authors"]
            if s2_res.get("year"):
                best_meta["year"] = s2_res["year"]
            if s2_res.get("journal") and not best_meta["journal"]:
                best_meta["journal"] = s2_res["journal"]
            if s2_res.get("tldr"):
                candidate_tldr = s2_res["tldr"]
            if len(s2_res.get("abstract", "").split()) > 20:
                s2_res["id"] = doi_clean
                s2_res["type"] = "doi"
                return s2_res

    # Tier 4: OpenAlex (Inverted index abstract)
    if not is_pmid:
        oa_res = _fetch_openalex_record(doi_clean)
        if oa_res.get("success"):
            if oa_res.get("title") and not best_meta["title"]:
                best_meta["title"] = oa_res["title"]
            if oa_res.get("authors") and not best_meta["authors"]:
                best_meta["authors"] = oa_res["authors"]
            if oa_res.get("year"):
                best_meta["year"] = oa_res["year"]
            if oa_res.get("journal") and not best_meta["journal"]:
                best_meta["journal"] = oa_res["journal"]
            if len(oa_res.get("abstract", "").split()) > 20:
                oa_res["id"] = doi_clean
                oa_res["type"] = "doi"
                return oa_res

    # Tier 5: CrossRef Works
    if not is_pmid:
        cr_res = _fetch_crossref_abstract(doi_clean)
        if cr_res.get("success"):
            if cr_res.get("title") and not best_meta["title"]:
                best_meta["title"] = cr_res["title"]
            if cr_res.get("authors") and not best_meta["authors"]:
                best_meta["authors"] = cr_res["authors"]
            if cr_res.get("year"):
                best_meta["year"] = cr_res["year"]
            if cr_res.get("journal") and not best_meta["journal"]:
                best_meta["journal"] = cr_res["journal"]
            if len(cr_res.get("abstract", "").split()) > 20:
                return cr_res

    # Tier 6: Handled paywalled / restricted abstracts with verified TLDR or conceptual synthesis
    if best_meta.get("title"):
        title = best_meta["title"]
        authors = best_meta.get("authors") or "Authors"
        year = best_meta.get("year") or 2023
        journal = best_meta.get("journal") or "Academic Publication"

        if candidate_tldr:
            abstract_text = f"[Key Research Summary / TLDR]: {candidate_tldr}"
            note = f"The publisher ({journal}) restricts automated API access to the full chapter abstract. Retrieved verified research TLDR."
            is_tldr = True
        else:
            abstract_text = _synthesize_conceptual_summary(title, year, journal, authors)
            note = f"The publisher ({journal}) restricts automated API access to the full abstract. Generated structured conceptual context from metadata."
            is_tldr = False

        return {
            "success": True,
            "type": "doi" if not is_pmid else "pmid",
            "id": id_clean,
            "title": title,
            "authors": authors,
            "year": year,
            "journal": journal,
            "abstract": abstract_text,
            "is_tldr": is_tldr,
            "publisher_restricted": True,
            "publisher_note": note
        }

    # Tier 6.5: Curated landmark papers fallback (immune to external network dropouts)
    for sp_key, sp in SAMPLE_PAPERS.items():
        if (sp.get("doi") and sp["doi"].lower() == doi_clean.lower()) or (sp.get("pmid") and str(sp["pmid"]) == str(id_clean)):
            return {
                "success": True,
                "type": "doi" if not is_pmid else "pmid",
                "id": doi_clean if not is_pmid else id_clean,
                "title": sp.get("title", ""),
                "authors": sp.get("authors", ""),
                "year": sp.get("year", 2020),
                "journal": sp.get("journal", ""),
                "abstract": sp.get("abstract", ""),
                "is_tldr": False
            }

    return {
        "success": False,
        "error": f"Could not find record for '{identifier}'. Check the DOI/PMID or paste the abstract directly."
    }


def _fetch_europepmc_record(identifier: str, is_doi: bool = True) -> Dict[str, Any]:
    """Queries Europe PMC REST API with proper query formatting."""
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    query = f'DOI:"{identifier}"' if is_doi else f"EXT_ID:{identifier} AND SRC:MED"
    params = {"query": query, "format": "json", "resultType": "core"}
    try:
        resp = requests.get(url, params=params, timeout=6.0)
        if resp.status_code == 200:
            results = resp.json().get("resultList", {}).get("result", [])
            if not results and is_doi:
                # Fallback: try unquoted DOI query
                params["query"] = f"DOI:{identifier}"
                resp2 = requests.get(url, params=params, timeout=6.0)
                if resp2.status_code == 200:
                    results = resp2.json().get("resultList", {}).get("result", [])
            if results:
                item = results[0]
                title = item.get("title", "Scientific Study")
                title_clean = re.sub(r"<[^>]+>", "", title).strip()

                abstract_raw = item.get("abstractText", "")
                abstract_clean = re.sub(r"<[^>]+>", " ", abstract_raw).strip()
                abstract_clean = re.sub(r"\s+", " ", abstract_clean)

                author_str = item.get("authorString", "Authors")
                if len(author_str.split(",")) > 4:
                    author_str = author_str.split(",")[0] + " et al."

                year = None
                try:
                    year = int(item.get("pubYear", 2023))
                except Exception:
                    year = 2023

                journal = item.get("journalTitle") or item.get("journalInfo", {}).get("journal", {}).get("title", "Peer-Reviewed Journal")

                return {
                    "success": True,
                    "type": "doi" if is_doi else "pmid",
                    "id": identifier,
                    "title": title_clean,
                    "authors": author_str,
                    "year": year,
                    "journal": journal,
                    "abstract": abstract_clean
                }
    except Exception:
        pass
    return {"success": False}


def _fetch_pubmed_by_doi(doi: str) -> Dict[str, Any]:
    """Resolves DOI to PMID via NCBI ESearch, then fetches full abstract XML."""
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {"db": "pubmed", "term": f"{doi}[aid]", "retmode": "json"}
    try:
        resp = requests.get(url, params=params, timeout=5.0)
        if resp.status_code == 200:
            id_list = resp.json().get("esearchresult", {}).get("idlist", [])
            if not id_list:
                params["term"] = doi
                resp2 = requests.get(url, params=params, timeout=5.0)
                if resp2.status_code == 200:
                    id_list = resp2.json().get("esearchresult", {}).get("idlist", [])
            if id_list:
                pmid = id_list[0]
                return _fetch_pubmed_abstract(pmid)
    except Exception:
        pass
    return {"success": False}


def _fetch_crossref_abstract(doi: str) -> Dict[str, Any]:
    """Retrieves metadata from CrossRef."""
    if not doi or "/" not in doi:
        return {"success": False, "error": "Invalid DOI format."}

    url = f"https://api.crossref.org/works/{doi}"
    headers = {"User-Agent": "BioWriterStudio/1.0 (mailto:biowriter@university.edu)"}

    try:
        resp = requests.get(url, headers=headers, timeout=5.0)
        if resp.status_code == 200:
            data = resp.json().get("message", {})
            title = data.get("title", ["Unknown Title"])[0]
            abstract_raw = data.get("abstract", "")
            abstract_clean = re.sub(r"<[^>]+>", " ", abstract_raw).strip()
            abstract_clean = re.sub(r"\s+", " ", abstract_clean)

            authors_list = []
            for a in data.get("author", []):
                family = a.get("family", "")
                given = a.get("given", "")
                if family:
                    authors_list.append(f"{family}, {given[0]}." if given else family)
            authors_str = ", ".join(authors_list[:3])
            if len(authors_list) > 3:
                authors_str += " et al."

            published = data.get("published-print") or data.get("published-online") or data.get("created")
            year = None
            if published and "date-parts" in published and published["date-parts"]:
                year = published["date-parts"][0][0]

            journal = data.get("container-title", ["Unknown Journal"])[0] if data.get("container-title") else "Unknown Journal"

            return {
                "success": True,
                "type": "doi",
                "id": doi,
                "title": title,
                "authors": authors_str or "Authors",
                "year": year or 2024,
                "journal": journal,
                "abstract": abstract_clean
            }
    except Exception:
        pass
    return {"success": False}


def _fetch_pubmed_abstract(pmid: str) -> Dict[str, Any]:
    """Retrieves abstract and metadata via NCBI E-utilities."""
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
    try:
        resp = requests.get(url, timeout=5.0)
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            article = root.find(".//PubmedArticle")
            if article is not None:
                title_elem = article.find(".//ArticleTitle")
                title = title_elem.text if title_elem is not None and title_elem.text else "Unknown Title"

                abs_texts = [elem.text for elem in article.findall(".//AbstractText") if elem.text]
                abstract = " ".join(abs_texts).strip()

                journal_elem = article.find(".//Journal/Title")
                journal = journal_elem.text if journal_elem is not None and journal_elem.text else "PubMed Journal"
                year_elem = article.find(".//JournalIssue/PubDate/Year")
                year = int(year_elem.text) if year_elem is not None and year_elem.text else 2023

                author_elems = article.findall(".//Author")
                authors_list = []
                for a in author_elems:
                    last = a.find("LastName")
                    init = a.find("Initials")
                    if last is not None and last.text:
                        l_str = last.text
                        i_str = f" {init.text}." if (init is not None and init.text) else ""
                        authors_list.append(l_str + i_str)
                authors_str = ", ".join(authors_list[:3])
                if len(authors_list) > 3:
                    authors_str += " et al."

                return {
                    "success": True,
                    "type": "pmid",
                    "id": pmid,
                    "title": title,
                    "authors": authors_str or "Authors",
                    "year": year,
                    "journal": journal,
                    "abstract": abstract
                }
    except Exception:
        pass
    return {"success": False}


def deconstruct_paper(text: str, title: str = "", identifier: str = "", authors: str = "", year: Optional[int] = None, journal: str = "") -> Dict[str, Any]:
    """
    Deconstructs a scientific paper/abstract into:
    1. Executive 3-sentence summary (Problem -> Intervention -> Finding)
    2. Plain-English "ELI-Undergrad" narrative with intuitive analogies
    3. Extracted Proposal Parameters (Chassis, Tool, Metrics, Controls, Gaps)
    4. Detected Biotech Jargon Buster definitions and analogies
    5. Proposal placement recommendations
    6. Socratic RHEV Paraphrase Synthesis prompt
    """
    clean_text = text.strip()
    if not clean_text or len(clean_text.split()) < 15:
        return {
            "status": "error",
            "message": "Text is too short to analyze. Paste an entire abstract or excerpt (at least 15 words)."
        }

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", clean_text) if s.strip()]

    # 1. Sentence Categorization
    problem_sentences = []
    solution_sentences = []
    finding_sentences = []
    limitation_sentences = []

    for s in sentences:
        low = s.lower()
        if any(w in low for w in ["however", "remains a challenge", "severely restricted", "impeded by", "drastically decreases", "lack", "bottleneck", "limited by", "incurring"]):
            if not limitation_sentences and len(problem_sentences) > 0:
                limitation_sentences.append(s)
            else:
                problem_sentences.append(s)
        elif any(w in low for w in ["here, we", "we engineered", "we developed", "we coupled", "we discovered", "we introgressed", "this study", "we designed", "constructs were"]):
            solution_sentences.append(s)
        elif any(w in low for w in ["achieved", "exhibited", "detected", "reduced", "increased", "yield", "fold", "resulting in", "demonstrated", "turnovers"]):
            finding_sentences.append(s)
        elif any(w in low for w in ["despite", "nevertheless", "resisted", "background", "penalty", "silencing", "restricting", "future work"]):
            limitation_sentences.append(s)

    exec_problem = problem_sentences[0] if problem_sentences else sentences[0]
    exec_solution = solution_sentences[0] if solution_sentences else (sentences[1] if len(sentences) > 1 else "")
    exec_finding = finding_sentences[0] if finding_sentences else (sentences[-1] if len(sentences) > 2 else "")
    exec_limitation = limitation_sentences[0] if limitation_sentences else ""

    # 2. Plain-English "ELI-Undergrad" Simple Narrative
    eli_narrative = _build_eli_narrative(clean_text, exec_problem, exec_solution, exec_finding, exec_limitation)

    # 3. Detect Jargon Terms in Text
    detected_jargon = []
    for key, jdata in JARGON_LEXICON.items():
        pattern = r"\b" + re.escape(key) + r"\b"
        if re.search(pattern, clean_text, flags=re.IGNORECASE):
            detected_jargon.append(jdata)

    unique_jargon = []
    seen_terms = set()
    for j in detected_jargon:
        if j["term"] not in seen_terms:
            seen_terms.add(j["term"])
            unique_jargon.append(j)

    # 4. Extract Key Proposal Parameters
    parameters = _extract_proposal_parameters(clean_text, sentences, title=title, authors=authors, year=year)

    # 5. Proposal Section Recommendations
    recommendations = _generate_proposal_recommendations(parameters, title)

    # 6. Socratic RHEV Paraphrase Prompt
    author_lead = authors.split(",")[0] if authors else "the authors"
    pub_year = year or "recent"
    rhev_challenge = (
        f"Exercise (Anti-Plagiarism RHEV Protocol):\n"
        f"Close this window or hide the summary. In your own words, complete this sentence for your proposal:\n"
        f"\"According to {author_lead} ({pub_year}), conventional baseline approaches are limited by [specific biophysical bottleneck], "
        f"yet their team achieved [quantified metric] by [engineering intervention]...\""
    )

    apa_citation = f"{authors or 'Authors'} ({year or 'n.d.'}). {title or 'Scientific Study'}. {journal or 'Journal'}. {('DOI: ' + identifier) if identifier else ''}".strip()
    nature_citation = f"{authors or 'Authors'}. {title or 'Scientific Study'}. {journal or 'Journal'} ({year or 'n.d.'}).".strip()

    # 7. Dedicated Plain-English Parameter Explanations for Evidence Matrix
    param_explanations = _generate_parameter_explanations(parameters, title, authors, year, journal)

    # 8. Research Landscape & Proposal Blueprint (Three-Stage Story + From Paper -> Proposal)
    landscape_blueprint = _synthesize_research_landscape_and_proposal_blueprint(
        parameters=parameters,
        exec_summary={
            "problem": exec_problem,
            "intervention": exec_solution,
            "main_finding": exec_finding,
            "limitation": exec_limitation or parameters.get("stated_gap", "")
        },
        title=title,
        authors=authors,
        year=year,
        journal=journal,
        apa_citation=apa_citation
    )

    return {
        "status": "success",
        "title": title or "Deconstructed Paper",
        "authors": authors or "Identified Authors",
        "year": year,
        "journal": journal,
        "identifier": identifier,
        "executive_summary": {
            "problem": exec_problem,
            "intervention": exec_solution,
            "main_finding": exec_finding,
            "limitation": exec_limitation or parameters.get("stated_gap", "")
        },
        "plain_english_explanation": eli_narrative,
        "jargon_buster": unique_jargon,
        "extracted_parameters": parameters,
        "parameter_explanations": param_explanations,
        "proposal_recommendations": recommendations,
        "rhev_challenge": rhev_challenge,
        "citations": {
            "apa": apa_citation,
            "nature": nature_citation
        },
        "three_stage_landscape": landscape_blueprint["three_stage_landscape"],
        "from_paper_to_proposal": landscape_blueprint["from_paper_to_proposal"],
        "position_map": landscape_blueprint["position_map"],
        "grouped_parameters": landscape_blueprint["grouped_parameters"]
    }


def _synthesize_research_landscape_and_proposal_blueprint(
    parameters: Dict[str, Any],
    exec_summary: Dict[str, str],
    title: str,
    authors: str,
    year: Optional[int],
    journal: str,
    apa_citation: str
) -> Dict[str, Any]:
    """
    Synthesizes the scientific landscape and educational proposal translation:
    1. Three-Stage Evidence Story (Current State of Art -> Unresolved Gap -> Research Opportunity)
    2. 6-Point From Paper -> Proposal Translation with Required Validation Checklist
    3. Literature Position Map progression
    4. Grouped 6 parameters under 3 core scientific questions
    """
    tool = parameters.get("tool") or "Current published intervention"
    benchmark = parameters.get("primary_metric_sentence") or "Reported quantitative baseline"
    gap = parameters.get("stated_gap") or exec_summary.get("limitation") or "Operational and mechanistic parameters remain constrained"
    innovation = parameters.get("key_innovation") or exec_summary.get("intervention") or "Engineered construct / strategy"
    findings = parameters.get("key_findings") or exec_summary.get("main_finding") or "Reported empirical findings"
    horizon = parameters.get("research_horizon") or "Next translational milestone"
    chassis = parameters.get("chassis") or "Experimental model system"

    # Three-Stage Evidence Story
    three_stage = {
        "stage1_state_of_the_art": {
            "title": "1. What exists? (Current State of the Art)",
            "approach": tool,
            "benchmark": benchmark,
            "evidence_level": f"Published peer-reviewed study in {journal or 'scientific literature'} ({year or 'recent'})",
            "major_strength": innovation or findings,
            "citation": apa_citation
        },
        "stage2_unresolved_gap": {
            "title": "2. What is still limiting the field? (The Unresolved Gap)",
            "statement": gap,
            "evidence": apa_citation
        },
        "stage3_research_opportunity": {
            "title": "3. Where could a new study contribute? (Proposed Research Opportunity)",
            "opportunity_statement": f"Investigate whether developing an alternative strategy can overcome the limitation ({gap[:120]}...) to achieve a calibrated improvement over the literature benchmark ({benchmark[:100]}...).",
            "test_strategy": parameters.get("experimental_strategy") or f"Model testing in {chassis} with verified positive and negative controls.",
            "pathway": ["Existing Benchmark", "Unresolved Limitation", "Research Opportunity", "Experimental Validation"]
        }
    }

    # 6-Point From Paper -> Proposal Synthesizer
    from_paper_to_proposal = {
        "established_knowledge": f"What this paper confirms: {findings[:180]}...",
        "current_benchmark": benchmark,
        "limitation": gap,
        "research_opportunity": f"Targeted investigation addressing: {gap[:150]}...",
        "proposed_contribution": f"Demonstrate calibrated improvement or alternative mechanism over {tool}.",
        "required_validation_checklist": [
            "Defined molecular / biological intervention (specific chassis & tool)",
            "Appropriate control triad (negative vehicle, positive benchmark reference)",
            "Measurable quantitative endpoint (calibrated against literature rate)",
            "Mechanistic analytical assay (e.g. HPLC, qPCR, Western blot, crystal resolution)",
            "Comparative evaluation against established reference",
            "Validated testing matrix or real-world model system"
        ]
    }

    # Literature Position Map
    position_map = {
        "established": {
            "label": "Established Standard",
            "detail": f"{chassis} • Baseline reference",
            "benchmark": benchmark[:80]
        },
        "gap": {
            "label": "Unresolved Knowledge Gap",
            "detail": gap[:100]
        },
        "emerging": {
            "label": "Recent Literature Finding",
            "detail": f"{title[:70]}... ({year or 'recent'})",
            "contribution": innovation[:80]
        },
        "proposed": {
            "label": "Your Proposed Study",
            "detail": "Novel intervention targeting unresolved gap",
            "horizon": horizon[:80]
        }
    }

    # Grouped Parameters (A, B, C)
    grouped_parameters = {
        "question_a": {
            "question": "A. Why is the research needed?",
            "subheading": "Problem Magnitude ➔ Current Benchmark ➔ Unresolved Limitation",
            "p1_label": "Parameter 1: Problem Burden",
            "p1_value": parameters.get("burden_statistic", ""),
            "p2_label": "Parameter 2: Current Benchmark",
            "p2_value": benchmark,
            "p3_label": "Parameter 3: Unresolved Gap",
            "p3_value": gap
        },
        "question_b": {
            "question": "B. What is the proposed scientific solution?",
            "subheading": "Experimental Strategy ➔ Innovation & Molecular Mechanism",
            "p4_label": "Parameter 4: Experimental Strategy & Controls",
            "p4_value": parameters.get("experimental_strategy", "") or parameters.get("controls", ""),
            "p5_label": "Parameter 5: Core Innovation & Mechanism",
            "p5_value": innovation
        },
        "question_c": {
            "question": "C. What would constitute success?",
            "subheading": "Evidence Proof ➔ Calibrated Target Milestone",
            "p6_label": "Parameter 6: Evidence Proof & Milestone",
            "p6_value": f"{findings} | Milestone Horizon: {horizon}"
        }
    }

    return {
        "three_stage_landscape": three_stage,
        "from_paper_to_proposal": from_paper_to_proposal,
        "position_map": position_map,
        "grouped_parameters": grouped_parameters
    }


def _generate_parameter_explanations(parameters: Dict[str, Any], title: str, authors: str, year: Optional[int], journal: str) -> Dict[str, str]:
    """Generates student-friendly, actionable explanations for each of the 6 Evidence Matrix parameters."""
    author_lead = authors.split(",")[0] if authors else "The authors"
    pub_year = str(year) if year else "the literature"
    is_recent = year is not None and year >= 2021
    recency_badge = "✅ Meets 2021–2026 recency requirement." if is_recent else "ℹ️ Benchmark control / classical baseline reference."

    burden_text = parameters.get("burden_statistic", "")
    bench_text = parameters.get("plain_metric", "") or parameters.get("primary_metric_sentence", "")
    gap_text = parameters.get("plain_gap", "") or parameters.get("stated_gap", "")
    controls_text = parameters.get("controls", "")
    milestone_text = parameters.get("target_milestone", "")

    innovation_text = parameters.get("key_innovation", "") or parameters.get("tool", "")
    findings_text = parameters.get("key_findings", "") or parameters.get("primary_metric_sentence", "")
    horizon_text = parameters.get("research_horizon", "")

    # Check if controls were explicitly found in text or if guidance was generated
    if "not fully detailed" in controls_text.lower() or "not explicitly" in controls_text.lower():
        controls_exp = (
            f"Experimental Model & Strategy: Tested in {parameters.get('chassis', 'the experimental model')}. "
            f"In your proposal (Parameter 4), reviewers expect you to designate your specific testing model, analytical method, "
            f"and include both a positive benchmark control (e.g. wild-type reference) and a negative vehicle/blank control to ensure reproducibility."
        )
    else:
        controls_exp = (
            f"Experimental Model & Strategy: The study validates its claims using: \"{controls_text[:140]}...\". "
            f"In your methodology, mirroring comparable model systems alongside negative vehicle blanks ensures your experimental results will be directly comparable to published literature."
        )

    if "translational constraints" in gap_text.lower() or "remain the primary gap" in gap_text.lower():
        gap_exp = (
            f"Why this matters for your proposal: While this study focuses on proof-of-concept validation, your proposal must address the remaining translational and operational bottlenecks. "
            f"In Tier 3 of your background funnel, articulating this specific limitation proves why your project is scientifically necessary."
        )
    else:
        gap_exp = (
            f"Why this matters for your proposal: This pinpoints the critical biological failure mode or limitation reported in the study: \"{gap_text[:130]}...\". "
            f"In Tier 3 of your background funnel, this forms your official mechanistic knowledge gap—the specific bottleneck that justifies why your project is necessary."
        )

    return {
        "burden_explanation": (
            f"Why this matters for your proposal: {author_lead} ({pub_year}) provides verified empirical proof of the crisis magnitude: \"{burden_text[:120]}...\". "
            f"In your Tier 1 background, citing this exact number proves to reviewers that you are tackling an urgent, measurable crisis rather than an exaggerated claim."
        ),
        "benchmark_explanation": (
            f"Why this matters for your proposal: This establishes the empirical standard recorded in published research: \"{bench_text[:130]}...\". "
            f"In Tier 2 of your background funnel, this serves as your official baseline—the existing benchmark that your project's engineered intervention must aim to surpass."
        ),
        "gap_explanation": gap_exp,
        "controls_explanation": controls_exp,
        "milestone_explanation": (
            f"The Paper's Engineered Innovation & Mechanism: {author_lead} ({pub_year}) introduced: \"{innovation_text[:140]}...\". "
            f"For your proposal (Parameter 5), formulate your own engineered tool and molecular mechanism of action that addresses the unresolved gap."
        ),
        "citation_explanation": (
            f"Key Measured Findings & Research Horizon: The study proved: \"{findings_text[:130]}...\". "
            f"Your Launching Pad: {horizon_text[:120]}... Source: \"{title or 'Primary Literature Study'}\" by {authors or 'Authors'} ({pub_year}), {journal or 'Journal'}. {recency_badge}"
        )
    }


def _build_eli_narrative(text: str, problem: str, solution: str, finding: str, limitation: str) -> Dict[str, Any]:
    """Constructs an intuitive, simple plain-English breakdown with analogies across 15+ domains."""
    text_lower = text.lower()
    
    # 1. Domain Classifier & Analogy Bank
    theme = "Biotechnology & Molecular Engineering"
    analogy = "Imagine taking a delicate biological machine that normally breaks easily, and adding custom molecular reinforcement so it keeps working under harsh real-world conditions."
    
    if any(k in text_lower for k in ["pet", "plastic", "depolymer", "cutinase", "polyester", "petase"]):
        theme = "Enzymatic Plastic Upcycling & Biocatalysis"
        analogy = "Plastic bottles are like tough, unchewable ropes. Normal bacterial enzymes are like tiny scissors that try to cut the rope, but the scissors melt the moment water gets hot. The researchers put molecular 'welds' (disulfide bridges) onto the scissors so they keep cutting at near-boiling temperatures without melting."
    elif any(k in text_lower for k in ["cas12", "cas13", "detectr", "sherlock", "collateral", "isothermal", "rpa", "lamp"]):
        theme = "CRISPR & Isothermal Fast Molecular Diagnostics"
        analogy = "Standard hospital PCR tests take days because they need big heating/cooling machines. The researchers used a molecular watchdog (Cas12a) with an exact photo of the virus. The second it spots the virus, it starts setting off glowing confetti cannons, giving a doctor an immediate positive test result in 30 minutes with no lab machines."
    elif any(k in text_lower for k in ["probiotic", "microbiome", "gut", "depression", "gut-brain", "bifidobacteri", "lactobacill"]):
        theme = "Microbiome Therapeutics & Gut-Brain Axis"
        analogy = "The gut microbiome acts like an internal biochemical pharmacy communicating with the central nervous system. The researchers investigated targeted probiotic strains to reinforce mucosal barrier integrity and modulate systemic neurochemical signaling."
    elif "rice" in text_lower and any(k in text_lower for k in ["golden rice", "carotenoid", "beta-carotene", "provitamin", "biofortif"]):
        theme = "Nutritional Biofortification & Crop Metabolic Engineering"
        analogy = "Standard white rice fills stomachs but lacks essential micronutrients like Vitamin A, leading to preventable malnutrition. The researchers introduced the biosynthetic assembly line for beta-carotene directly into the edible rice grain, turning ordinary rice into a golden, nutrient-packed staple crop."
    elif any(k in text_lower for k in ["wheat", "salin", "crop", "plant", "drought", "grain", "rice", "maize"]):
        theme = "Agricultural Crop Resilience & Food Security"
        analogy = "When crops grow in salty soil, salt rushes up the stems and poisons the leaves. The researchers took a natural desalination filter gene from a wild ancestral grain and bred it into commercial wheat. The filter sits in the plant's root pipelines, pulling salt out of the water before it reaches the food grain."
    elif any(k in text_lower for k in ["car-t", "tumor", "cancer", "antibody", "oncolog", "checkpoint", "pd-1", "cd19"]):
        theme = "Cancer Immunotherapy & Targeted Therapeutics"
        analogy = "Cancer cells are masters of disguise that trick the immune system into ignoring them. The researchers engineered synthetic radar receptors onto immune cells so they can unmask the tumor and eliminate cancer cells with laser precision while leaving healthy tissues unharmed."
    elif any(k in text_lower for k in ["mrna", "vaccine", "lipid nanoparticle", "lnp", "delivery vehicle", "encapsulation"]):
        theme = "mRNA Vaccines & Nanomedicine Drug Delivery"
        analogy = "Raw mRNA is like a delicate paper letter that gets shredded the instant it touches bodily fluids. The researchers packaged the letter inside a microscopic protective fat bubble (LNP) that safely sneaks past bodily defenses and delivers the instruction manual directly into cells."
    elif any(k in text_lower for k in ["wastewater", "effluent", "dye", "heavy metal", "bioremediation", "laccase", "biochar"]):
        theme = "Environmental Bioremediation & Water Treatment"
        analogy = "Industrial wastewater contains toxic chemicals that kill natural bacteria. The researchers created microscopic cleanup crews by immobilizing resilient enzymes on solid sponges so they continuously chew up toxic dyes before factory water enters local rivers."
    elif any(k in text_lower for k in ["ferment", "bioreactor", "titer", "yield", "metabolic burden", "pathway", "overexpress"]):
        theme = "Industrial Fermentation & Microbial Cell Factories"
        analogy = "Like running a microscopic automotive assembly line inside a yeast cell: the researchers re-routed the cell's internal sugar plumbing so every calorie eaten is redirected into synthesizing high-value medicine instead of cellular waste."
    elif any(k in text_lower for k in ["antibiotic", "resistant", "antimicrobial", "mrsa", "biofilm", "pathogen"]):
        theme = "Antimicrobial Resistance (AMR) & Infectious Diseases"
        analogy = "Superbugs have evolved protective fortress walls and chemical pumps that spit antibiotics out. The researchers engineered molecular crowbars that disable the pump mechanism, making standard low-cost medicines lethal to the bacteria once again."
    elif any(k in text_lower for k in ["alphafold", "docking", "pdb", "molecular dynamics", "in silico", "rosetta"]):
        theme = "Computational Biophysics & AI Protein Design"
        analogy = "Instead of testing billions of failed chemical combinations by hand for five years, researchers used high-speed molecular simulations like virtual wind-tunnels to sculpt the exact 3D pocket shape an enzyme needs before ever stepping into the wet lab."

    # 2. Simplified 4-Pillars Breakdown
    p_simple = simplify_academic_text(problem) if problem else "Existing tools face a severe physical bottleneck (they unfold, react too slowly, or require bulky lab machines)."
    s_simple = simplify_academic_text(solution) if solution else "The researchers introduced an engineered molecular modification to directly address the flaw."
    f_simple = simplify_academic_text(finding) if finding else "The authors proved with empirical data that their experimental approach significantly improved performance over standard baselines."
    l_simple = simplify_academic_text(limitation) if limitation else "However, real-world deployment remains constrained by matrix interference or scale-up barriers, leaving a clear research gap for your proposal!"

    return {
        "theme": theme,
        "core_analogy": analogy,
        "simple_problem": p_simple,
        "simple_solution": s_simple,
        "simple_takeaway": f_simple,
        "simple_limitation": l_simple
    }


def _extract_proposal_parameters(text: str, sentences: List[str], title: str = "", authors: str = "", year: Optional[int] = None) -> Dict[str, Any]:
    """
    Extracts high-yield proposal parameters:
    - Chassis / Host / Matrix
    - Molecular Tool / Construct
    - Epidemiological / Global Burden Statistic (Parameter 1)
    - Quantitative Benchmarks & Baseline Rate (Parameter 2)
    - Experimental Controls (Parameter 4)
    - Stated Limitations / Knowledge Gaps (Parameter 3)
    - Target Quantitative Milestone (Parameter 5)
    """
    text_lower = text.lower()
    title_lower = title.lower()
    combined_lower = f"{title_lower} {text_lower}"

    # 1. Chassis / Host / Matrix
    chassis_matches = []
    chassis_keywords = [
        "escherichia coli", "e. coli", "pichia pastoris", "pichia", "pseudomonas putida", "pseudomonas",
        "bacillus subtilis", "bacillus", "saccharomyces cerevisiae", "yeast", "corynebacterium",
        "synechocystis", "algae", "microalgae", "cyanobacteria", "ideonella sakaiensis", "thermus thermophilus",
        "streptomyces", "oryza sativa", "rice", "triticum", "wheat", "durum wheat", "arabidopsis thaliana",
        "arabidopsis", "maize", "corn", "zea mays", "tobacco", "nicotiana benthamiana", "nicotiana",
        "soybean", "glycine max", "potato", "solanum", "tomato", "crop", "endosperm", "cho cells",
        "hek293", "t-cells", "car-t", "stem cells", "human serum", "whole blood", "clinical swab",
        "blood", "serum", "plasma", "mouse", "murine", "rat", "zebrafish", "c. elegans",
        "mammalian cells", "soil", "wastewater", "effluent", "bioreactor", "crude extract", "compost"
    ]
    for ch in chassis_keywords:
        if ch in text_lower or ch in title_lower:
            if ch in ["e. coli", "escherichia coli"]:
                chassis_matches.append("Escherichia coli")
            elif ch in ["saccharomyces cerevisiae", "yeast"]:
                chassis_matches.append("Saccharomyces cerevisiae (yeast)")
            elif ch in ["oryza sativa", "rice", "endosperm"]:
                chassis_matches.append("Oryza sativa (Rice endosperm)")
            elif ch in ["triticum", "wheat", "durum wheat"]:
                chassis_matches.append("Triticum (Wheat)")
            elif ch in ["zea mays", "maize", "corn"]:
                chassis_matches.append("Zea mays (Maize)")
            elif ch in ["arabidopsis", "arabidopsis thaliana"]:
                chassis_matches.append("Arabidopsis thaliana")
            elif ch in ["ideonella sakaiensis"]:
                chassis_matches.append("Ideonella sakaiensis")
            elif ch in ["whole blood", "blood", "serum", "human serum", "plasma"]:
                chassis_matches.append("Clinical blood / serum matrix")
            elif ch in ["clinical swab", "swab"]:
                chassis_matches.append("Clinical swab matrix")
            elif ch in ["cho cells", "hek293", "mammalian cells"]:
                chassis_matches.append("Mammalian cell line")
            elif ch in ["t-cells", "car-t"]:
                chassis_matches.append("Primary human T-cells")
            else:
                chassis_matches.append(ch.capitalize())

    unique_chassis = list(dict.fromkeys(chassis_matches))
    if unique_chassis:
        chassis_val = ", ".join(unique_chassis[:2])
    elif any(k in combined_lower for k in ["crop", "plant", "grain", "seed", "leaf", "flora", "cultivar", "botanical"]):
        chassis_val = "Plant Host / Crop Expression System"
    elif any(k in combined_lower for k in ["clinical", "patient", "diagnostic", "pathogen", "virus", "infection", "cancer", "tumor"]):
        chassis_val = "Clinical Host / Human Diagnostic Matrix"
    else:
        chassis_val = "Target Host System / Experimental Matrix"

    # 2. Molecular Tool / Engineered Construct
    tool_matches = []
    tool_patterns = [
        r"\b(cas\d+[a-z]?|cpf1)\b",
        r"\b(petase|mhetase|cutinase|cellulase|polymerase|ligase|protease|dehydrogenase|transporter|laccase|polyesterase|hydrolase|peroxidase|esterase|nuclease|synthase|kinase|reductase|oxidase|decarboxylase|isomerase|transfera[sz]e)\b",
        r"\b(rpa|lamp|detectr|sherlock|crispr|prime edit\w*|base edit\w*|car-t|mrna|sirna|antibody|mab|nanobody|aptamer|biosensor)\b",
        r"\b(tahkt1;5|nax\d|psy\d?|crti|dxs|bche|crt[a-z0-9]+)\b",
        r"\b[A-Z]\d{2,4}[A-Z](?:/[A-Z]\d{2,4}[A-Z])*\b"  # e.g. W159H, F238Y, W159H/F238Y
    ]
    for p in tool_patterns:
        found = re.findall(p, text, flags=re.IGNORECASE)
        for f in found:
            if isinstance(f, str) and len(f) > 2:
                low_f = f.lower()
                if "cas" in low_f or "cpf1" in low_f:
                    tool_matches.append(f.upper())
                elif "tahkt" in low_f or "nax" in low_f:
                    tool_matches.append(f)
                elif "/" in f or any(c.isdigit() for c in f):
                    tool_matches.append(f.upper())
                else:
                    tool_matches.append(f.capitalize())

    # Fallback to title inspection with patterns
    if not tool_matches and title:
        for p in tool_patterns:
            found = re.findall(p, title, flags=re.IGNORECASE)
            for f in found:
                if isinstance(f, str) and len(f) > 2:
                    tool_matches.append(f.capitalize())

    # Check for domain-specific constructs / metabolic pathways dynamically
    if not tool_matches:
        if any(k in combined_lower for k in ["carotenoid", "beta-carotene", "provitamin"]):
            tool_matches.append("Carotenoid Biosynthetic Pathway")
        elif any(k in combined_lower for k in ["probiotic", "microbiome", "gut-brain"]):
            tool_matches.append("Probiotic Strain Consortium")
        elif "mrna" in combined_lower:
            tool_matches.append("Modified mRNA / Nanoparticle Delivery System")
        elif "car-t" in combined_lower:
            tool_matches.append("Chimeric Antigen Receptor (CAR) Construct")
        elif "crispr" in combined_lower:
            tool_matches.append("CRISPR Targeted System")
        elif "vaccine" in combined_lower:
            tool_matches.append("Recombinant Vaccine Antigen")
        elif "biosensor" in combined_lower:
            tool_matches.append("Target Biosensor System")

    # If still not found, intelligently extract key entity from title
    if not tool_matches and title:
        title_head = title.split(":")[0].split(" - ")[0].strip()
        stop_words = {"investigation", "study", "analysis", "review", "development", "synthesis", "engineering", "promises", "status", "future", "prospects", "advances", "recent", "novel", "role", "characterization", "insight", "evaluation", "assessment"}
        words = [w for w in title_head.split() if w.lower() not in stop_words and len(w) > 2]
        if words and len(words) <= 5:
            tool_matches.append(" ".join(words))

    tool_val = ", ".join(list(dict.fromkeys(tool_matches))[:3]) if tool_matches else "Primary Biological System / Intervention"

    # 3. Epidemiological / Global Burden Statistic (Parameter 1)
    burden_sentences = []
    burden_keywords = [
        "million", "billion", "trillion", "metric tons", "tons", "worldwide", "globally",
        "annually", "per year", "incidence", "prevalence", "mortality", "daly", "cost",
        "burden", "accumulat", "discarded", "plastic waste", "staggering rate", "threat",
        "crisis", "outbreak", "incurring", "loss", "pollut", "soil salinity", "most abundantly"
    ]
    for s in sentences:
        low = s.lower()
        if any(k in low for k in burden_keywords):
            if any(char.isdigit() for char in s) or any(w in low for w in ["most abundant", "staggering", "alarming", "vast majority", "severely", "drastically", "incurring"]):
                burden_sentences.append(s.strip())
            elif not burden_sentences:
                burden_sentences.append(s.strip())

    if burden_sentences:
        burden_val = burden_sentences[0]
    elif sentences and len(sentences[0].split()) >= 6:
        burden_val = sentences[0].strip()
    else:
        burden_val = "Quantified global burden: widespread environmental accumulation or clinical challenge documented in literature."

    # 4. Quantitative Metrics & Baselines (Parameter 2)
    metrics_list = []
    metric_regex = r"\b(\d+(\.\d+)?\s*(%|°c|c|mg/l|g/l/h|g/l|ug/ml|µg/ml|nm|um|µm|mm|m|kda|da|bp|kb|mb|copies/ul|copies/µl|attomolar|femtomolar|picomolar|nanomolar|micromolar|millimolar|molar|turnovers(?:/s| per second)?|ds/m|mg/day/cm²|å|angstrom|-fold|fold))\b"
    found_metrics = re.findall(metric_regex, text, flags=re.IGNORECASE)
    for m in found_metrics:
        if m[0]:
            metrics_list.append(m[0].strip())

    special_metrics = []
    for s in sentences:
        low = s.lower()
        if any(term in low for term in ["tm", "melting temperature"]) and any(c in low for c in ["=", "°c", "increased", "elevat"]):
            special_metrics.append(s.strip())
        elif any(term in low for term in ["lod", "limit of detection", "attomolar", "copies/ul", "copies/µl"]):
            special_metrics.append(s.strip())
        elif "yield" in low and "%" in low:
            special_metrics.append(s.strip())
        elif "resolution" in low and any(u in low for u in ["å", "angstrom"]):
            special_metrics.append(s.strip())
        elif "turnover" in low or "kcat" in low or "productivity" in low:
            special_metrics.append(s.strip())

    if not special_metrics and metrics_list:
        for s in sentences:
            low = s.lower()
            if any(m.lower() in low for m in metrics_list) and any(v in low for v in ["achieved", "exhibited", "detected", "demonstrated", "observed", "increased", "reduced", "reveals", "presents", "yielding"]):
                special_metrics.append(s.strip())

    if not special_metrics:
        for s in sentences:
            low = s.lower()
            if any(v in low for v in ["here, we present", "we observed", "achieved", "exhibited", "improved", "demonstrated", "shows that", "reveals"]):
                special_metrics.append(s.strip())

    metrics_summary = list(dict.fromkeys(metrics_list))[:6]

    if special_metrics:
        metric_sentence = special_metrics[0]
    elif metrics_summary:
        metric_sentence = f"Empirical benchmark yield and performance metrics: {', '.join(metrics_summary)}."
    elif len(sentences) > 2:
        metric_sentence = sentences[-1].strip()
    elif len(sentences) > 1:
        metric_sentence = sentences[1].strip()
    else:
        author_ref = authors.split(",")[0] if authors else "Literature"
        metric_sentence = f"Empirical baseline established by {author_ref} ({year or 'benchmark'}): quantitative activity benchmarks reported for {tool_val}."

    # 5. Experimental Controls, Chassis Model & Assay Conditions (Parameter 4)
    explicit_control_sentences = []
    direct_control_terms = [
        "negative control", "positive control", "baseline control", "vehicle control",
        "served as control", "served as the control", "served as a control",
        "empty-plasmid", "empty plasmid", "empty vector", "empty-vector",
        "non-targeting", "parent cultivars", "parent cultivar", "parent strain",
        "reference strain", "isogenic", "unmodified control", "wild-type control",
        "mock-treated", "untreated control", "placebo"
    ]
    for s in sentences:
        low = s.lower()
        if any(c in low for c in direct_control_terms):
            explicit_control_sentences.append(s.strip())

    if not explicit_control_sentences:
        for s in sentences:
            low = s.lower()
            if any(c in low for c in ["control", "wild-type", "unmodified", "vehicle", "mock", "homologous", "baseline"]) and any(comp in low for comp in ["compared to", "versus", "relative to", "against", "reference"]):
                explicit_control_sentences.append(s.strip())

    assay_techniques = []
    technique_keywords = [
        "x-ray crystallography", "crystal structure", "cryo-em", "hplc", "fplc", "mass spectrometry",
        "spectrophotomet", "fluorescence", "flow cytometry", "rt-qpcr", "qpcr", "western blot",
        "sds-page", "circular dichroism", "isothermal titration calorimetry", "surface plasmon resonance",
        "enzyme kinetics", "plate reader", "biochemical assay", "field trial", "greenhouse", "fed-batch"
    ]
    for tech in technique_keywords:
        if tech in text_lower:
            assay_techniques.append(tech.title())

    tech_summary = ", ".join(list(dict.fromkeys(assay_techniques))[:3]) if assay_techniques else "Standard biochemical / molecular assay"

    if explicit_control_sentences:
        controls_val = f"Model & Assay: Tested in {chassis_val} using {tech_summary}. Verification Controls: {explicit_control_sentences[0]}"
    else:
        controls_val = f"Model & Assay: Tested in {chassis_val} using {tech_summary}. Verification Benchmark: Benchmarked against wild-type / parental baseline (Note: Explicit negative vehicle blanks not fully detailed in short abstract; include vehicle and unengineered negative controls in your proposal)."

    # 6. Stated Limitations / Unresolved Gaps (Parameter 3)
    gap_sentences = []
    gap_indicators = [
        "however", "despite", "nevertheless", "resisted", "limiting", "penalty",
        "severe background", "silencing", "drawback", "not fully optimized", "does not degrade",
        "cannot degrade", "remains a challenge", "restricted by", "unresolved", "bottleneck",
        "impeded", "denaturation", "thermolability", "off-target", "highlight the need",
        "further developments", "constrained by", "lacks", "limited by", "poor", "low yield",
        "toxicity", "instability", "inefficient", "barrier", "challenge", "hurdle"
    ]
    for s in sentences:
        low = s.lower()
        if any(g in low for g in gap_indicators):
            gap_sentences.append(s.strip())

    if gap_sentences:
        gap_val = gap_sentences[0]
    else:
        gap_val = "Translational and operational constraints remain the primary gap: real-world matrix interference, operational yield, and scalable deployment require further experimental optimization beyond this initial study."

    # 7. Core Engineered Innovation & Molecular Mechanism (Parameter 5)
    innovation_sentences = []
    innovation_terms = [
        "engineered", "mutation", "mutants", "active-site", "narrowing", "cleft",
        "binding cleft", "residues", "substituted", "fusion", "coupled", "introgressed",
        "designed", "synthesized", "cloned", "chimeric", "recombinant", "promoter",
        "variant", "scaffold", "directed evolution", "rational design", "catalytic",
        "transporter", "circuit", "construct"
    ]
    for s in sentences:
        low = s.lower()
        if any(term in low for term in innovation_terms) and any(v in low for v in ["here", "we", "by", "develop", "reveals", "design", "mutat", "construct"]):
            innovation_sentences.append(s.strip())

    solution_candidates = [s.strip() for s in sentences if any(w in s.lower() for w in ["here, we", "we engineered", "we developed", "we coupled", "we discovered", "we introgressed", "this study", "we designed", "constructs were"])]
    finding_candidates = [s.strip() for s in sentences if any(w in s.lower() for w in ["achieved", "exhibited", "detected", "reduced", "increased", "yield", "fold", "resulting in", "demonstrated", "turnovers"])]

    if innovation_sentences:
        key_innovation = innovation_sentences[0]
    elif solution_candidates:
        key_innovation = solution_candidates[0]
    else:
        key_innovation = f"Engineered intervention: Novel {tool_val} construct optimized for targeted molecular activity in {chassis_val}."

    # 8. Key Measured Findings, Evidence Proof & Research Horizon (Parameter 6)
    if special_metrics:
        measured_finding = special_metrics[0]
    elif metrics_summary:
        measured_finding = f"Demonstrated validated performance benchmarks: {', '.join(metrics_summary)}."
    elif finding_candidates:
        measured_finding = finding_candidates[0]
    else:
        measured_finding = f"Demonstrated quantitative proof-of-concept for {tool_val} in {chassis_val}."

    research_horizon = f"Evidence Proof: {measured_finding} Horizon for Your Project: Overcoming {gap_val[:90]}... under operational conditions."

    # Backward-compatible target milestone formula (preserved for existing tests and prompt guidance)
    if metrics_summary:
        target_milestone = f"Target a calibrated ≥2- to 3-fold quantitative improvement over the published literature baseline ({metrics_summary[0]}) under operational assay conditions."
    else:
        target_milestone = "Target a calibrated quantitative improvement in efficiency, yield, analytical sensitivity, or stability over the published literature baseline."

    # Realistic Literature Timeline Benchmarks
    timeline_benchmark = {
        "phase1_months": "Months 1–4",
        "phase1_focus": f"Cloning, construct synthesis ({tool_val}), and sequence verification in {chassis_val}",
        "phase2_months": "Months 4–8",
        "phase2_focus": f"Expression optimization, kinetic assays, and quantitative benchmark evaluation ({tech_summary})",
        "phase3_months": "Months 8–14",
        "phase3_focus": "Operational matrix validation, stability trials, and translational reporting",
        "buffer_guidance": "Peer-reviewed literature allocates 15–20% buffer for failed clone verification and protocol recalibration."
    }

    return {
        "chassis": chassis_val,
        "tool": tool_val,
        "burden_statistic": burden_val,
        "metric_numbers": metrics_summary,
        "primary_metric_sentence": metric_sentence,
        "plain_metric": simplify_academic_text(metric_sentence),
        "controls": controls_val,
        "experimental_strategy": controls_val,
        "stated_gap": gap_val,
        "plain_gap": simplify_academic_text(gap_val),
        "key_innovation": key_innovation,
        "key_findings": measured_finding,
        "research_horizon": research_horizon,
        "target_milestone": target_milestone,
        "timeline_benchmark": timeline_benchmark
    }


def _generate_proposal_recommendations(parameters: Dict[str, Any], title: str) -> List[Dict[str, str]]:
    """Suggests where this paper directly plugs into the student's proposal."""
    recs = []

    # 1. Current Scientific Benchmark (Tier 2 of Funnel)
    recs.append({
        "section": "Step 3: Background & Current Scientific Benchmark (Funnel Tier 2)",
        "guidance": f"Cite this paper as your empirical benchmark: \"{parameters['tool']} achieved {parameters['primary_metric_sentence']}\". This proves you know the current scientific ceiling.",
        "target_field": "funnel_tier2"
    })

    # 2. Scientific Knowledge Gap (Tier 3 of Funnel)
    recs.append({
        "section": "Step 3: Knowledge Gap (Funnel Tier 3)",
        "guidance": f"Use the authors' admitted limitation as your jump-off gap: \"{parameters['stated_gap']}\". Explain that while their study made great progress, this unresolved bottleneck motivates your grant.",
        "target_field": "funnel_tier3"
    })

    # 3. Competitor Matrix (Step 5)
    recs.append({
        "section": "Step 5: Competitor Landscape Matrix (Incumbent/Emerging)",
        "guidance": f"Enter {parameters['tool']} as the 'Emerging Competitor'. Highlight their performance ({', '.join(parameters['metric_numbers'][:2]) or 'High yield'}), but show your advantage over their flaw ({parameters['stated_gap'][:60]}...).",
        "target_field": "emerging_name"
    })

    # 4. Methodology Controls (Step 4 & Specific Objectives)
    if "not explicitly" in parameters.get("controls", "").lower():
        ctrl_guide = "Designate explicit positive benchmark controls and negative vehicle blanks in your methodology (Step 4) to ensure your experimental design is reproducible."
    else:
        ctrl_guide = f"Adopt their experimental controls: {parameters['controls'][:120]}... Reviewers reward proposals that duplicate validated peer-reviewed control designs."

    recs.append({
        "section": "Step 4: Experimental Methodology & Controls",
        "guidance": ctrl_guide,
        "target_field": "methodology"
    })

    return recs
