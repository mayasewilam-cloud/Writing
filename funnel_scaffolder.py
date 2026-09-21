"""
Inverted Funnel Paragraph Scaffolder for BT_301 & Scientific Grant Writing.
Provides formal academic metadiscourse sentence structures and rhetorical frames
for constructing authoritative grant background arguments.
"""

from typing import Dict, List, Any


def get_sentence_starters() -> Dict[str, List[Dict[str, str]]]:
    """
    Returns rigorous, formal academic sentence starters for each tier of the Inverted Funnel.
    """
    return {
        "tier1": [
            {
                "title": "Epidemiological / Global Impact Frame",
                "template": "[Target Condition / Contaminant / Disease] represents an escalating global healthcare and economic challenge, accounting for an estimated [Quantified Statistical Metric, e.g., 1.27 million attributable deaths / 350 million metric tons] annually [Citation].",
                "example": "Multidrug-resistant Gram-negative bacterial infections represent an escalating global healthcare crisis, accounting for an estimated 1.27 million direct attributable deaths annually [Murray et al., 2022]."
            },
            {
                "title": "Industrial / Sector Economic Loss Frame",
                "template": "In [Target Sector / Agricultural Region], [Contaminant / Pathological Stress] inflicts substantial systemic damage, generating an estimated annual economic loss exceeding [Monetary Figure / Yield Percentage] [Citation].",
                "example": "In semi-arid Mediterranean agriculture, foliar salinity stress inflicts substantial systemic damage, generating an estimated annual wheat harvest loss exceeding 35% [World Bank, 2023]."
            }
        ],
        "tier2": [
            {
                "title": "Current Scientific Benchmark & Baseline Frame",
                "template": "Conventional mitigation strategies predominantly rely on [Current Standard Protocol or Technological Benchmark], which operates via [Biochemical / Biophysical Mechanism] to achieve a reported baseline [Performance Metric] [Citation].",
                "example": "Conventional remediation strategies predominantly rely on enzymatic depolymerization utilizing wild-type Ideonella sakaiensis PETase, which cleaves ester bonds within the polymer backbone to yield a baseline degradation rate of 0.13 mg/day/cm² [Yoshida et al., 2016]."
            },
            {
                "title": "Current Diagnostic / Therapeutic Standard Frame",
                "template": "At present, standard detection of [Biomarker / Pathogen] relies upon [Gold Standard Clinical Assay], which demonstrates an analytical sensitivity of [Baseline Metric] with a turnaround time of [Duration] [Citation].",
                "example": "At present, standard detection of the colistin resistance gene mcr-1 relies upon quantitative PCR (qPCR), which demonstrates an analytical sensitivity of 100 CFU/mL with an operational turnaround time of 4 to 6 hours [Liu et al., 2016]."
            }
        ],
        "tier3": [
            {
                "title": "Mechanistic Bottleneck & Knowledge Gap Frame",
                "template": "However, widespread translational implementation remains critically constrained by [Specific Biophysical / Biochemical Failure Mode], which compromises [Operational Parameter] and limits functional performance to below [Empirical Failure Metric] [Citation].",
                "example": "However, widespread industrial deployment remains critically constrained by the low thermal unfolding transition (Tm < 48°C), which triggers irreversible active-site denaturation and limits operational catalytic half-life to under 2.5 hours in bioreactor environments [Austin et al., 2018]."
            },
            {
                "title": "Selectivity / Off-Target Barrier Frame",
                "template": "Despite recent incremental advancements, existing interventions fail to overcome [Specific Biophysical Limitation], predominantly driven by [Underlying Molecular Cause], thereby introducing substantial risks of [Adverse Failure Mode] [Citation].",
                "example": "Despite recent incremental advancements, current Cas9 editing platforms fail to prevent off-target double-stranded breaks at non-canonical protospacer adjacent motifs, predominantly driven by conformational tolerance to distal mismatches [Kim et al., 2022]."
            }
        ],
        "tier4": [
            {
                "title": "Mechanistic Hypothesis & Quantitative Objective Frame",
                "template": "To resolve this critical bottleneck, this project proposes to engineer [Engineered Molecular Tool / Formulation] integrated within [Experimental System / Matrix]. We hypothesize that [Specific Molecular Mechanism] will [Biophysical Effect], thereby elevating [Target Performance Metric] to [Target Benchmark Threshold].",
                "example": "To resolve this critical bottleneck, this project proposes to engineer stabilizing salt bridges (K142-D180) into PETase expressed in Pseudomonas putida. We hypothesize that introducing complementary electrostatic interactions will rigidify the flexible catalytic cleft, elevating thermal unfolding temperature Tm by ≥12°C and increasing 24-hour polymer conversion by ≥3-fold."
            }
        ]
    }


def assemble_background_narrative(funnel_data: Dict[str, str]) -> str:
    paragraphs = [
        funnel_data.get("tier1", "").strip(),
        funnel_data.get("tier2", "").strip(),
        funnel_data.get("tier3", "").strip(),
        funnel_data.get("tier4", "").strip()
    ]
    return "\n\n".join([p for p in paragraphs if p])
