"""
Unit Tests for BioWriter Studio (BT_301 Socratic Portal).
Tests search builder, rubric auditing logic, future tense detection,
Socratic anti-cheating firewalls, Viva Voce generator, and document exports.
"""

import os
import sys
import unittest
import json
from io import BytesIO

# Add portal root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.search_builder import build_boolean_query, get_curated_examples
from core.audit_rules import (
    audit_title,
    audit_abstract,
    audit_methodology_tense,
    audit_aims_independence,
    audit_swot_pestel,
    calculate_full_rubric_audit
)
from core.socratic_engine import analyze_student_draft, generate_viva_defense_questions
from core.funnel_scaffolder import get_sentence_starters, assemble_background_narrative
from core.export_service import generate_markdown_portfolio, generate_docx_portfolio
from core.paraphrase_engine import audit_paraphrase_rhev
from core.reference_service import audit_bibliography_recency, fetch_doi_metadata
from core.slides_service import create_defense_presentation
from core.instructor_engine import get_rapid_comment_bank, compile_instructor_feedback_report
from core.impact_novelty_engine import (
    audit_gap_statement,
    audit_novelty_and_soundness,
    build_significance_search_queries,
    evaluate_proposal_logic_chain,
    audit_competitor_matrix_and_usp,
    GAP_TAXONOMY
)
from core.paper_summarizer import (
    deconstruct_paper,
    fetch_paper_abstract_and_meta,
    SAMPLE_PAPERS,
    JARGON_LEXICON
)
from app import app


class TestSearchBuilder(unittest.TestCase):
    def test_build_boolean_query(self):
        result = build_boolean_query(
            chassis="Pseudomonas putida",
            tool="PETase",
            target="polyethylene terephthalate",
            synonyms={"tool": ["MHETase"], "target": ["PET plastic"]}
        )
        self.assertIn('"Pseudomonas putida"', result["query"])
        self.assertIn('(PETase OR MHETase)', result["query"])
        self.assertIn("pubmed.ncbi.nlm.nih.gov", result["links"]["pubmed"])
        self.assertIn("scholar.google.com", result["links"]["scholar"])

    def test_curated_examples(self):
        examples = get_curated_examples()
        self.assertGreaterEqual(len(examples), 3)
        self.assertTrue(bool(examples[0].get("system") or examples[0].get("chassis")))


