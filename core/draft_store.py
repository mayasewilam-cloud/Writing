"""
BioWriter Studio - Server-side Student Draft Storage and Roster Management.
Persists student proposal drafts as structured JSON in portal/data/drafts/.
"""

import os
import re
import json
import datetime
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.environ.get("VERCEL"):
    DATA_DIR = os.path.join("/tmp", "data")
    DRAFTS_DIR = os.path.join(DATA_DIR, "drafts")
else:
    DATA_DIR = os.path.join(BASE_DIR, "data")
    DRAFTS_DIR = os.path.join(DATA_DIR, "drafts")


def _ensure_drafts_dir():
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    if os.environ.get("VERCEL") and os.path.exists(os.path.join(BASE_DIR, "data", "drafts")):
        bundled = os.path.join(BASE_DIR, "data", "drafts")
        for f in os.listdir(bundled):
            src = os.path.join(bundled, f)
            dst = os.path.join(DRAFTS_DIR, f)
            if not os.path.exists(dst) and os.path.isfile(src):
                try:
                    with open(src, "r", encoding="utf-8") as rf, open(dst, "w", encoding="utf-8") as wf:
                        wf.write(rf.read())
                except Exception:
                    pass


def sanitize_student_id(student_id: str) -> str:
    if not student_id:
        return "student_draft"
    clean = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", student_id.strip()).strip("_")
    return clean[:40] if clean else "student_draft"


def calculate_draft_summary(data: Dict[str, Any]) -> Dict[str, Any]:
    nodes = 0
    if data.get("chassis") and data.get("tool"):
        nodes += 1
    if data.get("query"):
        nodes += 1
    if data.get("matrix") and (data.get("matrix", {}).get("blue") or data.get("matrix", {}).get("green")):
        nodes += 1
    if data.get("funnel") and data.get("funnel", {}).get("tier1"):
        nodes += 1
    if data.get("aims") and data.get("aims", {}).get("aim1"):
        nodes += 1
    if data.get("methodology") and len(data.get("methodology", "").strip()) > 30:
        nodes += 1
    if data.get("impact_data") and (data.get("impact_data", {}).get("academic") or data.get("impact_data", {}).get("economic")):
        nodes += 1
    if data.get("competitor_data") and data.get("competitor_data", {}).get("usp"):
        nodes += 1
    if data.get("swot") and data.get("swot", {}).get("s") and data.get("swot", {}).get("w"):
        nodes += 1
    if data.get("references") and len(data.get("references", "").strip()) > 20:
        nodes += 1

    # Approximate total words
    all_text = " ".join([
        str(data.get("title", "")),
        str(data.get("abstract", "")),
        str(data.get("methodology", "")),
        str(data.get("funnel", {}).get("tier1", "")),
        str(data.get("funnel", {}).get("tier2", "")),
        str(data.get("funnel", {}).get("tier3", "")),
        str(data.get("funnel", {}).get("tier4", "")),
        str(data.get("aims", {}).get("aim1", "")),
        str(data.get("aims", {}).get("aim2", "")),
        str(data.get("aims", {}).get("aim3", ""))
    ])
    words = len(all_text.split())

    return {
        "completed_nodes": nodes,
        "completion_percentage": int((nodes / 10.0) * 100),
        "word_count": words
    }