class TestRubricAudits(unittest.TestCase):
    def test_title_audit_all_or_none(self):
        # Vague title fails
        bad_title = audit_title("CRISPR in Wheat", chassis="Triticum aestivum", tool="Cas9")
        self.assertEqual(bad_title["score"], 0.0)
        self.assertFalse(bad_title["passed"])

        # Complete formula passes
        good_title = audit_title(
            "Targeted Base Editing in Triticum aestivum to Enhance Foliar Salinity Tolerance for Arid Agriculture",
            chassis="Triticum aestivum",
            tool="base edit"
        )
        self.assertEqual(good_title["score"], 2.0)
        self.assertTrue(good_title["passed"])

    def test_abstract_audit_word_count(self):
        empty_res = audit_abstract("")
        self.assertEqual(empty_res["score"], 0.0)

        # 280-word abstract penalized
        long_abstract = "word " * 280
        long_res = audit_abstract(long_abstract)
        self.assertTrue(any("250-word" in issue for issue in long_res["issues"]))

    def test_methodology_future_tense(self):
        # Past tense violation
        past_text = "Bacterial cultures were inoculated and enzyme activity was performed using spectrophotometry."
        res_past = audit_methodology_tense(past_text)
        self.assertLess(res_past["tense_mark"], 1.0)
        self.assertTrue(len(res_past["past_violations"]) > 0)

        # Future tense compliance
        future_text = (
            "Recombinant strains will be inoculated into LB media at 37°C. Subsequently, protein expression will be induced "
            "with 0.5 mM IPTG. Enzymatic depolymerization will undergo incubation at 50°C and will evaluate product yield via HPLC. "
            "Untransformed host cells will serve as the negative control, and purified commercial PETase will serve as the positive control."
        )
        res_future = audit_methodology_tense(future_text)
        self.assertEqual(res_future["tense_mark"], 1.0)
        self.assertGreaterEqual(res_future["score"], 10.0)

    def test_aims_domino_collapse_check(self):
        aim1 = "Screen 50,000 mutants to identify a thermostable variant."
        aim2 = "If Aim 1 works, test the candidate in mice."
        aim3 = "Pilot scale manufacturing."
        res = audit_aims_independence(aim1, aim2, aim3)
        self.assertTrue(res["has_domino_risk"])
        self.assertTrue(any("DOMINO COLLAPSE RISK" in issue for issue in res["issues"]))

    def test_swot_cliche_check(self):
        swot_data = {
            "strengths": "Good enzyme stability",
            "weaknesses": "We are students and have lack of experience",
            "opportunities": "Industry",
            "threats": "Cost"
        }
        res = audit_swot_pestel(swot_data, {"political": "x", "economic": "x", "social": "x", "technological": "x", "environmental": "x", "legal": "x"})
        self.assertTrue(any("student" in issue.lower() or "cliché" in issue.lower() or "cliche" in issue.lower() for issue in res["issues"]))

    def test_full_rubric_audit_scaling(self):
        sample_proposal = {
            "title": "Engineered Salt Bridges in Pseudomonas putida PETase to Elevate Thermostability for Plastic Bioremediation",
            "chassis": "Pseudomonas putida",
            "tool": "PETase",
            "target": "PET plastic",
            "abstract": (
                "PET plastic accumulation poses a global crisis with 350 million tons generated annually. "
                "Here, recombinant constructs expressing engineered PETase in Pseudomonas putida will be cultured and assayed. "
                "We expect to achieve a 4-fold increase in degradation rate, enabling sustainable bioremediation."
            ),
            "funnel": {
                "tier1": "PET waste accounts for over 350 million tons annually [Geyer et al., 2017].",
                "tier2": "Conventional strategies rely on wild-type PETase cleaving ester bonds with 0.13 mg/day/cm² baseline [Yoshida et al., 2016].",
                "tier3": "However, widespread deployment remains critically constrained by low thermal stability (Tm < 48°C) causing denaturation [Austin et al., 2018].",
                "tier4": "We propose to engineer salt bridges, hypothesizing that electrostatic stabilization will elevate Tm by ≥12°C and increase conversion by 3-fold."
            },
            "aims": {
                "aim1": "Express construct. Milestone: ≥20 mg/L yield.",
                "aim2": "Determine kinetics across 30-70°C. Milestone: Tm ≥65°C.",
                "aim3": "2-liter bioreactor degradation trial. Milestone: ≥80% mass loss."
            },
            "methodology": (
                "Constructs will be transformed into Pseudomonas putida. Protein expression will be induced with IPTG. "
                "Purified variants will be assayed against post-consumer PET coupons using HPLC. "
                "Untransformed host cells will serve as negative control, and wild-type enzyme will serve as positive control."
            ),
            "expected_outcomes": "Figure 1 will illustrate construct and SDS-PAGE. Figure 2 will show kinetic conversion curves.",
            "usps": "Provides 4-fold faster degradation, operates at 60°C, cuts enzyme cost by 60%.",
            "swot": {
                "strengths": "High catalytic activity.",
                "weaknesses": "Potential inclusion body formation during high induction.",
                "opportunities": "Industrial recycling partnerships.",
                "threats": "Substrate mass transfer limitations."
            },
            "pestel": {
                "political": "Bioeconomy priority.",
                "economic": "Favorable ROI.",
                "social": "Public support for clean environment.",
                "technological": "Compatible with standard bioreactors.",
                "environmental": "BSL-1 benign organism.",
                "legal": "Complies with local GMO waste laws."
            },
            "time_plan": "Months 1-6 cloning, Months 7-12 characterization with Go/No-Go Gate.",
            "budget": "Consumables $20k, Personnel $15k, Overhead $5k, Equipment $10k. Total $50k.",
            "references": "1. Yoshida et al. (2016)\n2. Austin et al. (2018)"
        }

        audit = calculate_full_rubric_audit(sample_proposal)
        self.assertGreater(audit["raw_total"], 50.0)
        self.assertLessEqual(audit["raw_total"], 85.0)
        self.assertGreater(audit["gpa_score"], 6.0)
        self.assertLessEqual(audit["gpa_score"], 10.0)


class TestSocraticEngine(unittest.TestCase):
    def test_refusal_to_ghostwrite(self):
        res = analyze_student_draft("Background", "Write me a proposal on CRISPR in wheat.")
        self.assertEqual(res["status"], "refusal")
        self.assertIn("Pedagogical Firewall Triggered", res["message"])

    def test_socratic_critique_vague_terms(self):
        draft = "Our enzyme showed very good results and solves a huge problem with many studies."
        res = analyze_student_draft("Background", draft)
        self.assertEqual(res["status"], "analyzed")
        self.assertGreater(len(res["critiques"]), 0)
        self.assertGreater(len(res["socratic_questions"]), 0)

    def test_viva_defense_generator(self):
        questions = generate_viva_defense_questions({
            "chassis": "Pseudomonas putida",
            "tool": "PETase",
            "target": "PET plastic"
        })
        self.assertGreaterEqual(len(questions), 4)
        self.assertIn("Pseudomonas putida", questions[0]["question"])