def save_student_draft(student_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    _ensure_drafts_dir()
    clean_id = sanitize_student_id(student_id or data.get("student_id", ""))
    now_iso = datetime.datetime.now().isoformat()
    now_readable = datetime.datetime.now().strftime("%b %d, %Y - %H:%M")

    data["student_id"] = clean_id
    data["student_name"] = data.get("student_name", "BT_301 Student")
    data["updated_at"] = now_iso
    data["updated_at_readable"] = now_readable

    summary = calculate_draft_summary(data)
    data["summary"] = summary

    filepath = os.path.join(DRAFTS_DIR, f"{clean_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return {
        "success": True,
        "student_id": clean_id,
        "student_name": data["student_name"],
        "title": data.get("title", "Untitled Proposal"),
        "updated_at": now_readable,
        "summary": summary
    }


def get_student_draft(student_id: str) -> Optional[Dict[str, Any]]:
    _ensure_drafts_dir()
    clean_id = sanitize_student_id(student_id)
    filepath = os.path.join(DRAFTS_DIR, f"{clean_id}.json")
    if not os.path.exists(filepath):
        # Case insensitive / partial lookup fallback
        for fname in os.listdir(DRAFTS_DIR):
            if fname.lower().endswith(".json"):
                stem = fname[:-5]
                if stem.lower() == clean_id.lower() or stem.lower() == student_id.lower():
                    filepath = os.path.join(DRAFTS_DIR, fname)
                    break
        else:
            return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            data["summary"] = calculate_draft_summary(data)
            return data
    except Exception:
        return None


def toggle_draft_lock(student_id: str, is_locked: bool) -> Dict[str, Any]:
    """Toggles or sets the proposal lock for official grading."""
    _ensure_drafts_dir()
    clean_id = sanitize_student_id(student_id)
    draft = get_student_draft(clean_id)
    if not draft:
        return {"success": False, "error": f"Student draft '{clean_id}' not found."}

    draft["is_locked_for_grading"] = bool(is_locked)
    draft["locked_at"] = datetime.datetime.now().strftime("%b %d, %Y - %H:%M") if is_locked else None

    filepath = os.path.join(DRAFTS_DIR, f"{clean_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(draft, f, indent=2, ensure_ascii=False)

    return {
        "success": True,
        "student_id": clean_id,
        "is_locked_for_grading": bool(is_locked),
        "message": "Proposal successfully locked for faculty grading." if is_locked else "Proposal unlocked for revisions."
    }


def dispatch_faculty_feedback(student_id: str, feedback: Dict[str, Any]) -> Dict[str, Any]:
    """Stores official instructor evaluation, point overrides, and action items onto the student's cloud record."""
    _ensure_drafts_dir()
    clean_id = sanitize_student_id(student_id)
    draft = get_student_draft(clean_id)
    if not draft:
        return {"success": False, "error": f"Student draft '{clean_id}' not found."}

    now_readable = datetime.datetime.now().strftime("%b %d, %Y - %H:%M")
    feedback["dispatched_at"] = now_readable

    draft["faculty_review"] = feedback
    # Also save to disk
    filepath = os.path.join(DRAFTS_DIR, f"{clean_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(draft, f, indent=2, ensure_ascii=False)

    return {
        "success": True,
        "student_id": clean_id,
        "dispatched_at": now_readable,
        "faculty_review": feedback,
        "message": f"Official evaluation successfully dispatched to student draft {clean_id}."
    }


def delete_student_draft(student_id: str) -> Dict[str, Any]:
    """Permanently deletes a student's proposal draft file from the server database."""
    _ensure_drafts_dir()
    clean_id = sanitize_student_id(student_id)
    if not clean_id or clean_id == "student_draft":
        return {"success": False, "error": "Invalid student ID."}

    filepath = os.path.join(DRAFTS_DIR, f"{clean_id}.json")
    if not os.path.exists(filepath):
        # Case-insensitive fallback
        for fname in os.listdir(DRAFTS_DIR):
            if fname.lower().endswith(".json") and fname[:-5].lower() == clean_id.lower():
                filepath = os.path.join(DRAFTS_DIR, fname)
                break
        else:
            return {"success": False, "error": f"Submission for student '{clean_id}' not found."}

    try:
        os.remove(filepath)
        return {
            "success": True,
            "student_id": clean_id,
            "message": f"Proposal submission for {clean_id} permanently removed."
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to delete submission: {str(e)}"}


def list_student_drafts() -> List[Dict[str, Any]]:
    _ensure_drafts_dir()
    seed_default_drafts()

    roster = []
    for fname in os.listdir(DRAFTS_DIR):
        if fname.endswith(".json"):
            filepath = os.path.join(DRAFTS_DIR, fname)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    summary = calculate_draft_summary(d)
                    fac_rev = d.get("faculty_review")
                    action_items = fac_rev.get("action_items", []) if (fac_rev and isinstance(fac_rev, dict)) else []
                    completed_feedback = d.get("completed_feedback_items", [])
                    roster.append({
                        "student_id": d.get("student_id", fname[:-5]),
                        "student_name": d.get("student_name", "Anonymous Student"),
                        "title": d.get("title", "Untitled Proposal"),
                        "modality": d.get("modality", "Cellular Expression"),
                        "updated_at": d.get("updated_at_readable", d.get("updated_at", "Recently")),
                        "completed_nodes": summary["completed_nodes"],
                        "completion_percentage": summary["completion_percentage"],
                        "word_count": summary["word_count"],
                        "is_locked_for_grading": bool(d.get("is_locked_for_grading", False)),
                        "faculty_reviewed": bool(fac_rev),
                        "faculty_review": fac_rev,
                        "total_action_items": len(action_items),
                        "completed_feedback_items": completed_feedback,
                        "completed_action_count": len(completed_feedback)
                    })
            except Exception:
                continue

    roster.sort(key=lambda x: x.get("student_id", ""))
    return roster


def seed_default_drafts():
    """Seeds 3 rich sample student drafts if not already present."""
    _ensure_drafts_dir()
    samples = [
        {
            "student_id": "ST-2026-01",
            "student_name": "Sara Al-Mansoor & Team BioDetect",
            "modality": "Cell-Free Diagnostics",
            "chassis": "Cell-free Tx-Tl lysate",
            "tool": "CRISPR-Cas12a (LbCas12a) with FAM-quencher reporter",
            "target": "mcr-1 colistin resistance plasmid gene in wastewater",
            "query": '("CRISPR-Cas12a" OR "DETECTR") AND ("mcr-1" OR "colistin resistance") AND "wastewater" AND "isothermal"',
            "title": "CRISPR-Cas12a-Assisted Isothermal Detection of Polymyxin Resistance (mcr-1) in Agricultural Wastewater",
            "abstract": "The environmental dissemination of polymyxin resistance mediated by the plasmid-borne mcr-1 gene poses an escalating threat to global public health. Conventional surveillance relies on bacterial culture followed by quantitative PCR, which requires centralized laboratory infrastructure and 24 to 48 hours of turnaround time. Here, we present an all-in-one cell-free diagnostic assay combining Recombinase Polymerase Amplification (RPA) with CRISPR-Cas12a trans-cleavage for rapid, visual detection of mcr-1 directly from agricultural runoff within 45 minutes at 37°C. The engineered system utilizes a chemically modified crRNA targeting a conserved catalytic motif of mcr-1, unleashing indiscriminate collateral cleavage of single-stranded DNA fluorophore-quencher probes upon target engagement. In preliminary benchmarking against spiked environmental matrices, the platform achieved a limit of detection of 5 copies/uL without cross-reactivity against wild-type E. coli or related beta-lactamase genes. This point-of-need diagnostic provides a decentralized biosurveillance tool to track antimicrobial resistance dissemination at agricultural discharge interfaces.",
            "funnel": {
                "tier1": "Antimicrobial resistance (AMR) is projected to cause 10 million annual fatalities by 2050. Colistin remains one of the few last-resort reserve antibiotics for treating multidrug-resistant Gram-negative bacterial infections.",
                "tier2": "The mobilization of the phosphoethanolamine transferase gene (mcr-1) onto conjugative plasmids has facilitated rapid horizontal transmission across livestock reservoirs and agricultural irrigation waterways.",
                "tier3": "Current environmental monitoring relies on culture-dependent enrichment and benchtop qPCR. These methods fail point-of-need requirements due to thermal cycler dependency, high reagent costs, and 48-hour diagnostic turnaround times.",
                "tier4": "We hypothesize that coupling isothermal recombinase polymerase amplification (RPA) at 37°C with catalytic CRISPR-Cas12a trans-cleavage will achieve single-copy limit of detection of mcr-1 in wastewater within 45 minutes."
            },
            "matrix": {
                "blue": "LOD: 100 CFU/mL; Assay Time: 45 min at 37°C; Turnaround: <1 hour",
                "yellow": "Isothermal RPA coupled with CRISPR-Cas12a trans-cleavage of ssDNA-FAM reporters",
                "green": "Environmental wastewater matrix contains humic acid inhibitors that suppress fluorescent reporter kinetics",
                "purple": "Positive: Synthesized mcr-1 DNA template; Negative: Nuclease-free water and non-target plasmid (pUC19)",
                "citation": "Chen et al. (2018) Science; Gootenberg et al. (2017) Science"
            },
            "aims": {
                "aim1": "Design and screen 5 chemically modified crRNA candidates targeting conserved regions of the mcr-1 catalytic domain for optimal Cas12a trans-cleavage kinetics.",
                "aim2": "Formulate a one-pot RPA-Cas12a reaction buffer containing trehalose and BSA to overcome humic acid polymerase inhibition in agricultural runoff.",
                "aim3": "Validate diagnostic sensitivity and specificity against 50 blind environmental effluent samples benchmarked against standard TaqMan qPCR."
            },
            "methodology": "crRNA sequences targeting mcr-1 will be synthesized with 2'-O-methyl modifications. Recombinase Polymerase Amplification will be conducted at 37°C for 20 minutes using TwistAmp Basic reagents. Subsequently, 2 uL of RPA amplicon will be transferred to a 50 nM LbCas12a reaction containing 100 nM FAM-TAMRA single-stranded DNA reporter. Fluorescent kinetic measurements will be recorded every 60 seconds on a portable microplate fluorometer. Positive control reactions will contain 1,000 copies/uL of sequence-verified mcr-1 plasmid DNA; negative vehicle controls will substitute template with nuclease-free water; specificity controls will test gDNA from multidrug-resistant clinical isolates carrying blaCTX-M and blaNDM-1.",
            "impact_data": {
                "academic": "Publishes an open-access protocol for one-pot environmental CRISPR diagnostics and kinetic characterization of chemically modified crRNAs in complex matrix buffers.",
                "economic": "Reduces diagnostic unit costs from $35.00/sample (qPCR) down to $2.80/sample, enabling high-frequency decentralized farm monitoring without capital infrastructure.",
                "societal": "Provides early-warning environmental surveillance to intercept antimicrobial resistance spillover into community drinking water aquifers."
            },
            "competitor_data": {
                "incumbent": "Benchtop qPCR (Applied Biosystems 7500): 2.5 hours, $35/test, requires trained operator and cold-chain storage.",
                "emerging": "Standard loop-mediated isothermal amplification (LAMP): 65°C heating block required, prone to false-positive primer-dimer turbidity.",
                "proposed": "One-pot RPA-Cas12a at ambient 37°C: 45 min, $2.80/test, visual fluorescent or lateral flow readout.",
                "usp": "The only field-deployable assay operating strictly at 37°C without thermal cycling that discriminates single-nucleotide mcr-1 variants from benign commensal flora."
            },
            "swot": {
                "s": "High specificity of Cas12a PAM recognition; sub-picomolar sensitivity via dual catalytic amplification.",
                "w": "Cas12a collateral activity can lead to premature probe exhaustion; commercial RPA enzyme pellets have batch-to-batch variability.",
                "o": "Expanding regulatory mandates for agricultural discharge monitoring; scalable to lateral flow dipstick format.",
                "t": "Rapid evolution of mcr alleles (mcr-2 through mcr-10) potentially escaping the single crRNA targeting window."
            },
            "aims_contingencies": {
                "aim1_fallback": "Synthesize alternative 2'-fluoro modified crRNA candidates if chemical degradation occurs in environmental matrices.",
                "aim2_fallback": "Supplement reaction buffer with betaine or secondary surfactant if trehalose alone fails to suppress humic acid inhibition.",
                "aim3_fallback": "Incorporate magnetic bead pre-concentration step if wastewater target viral load falls below 5 copies/uL."
            },
            "control_triad": {
                "negative_control": "Nuclease-free water and non-target pUC19 plasmid vector (vehicle background).",
                "positive_control": "Sequence-verified synthesized mcr-1 DNA template at 1,000 copies/uL (analytical benchmark).",
                "specificity_control": "Genomic DNA from clinical isolates harboring non-target resistance genes (blaCTX-M-15 and blaNDM-1)."
            },
            "biotech_risk_matrix": {
                "off_target": "Spurious trans-cleavage triggered by non-target environmental homologs. Mitigation: Stringent TTTV PAM scanning and 20-nt crRNA matching.",
                "toxicity": "Minimal cellular toxicity (cell-free assay), but fluorophore quenching in dark effluent. Mitigation: Dual-wavelength ratiometric fluorometry.",
                "solubility": "RPA enzyme pellet denaturation under field ambient heat. Mitigation: Trehalose-based dry lyosphere stabilization.",
                "biosafety": "Handling pathogenic wastewater samples (BSL-2). Mitigation: Rapid chemical lysis / heat inactivation (95°C, 3 min) at collection point."
            },
            "budget": [
                {"category": "Consumables & Reagents", "description": "TwistAmp RPA kits, Cas12a enzyme, modified crRNA oligos, fluorescent ssDNA reporters", "amount": 6500},
                {"category": "Equipment & Tooling", "description": "Portable 37°C heating block and battery-operated handheld fluorometer", "amount": 3200},
                {"category": "Testing & Analytical Services", "description": "Sanger sequencing verification and environmental wastewater core testing", "amount": 1800},
                {"category": "Dissemination & Publication", "description": "Open-access journal publication charges (e.g. Environmental Science & Technology)", "amount": 2500}
            ],
            "references": "Chen, J. S., et al. (2018). CRISPR-Cas12a target binding unleashes indiscriminate single-stranded DNase activity. Science, 360(6387), 436-439.\nGootenberg, J. S., et al. (2017). Nucleic acid detection with CRISPR-Cas13a/C2c2. Science, 356(6336), 438-442.\nLiu, Y. Y., et al. (2016). Emergence of plasmid-mediated colistin resistance mechanism MCR-1 in animals and human beings in China: a microbiological and molecular biological study. The Lancet Infectious Diseases, 16(2), 161-168.\nWang, M., et al. (2022). Portable microfluidic CRISPR diagnostics for environmental pathogen surveillance. Nature Biotechnology, 40(8), 1205-1215."
        },
        {
            "student_id": "ST-2026-02",
            "student_name": "Omar Tariq & Team EnzymX",
            "modality": "Cellular Expression",
            "chassis": "Escherichia coli BL21(DE3)",
            "tool": "Engineered FAST-PETase with S214H/I168R/W159H mutations",
            "target": "Post-consumer polyethylene terephthalate (PET) plastic bottles",
            "query": '("PETase" OR "FAST-PETase") AND ("protein engineering" OR "rational design") AND ("polyethylene terephthalate" OR "PET recycling")',
            "title": "Engineered Fast-PETase Depolymerase with Hydrophobic Cavity Mutations for Enhanced Low-Temperature Biodegradation",
            "abstract": "Accumulation of polyethylene terephthalate (PET) microplastics constitutes a pervasive ecological hazard due to the extreme recalcitrance of aromatic ester bonds. Bacterial PETase enzymes isolated from Ideonella sakaiensis exhibit native activity at mesophilic temperatures but suffer from low kinetic turnover (kcat < 10 s-1) and rapid thermal inactivation at temperatures above 37°C. In this study, we rationally engineered the substrate-binding groove of FAST-PETase through targeted mutagenesis of hydrophobic residues flanking the catalytic triad (S214H and I168R) to stabilize the pre-hydrolysis Michaelis complex. Recombinant variants expressed in Escherichia coli BL21(DE3) demonstrated an 8.4-fold increase in depolymerization rate against commercial amorphous PET films at 30°C compared to wild-type enzyme, achieving 74% conversion into monomeric terephthalic acid (TPA) within 48 hours without requiring energy-intensive thermal pre-treatment.",
            "funnel": {
                "tier1": "Over 350 million metric tons of plastic waste are generated annually worldwide, with polyethylene terephthalate (PET) comprising the majority of single-use beverage containers.",
                "tier2": "Enzymatic biorecycling using microbial depolymerases provides a circular closed-loop alternative to mechanical downcycling and chemical pyrolysis.",
                "tier3": "Native Ideonella sakaiensis PETase suffers from low kinetic turnover (kcat = 8.2 s-1) and rapid active-site collapse at temperatures below the glass transition point of PET.",
                "tier4": "We hypothesize that introducing targeted hydrophobic-to-cationic substitutions (I168R and S214H) will lower the activation energy barrier for ester bond cleavage on untreated amorphous PET films at 30°C."
            },
            "matrix": {
                "blue": "Conversion: 74% degradation in 48 h; kcat: 42.5 s-1 at 30°C; Tm: 52.4°C",
                "yellow": "Rational active-site engineering via site-directed mutagenesis and Ni-NTA purification",
                "green": "High-crystallinity commercial PET remains recalcitrant without prior chemical swelling",
                "purple": "Positive: Wild-type IsPETase; Negative: Catalytic mutant S160A and empty pET-28a vector",
                "citation": "Lu et al. (2022) Nature; Tournier et al. (2020) Nature"
            },
            "aims": {
                "aim1": "Construct expression plasmids for 6 rational PETase active-site variants using Gibson Assembly and transform into E. coli BL21(DE3).",
                "aim2": "Express and purify recombinant enzymes via immobilized metal affinity chromatography (IMAC) and determine melting temperature (Tm) via differential scanning fluorimetry (DSF).",
                "aim3": "Quantify degradation kinetics (kcat, Km) and monomer release (TPA, MHET) against post-consumer commercial PET films via reverse-phase HPLC."
            },
            "aims_contingencies": {
                "aim1_fallback": "Switch expression to Pichia pastoris with alpha-mating factor secretion if E. coli yields insoluble inclusion bodies.",
                "aim2_fallback": "Add 5% glycerol and 0.5M L-arginine during IMAC elution if engineered mutants show active-site aggregation.",
                "aim3_fallback": "Apply pre-swelling with mild eco-friendly solvents (ethanol/water 1:1) if high-crystallinity industrial PET resists degradation."
            },
            "control_triad": {
                "negative_control": "Catalytic-dead mutant S160A and empty pET-28a vector cell lysate.",
                "positive_control": "Purified wild-type Ideonella sakaiensis PETase benchmark enzyme.",
                "specificity_control": "Substrate mock control: non-PET polyesters (polycaprolactone and PLA) to verify aromatic ester specificity."
            },
            "biotech_risk_matrix": {
                "off_target": "Hydrolysis of cellular ester compounds in host. Mitigation: Periplasmic targeting or induction in stationary phase.",
                "toxicity": "Metabolic burden of high-copy plasmid expression. Mitigation: Tunable T7 promoter induction with low IPTG (0.1 mM).",
                "solubility": "Inclusion body aggregation during high-yield expression. Mitigation: Cold induction (16°C) and chaperone co-expression (GroEL-GroES).",
                "biosafety": "Accidental release of engineered E. coli with enhanced degradation capacity. Mitigation: Standard BSL-1 laboratory containment and clean autoclave destruction."
            },
            "methodology": "Target mutations will be introduced into pET-28a-FAST-PETase via site-directed mutagenesis primers. Expression in E. coli BL21(DE3) will be induced at OD600 = 0.6 using 0.2 mM IPTG at 18°C for 16 hours. Cell pellets will be lysed by sonication in 50 mM Tris-HCl buffer (pH 7.5, 300 mM NaCl) and purified through a 5 mL HisTrap HP column. Depolymerization assays will be performed by incubating 100 nM purified enzyme with 10 mg amorphous PET coupons in 1 mL buffer at 30°C with 150 rpm orbital shaking. Reaction products (TPA, MHET) will be quenched with DMSO and quantified on an Agilent 1260 Infinity HPLC equipped with a C18 column. Controls will include wild-type IsPETase (positive benchmark) and inactive S160A catalytic dead mutant (negative control).",
            "impact_data": {
                "academic": "Elucidates biophysical mechanics of how active-site hydrophobic architecture modulates aromatic polymer binding below glass transition temperature.",
                "economic": "Enables ambient-temperature enzymatic biorecycling without energy-intensive heating of waste plastic, reducing carbon emissions by 68%.",
                "societal": "Provides municipal recycling facilities with an affordable, non-toxic bio-treatment method for plastic landfill mitigation."
            },
            "competitor_data": {
                "incumbent": "Mechanical shredding and thermal extrusion: degrades polymer chains, yielding low-grade grey plastic suitable only for carpeting.",
                "emerging": "Thermophilic engineered cutinases (LCC-ICCG) operating at 72°C: requires huge electrical inputs to maintain high temperature.",
                "proposed": "Engineered Fast-PETase (I168R/S214H): Operates directly at 30°C with high kinetic turnover on post-consumer packaging.",
                "usp": "The first biocatalytic variant achieving >70% plastic breakdown at room temperature (30°C) without requiring auxiliary heating."
            },
            "swot": {
                "s": "High solubility in standard E. coli expression; rapid HPLC quantification of monomer release.",
                "w": "Recombinant enzymes accumulate in inclusion bodies if induction temperature exceeds 22°C.",
                "o": "Global single-use plastic reduction treaties creating strong industrial pull for biocatalytic solutions.",
                "t": "Chemical recycling (glycolysis/methanolysis) has established industrial scale despite harsh solvent usage."
            },
            "budget": [
                {"category": "Consumables & Reagents", "description": "Competent cells, IPTG, Ni-NTA resins, HPLC solvents, commercial PET substrate coupons", "amount": 5800},
                {"category": "Equipment & Tooling", "description": "Access to high-resolution HPLC and differential scanning fluorimeter", "amount": 2500},
                {"category": "Testing & Analytical Services", "description": "Mass spectrometry of degradation intermediates and protein sequencing", "amount": 2200},
                {"category": "Dissemination & Publication", "description": "ACS Catalysis open-access publication charges", "amount": 2500}
            ],
            "references": "Tournier, V., et al. (2020). An engineered PET depolymerase to break down and recycle plastic bottles. Nature, 580(7802), 216-219.\nLu, H., et al. (2022). Machine learning-aided engineering of hydrolases for PET depolymerization. Nature, 604(7907), 662-667.\nAustin, H. P., et al. (2018). Characterization and engineering of a plastic-degrading aromatic polyesterase. PNAS, 115(19), E4350-E4357."
        },
        {
            "student_id": "ST-2026-03",
            "student_name": "Amna Syeda & Team NutriGrain",
            "modality": "Cellular Expression",
            "chassis": "Oryza sativa indica (Rice)",
            "tool": "Maize Phytoene Synthase (ZmPSY1) and Bacterial Desaturase (CrtI)",
            "target": "Provitamin A (beta-carotene) biosynthetic pathway in rice endosperm",
            "query": '("Golden Rice" OR "provitamin A") AND ("phytoene synthase" OR "ZmPSY1") AND "endosperm" AND "biofortification"',
            "title": "Optimization of Phytoene Synthase Expression in Golden Rice Endosperm for Provitamin A Biofortification",
            "abstract": "Vitamin A deficiency remains a devastating nutritional affliction affecting over 190 million preschool children in developing nations where milled rice constitutes the predominant dietary caloric intake. Because the endosperm of wild-type Oryza sativa naturally lacks carotenoid pigments despite synthesizing the early isoprenoid precursor geranylgeranyl diphosphate (GGPP), engineered biofortified 'Golden Rice' introduces exogenous phytoene synthase (psy) and carotene desaturase (crtI) genes. However, first-generation lines exhibited insufficient beta-carotene accumulation due to promoter attenuation and uncoordinated enzymatic flux. In this proposal, we engineer an enhanced multi-gene expression cassette utilizing the endosperm-specific glutelin promoter (Gt1) driving a codon-optimized Zea mays phytoene synthase (ZmPSY1) coupled to Erwinia uredovora crtI. The construct will be delivered via Agrobacterium tumefaciens-mediated transformation into elite indica varieties. We anticipate achieving >30 ug/g dry grain beta-carotene yield, providing 60% of the recommended dietary allowance (RDA) in a standard 100g daily serving.",
            "funnel": {
                "tier1": "Micronutrient malnutrition, notably Vitamin A deficiency (VAD), causes irreversible childhood blindness in 500,000 children annually and exacerbates pediatric mortality.",
                "tier2": "Milled white rice provides over 70% of daily calories across South and Southeast Asia, but its starchy endosperm lacks provitamin A carotenoids.",
                "tier3": "First-generation Golden Rice (GR1) synthesized only 1.6 ug/g carotenoids due to low catalytic efficiency of the daffodil phytoene synthase enzyme.",
                "tier4": "We hypothesize that utilizing codon-optimized maize ZmPSY1 under the stringent endosperm-specific Gt1 promoter will increase provitamin A synthesis above 30 ug/g without inducing yield penalties."
            },
            "matrix": {
                "blue": "Yield: 32 ug/g beta-carotene; Bioavailability: 3.8:1 conversion ratio; Stability: 85% post-storage",
                "yellow": "Agrobacterium-mediated transformation with endosperm-specific Gt1 glutelin promoter",
                "green": "Post-harvest carotenoid degradation during prolonged tropical storage under elevated humidity",
                "purple": "Positive: Proven GR2 event lines; Negative: Untransformed wild-type indica parental cultivar",
                "citation": "Paine et al. (2005) Nature Biotechnology; Ye et al. (2000) Science"
            },
            "aims": {
                "aim1": "Assemble a binary T-DNA construct harboring codon-optimized ZmPSY1 and CrtI under the rice endosperm-specific Gt1 promoter using Golden Gate cloning.",
                "aim2": "Generate transgenic indica rice lines via Agrobacterium tumefaciens-mediated embryogenic callus transformation and confirm stable single-copy integration by Southern blot.",
                "aim3": "Quantify carotenoid profiles (beta-carotene, lutein, zeaxanthin) in polished grain across 3 harvest generations using reverse-phase HPLC."
            },
            "aims_contingencies": {
                "aim1_fallback": "Use alternative endosperm promoter (e.g. prolamin) if Gt1 promoter methylation leads to gene silencing.",
                "aim2_fallback": "Utilize particle bombardment / biolistics if Agrobacterium embryogenic callus transformation frequency is < 2%.",
                "aim3_fallback": "Test natural antioxidant co-expression (e.g. alpha-tocopherol) if post-harvest beta-carotene degradation exceeds 30%."
            },
            "control_triad": {
                "negative_control": "Untransformed wild-type parental indica rice grain grown under identical greenhouse conditions.",
                "positive_control": "Certified reference GR2 event grain with established 30 ug/g carotenoid baseline.",
                "specificity_control": "Isogenic line expressing only empty pCAMBIA1300 vector to rule out tissue-culture somaclonal variation."
            },
            "biotech_risk_matrix": {
                "off_target": "Pleiotropic growth penalty due to GGPP precursor depletion from plant hormone (gibberellin) synthesis. Mitigation: Stringent endosperm-specific Gt1 promoter expression.",
                "toxicity": "No toxicity to consumer, but potential insect herbivory changes due to carotenoid alteration. Mitigation: Standard greenhouse biosafety netting.",
                "solubility": "Carotenoid oxidative degradation in humid tropical storage. Mitigation: Hermetic storage bags with oxygen scavengers.",
                "biosafety": "Gene flow via pollen drift to wild or weedy red rice (Oryza rufipogon). Mitigation: Spatial isolation buffer (≥ 100 meters) and staggered flowering times."
            },
            "methodology": "The synthetic expression cassette will be cloned into pCAMBIA1300. Immature embryos of Oryza sativa indica will be inoculated with Agrobacterium tumefaciens strain EHA105. Transgenic calli will be selected on hygromycin B (50 mg/L) and regenerated into plantlets under controlled greenhouse conditions. Grain from T1 and T2 generations will be dehusked and polished using an experimental micro-mill. Carotenoids will be extracted in cold acetone under dim light, saponified, and analyzed on a Waters Alliance HPLC with photodiode array detection at 450 nm. Positive controls will utilize certified GR2 reference grain; negative controls will evaluate untransformed wild-type parental grain.",
            "impact_data": {
                "academic": "Provides quantitative metabolic flux maps of the endosperm isoprenoid pathway and promoter-driver kinetics in tropical cereal crops.",
                "economic": "Reduces public healthcare costs associated with vitamin A deficiency supplementation and clinical ophthalmology interventions by $140M annually.",
                "societal": "Combats endemic micronutrient malnutrition in vulnerable agrarian populations without requiring changes to traditional culinary habits."
            },
            "competitor_data": {
                "incumbent": "Periodic high-dose synthetic Vitamin A capsule distribution: cost-inefficient ($2.50/dose), low rural reach, logistically vulnerable.",
                "emerging": "Dietary diversification campaigns: difficult to sustain in low-income populations living below the poverty threshold.",
                "proposed": "Self-sustaining biofortified Golden Rice: farmers save and replant seed freely with no recurring intervention costs.",
                "usp": "The only staple-food biofortification solution providing >60% of child Vitamin A requirements in a single daily bowl of rice."
            },
            "swot": {
                "s": "Proven safety record across regulatory approvals in Australia, New Zealand, USA, Canada, and the Philippines.",
                "w": "Vulnerability of carotenoids to oxidative degradation during open-air grain storage in tropical heat.",
                "o": "Recent deregulation in Southeast Asia establishing legal pathways for farmer commercialization.",
                "t": "Anti-GMO political activism and localized regulatory delays delaying variety registration."
            },
            "budget": [
                {"category": "Consumables & Reagents", "description": "Tissue culture media, hygromycin, Golden Gate enzymes, HPLC carotenoid analytical standards", "amount": 6200},
                {"category": "Equipment & Tooling", "description": "Controlled-environment plant growth chamber rental and greenhouse bench space", "amount": 3400},
                {"category": "Testing & Analytical Services", "description": "Southern blotting, digital droplet PCR for copy number, and HPLC testing", "amount": 2400},
                {"category": "Dissemination & Publication", "description": "Open-access publication in Plant Biotechnology Journal", "amount": 2500}
            ],
            "references": "Ye, X., et al. (2000). Engineering the provitamin A (beta-carotene) biosynthetic pathway into (carotenoid-free) rice endosperm. Science, 287(5451), 303-305.\nPaine, J. A., et al. (2005). Improving the nutritional value of Golden Rice through increased pro-vitamin A content. Nature Biotechnology, 23(4), 482-487.\nBeyer, P., et al. (2002). Golden Rice: introducing the beta-carotene biosynthesis pathway into rice endosperm by genetic engineering to defeat vitamin A deficiency. The Journal of Nutrition, 132(3), 506S-510S."
        }
    ]

    for sample in samples:
        fname = f"{sample['student_id']}.json"
        fpath = os.path.join(DRAFTS_DIR, fname)
        # If already exists, we also enrich it if missing keys
        if os.path.exists(fpath):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    curr = json.load(f)
                dirty = False
                for k in ["aims_contingencies", "control_triad", "biotech_risk_matrix"]:
                    if k not in curr:
                        curr[k] = sample[k]
                        dirty = True
                if dirty:
                    with open(fpath, "w", encoding="utf-8") as f:
                        json.dump(curr, f, indent=2, ensure_ascii=False)
            except Exception:
                pass
        else:
            sample["updated_at"] = datetime.datetime.now().isoformat()
            sample["updated_at_readable"] = "Initial Submission"
            sample["summary"] = calculate_draft_summary(sample)
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(sample, f, indent=2, ensure_ascii=False)