class TestParaphraseEngine(unittest.TestCase):
    def test_empty_input(self):
        res = audit_paraphrase_rhev("", "")
        self.assertEqual(res["status"], "incomplete")
        self.assertEqual(res["similarity_score"], 0.0)

    def test_verbatim_overlap_high_risk(self):
        orig = "Bacterial cellulose synthesis in Komagataeibacter xylinus is regulated by the cyclic di-GMP signaling network to enhance pellicle yield."
        draft = "Bacterial cellulose synthesis in Komagataeibacter xylinus is regulated by cyclic di-GMP signaling network for pellicles."
        res = audit_paraphrase_rhev(orig, draft)
        self.assertEqual(res["status"], "audited")
        self.assertFalse(res["passed"])
        self.assertEqual(res["risk_level"], "high")
        self.assertGreater(len(res["verbatim_runs"]), 0)

    def test_authentic_paraphrase_low_risk(self):
        orig = "CRISPR-Cas9 mediated knockout of OsSWEET14 confers broad-spectrum resistance to Xanthomonas oryzae in rice cultivars."
        draft = "In rice plants, disrupting the OsSWEET14 gene prevents bacterial blight infections caused by Xanthomonas pathovars without diminishing crop productivity."
        res = audit_paraphrase_rhev(orig, draft)
        self.assertEqual(res["status"], "audited")
        self.assertTrue(res["passed"])
        self.assertEqual(res["risk_level"], "low")
        self.assertLess(res["similarity_score"], 25.0)


class TestReferenceService(unittest.TestCase):
    def test_empty_references(self):
        res = audit_bibliography_recency("")
        self.assertEqual(res["total_count"], 0)
        self.assertFalse(res["passed_rubric"])

    def test_recency_passes_threshold(self):
        refs = (
            "1. Zhang et al. (2024). Targeted mutagenesis in maize. Nature Plants, 10, 112-120.\n"
            "2. Patel & Rao (2023). Metabolic engineering of yeast. Biotechnology Bioeng, 120, 45-56.\n"
            "3. Yoshida et al. (2022). Structural insights into PETase. ACS Catalysis, 12, 890-900.\n"
            "4. Smith et al. (2018). Historical overview of bioplastics. Bioresour Technol, 250, 1-10."
        )
        res = audit_bibliography_recency(refs)
        self.assertEqual(res["total_count"], 4)
        self.assertEqual(res["recent_count"], 3)
        self.assertEqual(res["recency_percentage"], 75.0)
        self.assertTrue(res["passed_rubric"])

    def test_recency_fails_threshold(self):
        refs = (
            "1. Smith (2010). Old paper.\n"
            "2. Johnson (2015). Another old study.\n"
            "3. Brown (2018). Third past paper.\n"
            "4. Davis (2024). Single recent work."
        )
        res = audit_bibliography_recency(refs)
        self.assertEqual(res["recency_percentage"], 25.0)
        self.assertFalse(res["passed_rubric"])

    def test_invalid_doi_format(self):
        res = fetch_doi_metadata("not-a-valid-doi")
        self.assertFalse(res["success"])
        self.assertIn("Invalid DOI format", res["error"])


class TestSlidesService(unittest.TestCase):
    def test_create_defense_presentation(self):
        data = {
            "title": "Engineering Thermostable PETase in Pseudomonas putida",
            "student_name": "Test Student",
            "overarching_aim": "Develop a biocatalytic degradation platform.",
            "aims": {
                "aim1": "Construct expression vectors. Milestone: >= 20 mg/L.",
                "aim2": "Measure degradation kinetics. Milestone: Tm >= 65 C.",
                "aim3": "2L bioreactor trial. Milestone: >= 80% plastic mass loss."
            },
            "funnel": {
                "tier1": "350M metric tons of plastic waste annually.",
                "tier2": "Wild-type enzyme exhibits 0.13 mg/day/cm2 baseline.",
                "tier3": "Thermal instability (Tm < 48 C) causes irreversible denaturation.",
                "tier4": "Engineered salt bridges will elevate thermostability."
            },
            "methodology": "Constructs will be expressed and evaluated via HPLC.",
            "swot": {"strengths": "High activity", "weaknesses": "Inclusion bodies", "opportunities": "Recycling", "threats": "Mass transfer"},
            "time_plan": "M1-M6 synthesis, M7-M12 assays",
            "budget": "Consumables: $20,000, Personnel: $15,000"
        }
        pptx_buf = create_defense_presentation(data)
        self.assertIsInstance(pptx_buf, BytesIO)
        self.assertGreater(pptx_buf.getbuffer().nbytes, 5000)


class TestInstructorEngine(unittest.TestCase):
    def test_comment_bank_structure(self):
        bank = get_rapid_comment_bank()
        self.assertIn("title", bank)
        self.assertIn("abstract", bank)
        self.assertIn("methodology", bank)
        self.assertIn("swot", bank)
        self.assertTrue(any(c["code"] == "METH-01" for c in bank["methodology"]))

    def test_compile_feedback_report(self):
        student_data = {"title": "Enzyme Study", "student_name": "Team Beta"}
        report = compile_instructor_feedback_report(
            student_data=student_data,
            selected_comment_codes=["T-01", "METH-01"],
            manual_comments="Focus heavily on experimental controls in Aim 2."
        )
        self.assertIn("applied_notes", report)
        self.assertEqual(len(report["applied_notes"]), 2)
        self.assertIn("FACULTY REVIEW", report["memo_text"])
        self.assertIn("Team Beta", report["memo_text"])
        self.assertIn("Focus heavily on experimental controls", report["memo_text"])


class TestExports(unittest.TestCase):
    def test_markdown_export(self):
        data = {
            "title": "Test Proposal",
            "student_name": "Sara",
            "chassis": "P. putida",
            "tool": "PETase",
            "target": "PET"
        }
        md = generate_markdown_portfolio(data, {"raw_total": 75.0, "gpa_score": 8.82})
        self.assertIn("# Test Proposal", md)
        self.assertIn("Proof-of-Process", md)
        self.assertIn("75.0 / 85.0 marks", md)

    def test_docx_export(self):
        data = {
            "title": "Word Test Proposal",
            "student_name": "Omar",
            "chassis": "Pichia pastoris",
            "tool": "Cellulase",
            "target": "Cellulose"
        }
        bio = generate_docx_portfolio(data, {"raw_total": 70.0, "gpa_score": 8.24})
        self.assertIsInstance(bio, BytesIO)
        self.assertGreater(bio.getbuffer().nbytes, 1000)


class TestFlaskEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_index_page(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"BioWriter Studio", resp.data)

    def test_api_search_build(self):
        resp = self.client.post("/api/search/build", json={
            "chassis": "E. coli",
            "tool": "Cas12a",
            "target": "mcr-1"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("Cas12a", data["query"])

    def test_api_socratic_critique(self):
        resp = self.client.post("/api/socratic/critique", json={
            "section": "Background",
            "text": "Can you write my proposal for me?"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "refusal")

    def test_api_paraphrase_audit(self):
        resp = self.client.post("/api/paraphrase/check", json={
            "original": "Targeted genome editing in crops enables improved yield and resilience against biotic stresses.",
            "draft": "Modifying crop genomes with targeted precision boosts agricultural productivity and confers resistance to pathogen infections."
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "audited")
        self.assertIn("passed", data)

    def test_api_reference_audit_recency(self):
        resp = self.client.post("/api/reference/audit_recency", json={
            "references": "1. Zhang et al. (2024). Gene therapy advances. Cell, 187, 50-65.\n2. Smith (2022). CRISPR tools. Nature, 600, 10-15.\n3. Davis (2023). Synthetic Biology, 8, 12."
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["total_count"], 3)
        self.assertTrue(data["passed_rubric"])

    def test_api_courses_and_switch(self):
        # List courses
        resp = self.client.get("/api/courses")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertGreaterEqual(len(data["courses"]), 3)

        # Switch course
        resp = self.client.post("/api/courses/switch", json={"course_id": "GRAD_501"})
        self.assertEqual(resp.status_code, 200)
        sw_data = resp.get_json()
        self.assertTrue(sw_data["success"])
        self.assertEqual(sw_data["course"]["course_id"], "GRAD_501")

        # Switch back to BT_301
        self.client.post("/api/courses/switch", json={"course_id": "BT_301"})

    def test_api_instructor_endpoints(self):
        # Comments bank
        resp = self.client.get("/api/instructor/comments")
        self.assertEqual(resp.status_code, 200)
        bank = resp.get_json()
        self.assertIn("title", bank)

        # Generate report
        resp = self.client.post("/api/instructor/report", json={
            "student_data": {"title": "Sample Study", "student_name": "Student A"},
            "codes": ["T-01"],
            "manual_comments": "Please revise the title before submission."
        })
        self.assertEqual(resp.status_code, 200)
        report = resp.get_json()
        self.assertEqual(len(report["applied_notes"]), 1)
        self.assertIn("FACULTY REVIEW", report["memo_text"])

    def test_api_export_docx(self):
        resp = self.client.post("/api/export/docx", json={
            "title": "Endpoint Test",
            "student_name": "Team A"
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.headers.get("Content-Type"),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    def test_api_export_pptx(self):
        resp = self.client.post("/api/export/pptx", json={
            "title": "Presentation Endpoint Test",
            "student_name": "Team Slide"
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.headers.get("Content-Type"),
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )

    def test_api_gap_audit(self):
        resp = self.client.post("/api/impact/gap_audit", json={
            "gap_text": "However, widespread industrial deployment remains critically constrained by low thermal denaturation thresholds (Tm < 48°C), causing irreversible denaturation."
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["passed"])
        self.assertTrue(data["has_contrast_pivot"])
        self.assertEqual(data["gap_type"], "performance")

    def test_api_novelty_audit(self):
        resp = self.client.post("/api/impact/novelty_audit", json={
            "title": "Engineering Salt Bridges in PETase",
            "chassis": "Pseudomonas putida",
            "tool": "PETase",
            "target": "PET plastic",
            "hypothesis": "We hypothesize that salt bridges stabilize the flexible beta-sheet because electrostatic bonds increase Tm.",
            "methodology": "Recombinant constructs will be induced with IPTG. Empty vector will serve as negative control, and purified wild-type enzyme will serve as positive control."
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["is_novel"])
        self.assertFalse(data["is_host_swap_trap"])
        self.assertGreaterEqual(data["soundness_score"], 80)

    def test_api_significance_search(self):
        resp = self.client.post("/api/impact/significance_search", json={
            "chassis": "Triticum aestivum",
            "tool": "TaHKT1;5",
            "target": "Salinity Stress in Arid Agriculture"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("pubmed_burden", data["links"])
        self.assertIn("google_market", data["links"])

    def test_api_competitor_audit(self):
        resp = self.client.post("/api/impact/competitor_audit", json={
            "competitor_data": {
                "incumbent_name": "Broth microdilution AST",
                "emerging_name": "Multiplex PCR"
            },
            "usp_text": "Unlike broth microdilution AST which delays results by 48 hours, our CRISPR-Cas12a isothermal assay delivers results in 30 minutes, enabling rapid clinical triage in decentralized clinics."
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["passed"])
        self.assertTrue(data["incumbent_named"])

    def test_api_chain_check(self):
        resp = self.client.post("/api/impact/chain_check", json={
            "funnel": {
                "tier1": "350M tons of plastic waste annually.",
                "tier3": "However, enzyme denatures at 48°C.",
                "tier4": "We hypothesize that salt bridges will increase Tm."
            },
            "aims": {
                "aim1": "Construct expression vectors.",
                "aim2": "Characterize DSC profiles."
            },
            "methodology": "Constructs will be expressed and evaluated using standard HPLC.",
            "expected_outcomes": "Figure 1: SDS-PAGE verification of soluble expression.",
            "impact": "Academic: open structural datasets. Economic: 60% bioprocess cost reduction."
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertGreaterEqual(data["filled_nodes"], 6)
        self.assertGreater(data["chain_health_pct"], 50)


class TestImpactNoveltyEngine(unittest.TestCase):
    def test_gap_taxonomy_definitions(self):
        self.assertIn("mechanistic", GAP_TAXONOMY)
        self.assertIn("performance", GAP_TAXONOMY)
        self.assertIn("methodological", GAP_TAXONOMY)
        self.assertIn("matrix", GAP_TAXONOMY)
        self.assertIn("translational", GAP_TAXONOMY)

    def test_audit_gap_statement_valid(self):
        gap = "However, widespread industrial deployment remains critically constrained by low thermal denaturation thresholds (Tm < 48°C), causing irreversible denaturation within 12 hours."
        res = audit_gap_statement(gap)
        self.assertTrue(res["passed"])
        self.assertTrue(res["has_contrast_pivot"])
        self.assertTrue(res["has_metric"])
        self.assertFalse(res["is_strawman"])

    def test_audit_gap_statement_missing_contrast(self):
        gap = "The enzyme is not very stable and stops working when it gets warm in the reactor."
        res = audit_gap_statement(gap)
        self.assertFalse(res["has_contrast_pivot"])
        self.assertLess(res["score"], 4.0)

    def test_audit_gap_statement_strawman(self):
        gap = "No one has ever studied plastic degradation before in history and nobody has studied bacteria."
        res = audit_gap_statement(gap)
        self.assertTrue(res["is_strawman"])
        self.assertTrue(any("Strawman" in issue for issue in res["issues"]))

    def test_novelty_host_swap_trap(self):
        res = audit_novelty_and_soundness(
            title="Expressing PETase in E. coli",
            chassis="Escherichia coli",
            tool="PETase",
            target="PET plastic",
            hypothesis="We will produce PETase in E. coli to degrade plastic.",
            methodology="Bacterial cultures will be grown and tested."
        )
        self.assertTrue(res["is_host_swap_trap"])
        self.assertEqual(res["risk_level"], "high")
        self.assertTrue(any("HOST-SWAP TRAP" in issue for issue in res["issues"]))

    def test_novelty_soundness_valid(self):
        res = audit_novelty_and_soundness(
            title="Engineered Salt Bridges in PETase",
            chassis="Pseudomonas putida",
            tool="PETase",
            target="PET plastic",
            hypothesis="We hypothesize that engineered salt bridges will stabilize the flexible loop because electrostatic bonds increase Tm.",
            methodology="Expression will be induced with IPTG. Empty vector transformants will serve as negative control, and commercial wild-type enzyme will serve as positive control."
        )
        self.assertFalse(res["is_host_swap_trap"])
        self.assertTrue(res["is_novel"])
        self.assertTrue(res["has_controls"])
        self.assertGreaterEqual(res["soundness_score"], 80)

    def test_competitor_matrix_and_strawman_detection(self):
        # Strawman competitor flagged
        res_straw = audit_competitor_matrix_and_usp(
            {"incumbent_name": "traditional methods"},
            "Unlike traditional methods, our tool works better."
        )
        self.assertTrue(any("Strawman Competitor" in i for i in res_straw["issues"]))

        # Specific competitor and winning formula passes
        res_good = audit_competitor_matrix_and_usp(
            {"incumbent_name": "Broth microdilution AST", "emerging_name": "Multiplex PCR"},
            "Unlike broth microdilution AST which delays results by 48 hours, our CRISPR-Cas12a assay delivers results in 30 minutes, enabling rapid clinical triage in decentralized emergency wards."
        )
        self.assertTrue(res_good["passed"])
        self.assertGreaterEqual(res_good["score"], 4.0)

    def test_proposal_logic_chain_evaluator(self):
        # Incomplete proposal
        res_empty = evaluate_proposal_logic_chain({})
        self.assertEqual(res_empty["filled_nodes"], 0)
        self.assertEqual(res_empty["chain_health_pct"], 0.0)

        # Complete proposal
        proposal = {
            "funnel": {
                "tier1": "350M metric tons of plastic waste annually [Geyer et al., 2017].",
                "tier3": "However, deployment is constrained by thermal instability (Tm < 48°C) [Austin et al., 2018].",
                "tier4": "We propose to engineer salt bridges, hypothesizing that electrostatic stabilization elevates Tm."
            },
            "aims": {
                "aim1": "Express construct. Milestone: ≥20 mg/L yield.",
                "aim2": "Determine kinetics across 30-70°C. Milestone: Tm ≥65°C."
            },
            "methodology": "Recombinant constructs will be synthesized, cloned into expression vectors, and induced with IPTG. Purified variants will be assayed against post-consumer PET coupons using HPLC with untransformed host cells as negative control.",
            "expected_outcomes": "Figure 1: SDS-PAGE verification of soluble expression. Figure 2: Kinetic progress curve.",
            "impact": "Academic: open structural datasets. Economic: 60% bioprocess cost reduction. Societal: tons of plastic diverted from landfills.",
            "time_plan": "Months 1-6 cloning, Months 7-12 characterization with Go/No-Go Gate.",
            "budget": "Consumables $20k, Personnel $15k, Overhead $5k, Equipment $10k. Total $50k.",
            "references": "1. Yoshida et al. (2016)\n2. Austin et al. (2018)"
        }
        res_full = evaluate_proposal_logic_chain(proposal)
        self.assertEqual(res_full["filled_nodes"], 10)
        self.assertEqual(res_full["chain_health_pct"], 100.0)
        self.assertTrue(res_full["is_complete"])


class TestPaperSummarizer(unittest.TestCase):
    def test_sample_papers_structure(self):
        self.assertIn("petase", SAMPLE_PAPERS)
        self.assertIn("crispr_dx", SAMPLE_PAPERS)
        self.assertIn("drought_wheat", SAMPLE_PAPERS)
        petase = SAMPLE_PAPERS["petase"]
        self.assertIn("abstract", petase)
        self.assertIn("title", petase)

    def test_deconstruct_petase(self):
        petase = SAMPLE_PAPERS["petase"]
        res = deconstruct_paper(
            text=petase["abstract"],
            title=petase["title"],
            identifier=petase["doi"],
            authors=petase["authors"],
            year=petase["year"],
            journal=petase["journal"]
        )
        self.assertEqual(res["status"], "success")
        self.assertIn("problem", res["executive_summary"])
        self.assertIn("intervention", res["executive_summary"])
        self.assertIn("main_finding", res["executive_summary"])

        # Plain English
        self.assertIn("theme", res["plain_english_explanation"])
        self.assertIn("core_analogy", res["plain_english_explanation"])
        self.assertIn("Enzymatic Plastic Upcycling", res["plain_english_explanation"]["theme"])

        # Parameters
        params = res["extracted_parameters"]
        self.assertIn("Escherichia coli", params["chassis"])
        self.assertTrue(len(params["metric_numbers"]) > 0)
        self.assertIn("negative control", params["controls"].lower())
        self.assertTrue(len(params["stated_gap"]) > 10)
        self.assertIn("burden_statistic", params)
        self.assertTrue(len(params["burden_statistic"]) > 10)
        self.assertIn("target_milestone", params)
        self.assertTrue(params["target_milestone"].startswith("Target"))
        self.assertNotIn("Empirical benchmark metrics documented in paper", params["primary_metric_sentence"])

        # Jargon buster
        self.assertTrue(len(res["jargon_buster"]) >= 1)

        # Proposal recommendations
        self.assertEqual(len(res["proposal_recommendations"]), 4)

        # Citations
        self.assertIn("Tournier", res["citations"]["apa"])
        self.assertIn("Nature", res["citations"]["apa"])

    def test_deconstruct_paper_austin_all_six_parameters(self):
        austin_text = (
            "Poly(ethylene terephthalate) (PET) is one of the most abundantly produced synthetic polymers "
            "and is accumulating in the environment at a staggering rate as discarded packaging and textiles. "
            "Here, we present a 0.92 Å resolution X-ray crystal structure of PETase, which reveals features "
            "common to both cutinases and lipases. By narrowing the binding cleft via mutation of two active-site "
            "residues to conserved amino acids in cutinases, we surprisingly observe improved PET degradation, "
            "suggesting that PETase is not fully optimized for crystalline PET degradation, despite presumably "
            "evolving in a PET-rich environment. PETase retains the ancestral α/β-hydrolase fold."
        )
        res = deconstruct_paper(
            text=austin_text,
            title="Characterization and engineering of a plastic-degrading aromatic polyesterase",
            identifier="10.1073/pnas.1718804115",
            authors="Austin, H. P. et al.",
            year=2018,
            journal="PNAS"
        )
        self.assertEqual(res["status"], "success")
        p = res["extracted_parameters"]
        # All 6 matrix parameters must be present and rich
        self.assertTrue(len(p["burden_statistic"]) > 20)
        self.assertIn("accumulating", p["burden_statistic"].lower())
        self.assertIn("0.92", p["primary_metric_sentence"])
        self.assertNotIn("Empirical benchmark metrics documented in paper", p["primary_metric_sentence"])
        self.assertTrue(len(p["stated_gap"]) > 20)
        self.assertTrue(len(p["controls"]) > 10)
        self.assertTrue(p["target_milestone"].startswith("Target"))
        self.assertIn("Austin", res["citations"]["apa"])

    def test_deconstruct_short_text_error(self):
        res = deconstruct_paper("Too short.")
        self.assertEqual(res["status"], "error")
        self.assertIn("too short", res["message"])

    def test_jargon_lexicon_matches(self):
        sample_text = (
            "We performed directed evolution to optimize codon optimization, "
            "preventing inclusion bodies and allosteric inhibition during heterologous expression."
        )
        res = deconstruct_paper(sample_text)
        terms = [j["term"] for j in res["jargon_buster"]]
        self.assertTrue(any("Directed Evolution" in t for t in terms))
        self.assertTrue(any("Inclusion Bodies" in t for t in terms))

    def test_api_paper_samples_endpoint(self):
        client = app.test_client()
        resp = client.get("/api/paper/samples")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("petase", data)
        self.assertIn("crispr_dx", data)

    def test_api_paper_summarize_endpoint(self):
        client = app.test_client()
        sample = SAMPLE_PAPERS["crispr_dx"]
        resp = client.post("/api/paper/summarize", json={
            "text": sample["abstract"],
            "title": sample["title"],
            "identifier": sample["doi"]
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("CRISPR", data["plain_english_explanation"]["theme"])
        self.assertIn("2.5 copies/uL", data["extracted_parameters"]["metric_numbers"])

    def test_api_paper_fetch_invalid(self):
        client = app.test_client()
        resp = client.post("/api/paper/fetch", json={
            "identifier": "invalid-doi-format"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertFalse(data["success"])
        self.assertIn("Invalid DOI format", data["error"])

    def test_doi_prefix_sanitization(self):
        # Verify sanitization of various DOI prefix formats
        prefixes = [
            "doi: 10.1038/s41586-020-2149-4",
            "https://doi.org/10.1038/s41586-020-2149-4",
            "\"10.1038/s41586-020-2149-4\"",
            "pmid: 29453302"
        ]
        for p in prefixes:
            res = fetch_paper_abstract_and_meta(p)
            self.assertTrue(res["success"], f"Failed on prefix format: {p}")
            self.assertGreater(len(res.get("abstract", "").split()), 20)

    def test_audit_all_writing_sections_complete(self):
        from core.audit_rules import audit_all_writing_sections
        proposal = {
            "title": "Engineering of Recombinant Leaf-Branch Compost Cutinase in Escherichia coli BL21(DE3) to Accelerate Depolymerization of Post-Consumer Poly(ethylene terephthalate)",
            "chassis": "Escherichia coli BL21(DE3)",
            "tool": "Engineered Leaf-Branch Compost Cutinase (LCC)",
            "target": "PET depolymerization rate exceeding 16.7 g/L/h",
            "abstract": "Poly(ethylene terephthalate) (PET) plastic accumulation represents a major global ecological crisis exceeding 350 million metric tons annually. In this study, recombinant cutinase variants will be engineered with disulfide bonds and active-site mutations (W159H/F238Y) to elevate thermal stability. Recombinant proteins will be expressed in Escherichia coli BL21(DE3) and assayed in a 100-L bioreactor. We anticipate achieving 90% depolymerization within 10 hours at 72°C, delivering an industrial benchmark for plastic upcycling.",
            "funnel": {
                "tier1": "Global plastic accumulation incurs over $13 billion annually in municipal management costs [1].",
                "tier2": "Conventional mechanical recycling degrades polymer chain length, while current wild-type leaf-branch cutinase protocols denature at 65°C [2].",
                "tier3": "However, catalytic deployment remains critically constrained by biophysical thermolability at the glass transition temperature of PET.",
                "tier4": "We hypothesize that introducing active-site disulfide bridges will elevate melting temperature because covalent stabilization reduces thermal unfolding entropy."
            },
            "aims": {
                "overarching": "To achieve 90% enzymatic PET depolymerization at pilot scale.",
                "aim1": "Aim 1: Rational design and expression of cutinase variants in E. coli to achieve Tm > 90°C.",
                "aim2": "Aim 2: High-throughput kinetic screening measuring initial hydrolysis rates with benchmark >10 g/L/h.",
                "aim3": "Aim 3: Pilot-scale 100-L bioreactor validation for fed-batch conversion with target >85% yield."
            },
            "methodology": "Recombinant plasmids will be transformed into E. coli BL21(DE3). Expression will be induced with 0.5 mM IPTG at 25°C. Enzymes will be purified via Ni-NTA chromatography. Wild-type cutinase will serve as the baseline control, and empty vector lysate will serve as the negative vehicle control.",
            "impact_data": {
                "academic": "Open-source thermodynamic coordinates and verified expression protocols.",
                "economic": "Reduces monomer synthesis costs by 45% compared to petrochemical synthesis.",
                "societal": "Mitigates post-consumer polyester accumulation and microplastic pollution."
            },
            "competitor_data": {
                "incumbent_name": "Mechanical Downcycling",
                "emerging_name": "Wild-Type LCC Cutinase",
                "proposed_name": "Thermostable Engineered LCC Variant",
                "usp": "High-purity terephthalic acid monomer recovery in <10 hours directly at 72°C."
            },
            "swot": {
                "s": "High catalytic conversion rate (>16 g/L/h)",
                "w": "Inclusion body formation during high-density cell fermentation",
                "o": "Commercial licensing with textile bottle manufacturers",
                "t": "Proteolytic cleavage during extended fed-batch fermentation"
            },
            "references": "1. Tournier, V. et al. (2020). Nature, 580, 216-219.\n2. Austin, H. P. et al. (2018). PNAS, 115, E4350.\n3. Lu, H. et al. (2022). Nature, 604, 662-667.\n4. Chen, C. C. et al. (2021). Nat Commun, 12, 1-10.\n5. Cui, Y. et al. (2021). ACS Catal, 11, 788-795."
        }
        res = audit_all_writing_sections(proposal)
        self.assertEqual(res["summary"]["total_sections"], 9)
        self.assertGreaterEqual(res["summary"]["passed_sections"], 7)
        self.assertEqual(res["summary"]["overall_status"], "Ready for Submission")

    def test_api_writing_audit_endpoint(self):
        client = app.test_client()
        resp = client.post("/api/writing/audit_all", json={
            "title": "A Study of Enzymes",
            "methodology": "We incubated the samples at 37 degrees and measured absorbance."
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["summary"]["total_sections"], 9)
        # Verify that past tense is flagged in methodology
        method_sec = next(s for s in data["sections"] if s["id"] == "sec_methodology")
        self.assertIn("warning", method_sec["status"])

    def test_faculty_view_route(self):
        client = app.test_client()
        resp = client.get("/faculty")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"BioWriter Faculty Studio", resp.data)
        self.assertIn(b"BT_301", resp.data)


if __name__ == "__main__":
    unittest.main()

