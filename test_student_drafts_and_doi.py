import os
import sys
import unittest
import json

# Add portal root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from core.draft_store import (
    save_student_draft,
    get_student_draft,
    list_student_drafts,
    calculate_draft_summary,
    sanitize_student_id
)
from core.paper_summarizer import (
    fetch_paper_abstract_and_meta,
    deconstruct_paper
)


class TestStudentDraftsAndDOI(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_sanitize_student_id(self):
        self.assertEqual(sanitize_student_id("ST-2026-01"), "ST-2026-01")
        self.assertEqual(sanitize_student_id("Team #1 / Bio!"), "Team__1___Bio")
        self.assertEqual(sanitize_student_id(""), "student_draft")

    def test_calculate_draft_summary(self):
        data = {
            "title": "Biofortification Study in Rice Crops",
            "abstract": "This study aims to optimize the biosynthesis of beta-carotene in rice endosperm through targeted transgenic expression of phytoene synthase.",
            "chassis": "Rice",
            "tool": "PSY1",
            "query": "Rice AND PSY1",
            "matrix": {"blue": "32 ug/g", "green": "Post-harvest loss"},
            "funnel": {"tier1": "Malnutrition affects millions worldwide each year in agrarian communities."},
            "aims": {"aim1": "Assemble plasmid construct harboring codon-optimized ZmPSY1 under endosperm promoter."},
            "methodology": "Transgenic rice lines will be transformed via Agrobacterium tumefaciens mediated tissue culture.",
            "impact_data": {"academic": "Metabolic flux map"},
            "competitor_data": {"usp": "Single daily serving"},
            "swot": {"s": "Proven safety", "w": "Storage loss"},
            "references": "Ye et al. (2000) Science."
        }
        res = calculate_draft_summary(data)
        self.assertEqual(res["completed_nodes"], 10)
        self.assertEqual(res["completion_percentage"], 100)
        self.assertGreater(res["word_count"], 20)

    def test_save_and_get_student_draft(self):
        test_sid = "TEST_STUDENT_99"
        test_data = {
            "student_name": "Test Student 99",
            "title": "Novel Biosensor Development",
            "modality": "Cell-Free Diagnostics",
            "chassis": "Cell-free lysate",
            "tool": "Cas12a"
        }
        save_res = save_student_draft(test_sid, test_data)
        self.assertTrue(save_res["success"])
        self.assertEqual(save_res["student_id"], test_sid)

        fetched = get_student_draft(test_sid)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["title"], "Novel Biosensor Development")
        self.assertEqual(fetched["student_name"], "Test Student 99")

    def test_list_student_drafts(self):
        roster = list_student_drafts()
        self.assertIsInstance(roster, list)
        self.assertGreaterEqual(len(roster), 3)
        sids = [r["student_id"] for r in roster]
        self.assertIn("ST-2026-01", sids)
        self.assertIn("ST-2026-02", sids)
        self.assertIn("ST-2026-03", sids)

    def test_api_student_draft_routes(self):
        # 1. Save draft via API
        resp = self.client.post("/api/student/save_draft", json={
            "student_id": "ST_API_TEST",
            "student_data": {
                "student_name": "API Student",
                "title": "Enzymatic Biorecycling",
                "modality": "Cellular Expression"
            }
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])

        # 2. Get drafts list
        resp2 = self.client.get("/api/student/drafts")
        self.assertEqual(resp2.status_code, 200)
        drafts = resp2.get_json()
        self.assertTrue(any(d["student_id"] == "ST_API_TEST" for d in drafts))

        # 3. Get specific draft
        resp3 = self.client.get("/api/student/draft/ST_API_TEST")
        self.assertEqual(resp3.status_code, 200)
        self.assertEqual(resp3.get_json()["draft"]["student_name"], "API Student")

        # 4. Get 404 for non-existent student
        resp4 = self.client.get("/api/student/draft/NON_EXISTENT_STUDENT_XYZ")
        self.assertEqual(resp4.status_code, 404)

    def test_api_compile_memo_and_report_alias(self):
        payload = {
            "student_data": {"student_name": "Sara", "title": "CRISPR Proposal"},
            "selected_codes": ["HYP-01"],
            "manual_comments": "Great work on the experimental design."
        }
        resp = self.client.post("/api/instructor/compile_memo", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("memo_text", data)
        self.assertIn("CRISPR Proposal", data["memo_text"])

    def test_doi_fetch_golden_rice_with_tldr(self):
        # Exact DOI tested by user in uploaded screenshot
        doi = "10.1007/978-981-15-5337-0_25"
        res = fetch_paper_abstract_and_meta(doi)
        if not res.get("success"):
            self.skipTest(f"Live DOI fetch skipped due to network timeout: {res.get('error')}")
        self.assertIn("Golden Rice", res.get("title", ""))
        self.assertGreater(len(res.get("abstract", "")), 30)
        self.assertTrue("is_tldr" in res or len(res.get("abstract", "")) > 50)

        decomp = deconstruct_paper(
            text=res["abstract"],
            title=res["title"],
            identifier=res["id"],
            authors=res["authors"],
            year=res["year"],
            journal=res["journal"]
        )
        self.assertEqual(decomp.get("status"), "success")
        self.assertIn("plain_english_explanation", decomp)
        self.assertIn("extracted_parameters", decomp)
        self.assertIn("parameter_explanations", decomp)

    def test_matrix_paper_explanations_and_summarization(self):
        sample_abstract = (
            "Over 350 million tons of plastic waste pollute ecosystems annually. "
            "Here, we engineered a thermostable PETase variant exhibiting a degradation rate "
            "of 1.2 mg/day/cm2 at 50°C, compared to wild-type PETase at 0.13 mg/day/cm2. "
            "Empty-plasmid mock lysates served as negative control. "
            "However, commercial depolymerization remains limited by high crystallinity substrates."
        )
        decomp = deconstruct_paper(
            text=sample_abstract,
            title="Engineered PETase Study",
            identifier="10.1038/s41586-020-2149-4",
            authors="Tournier, V. et al.",
            year=2020,
            journal="Nature"
        )
        self.assertEqual(decomp["status"], "success")
        self.assertIn("parameter_explanations", decomp)
        pe = decomp["parameter_explanations"]
        self.assertIn("burden_explanation", pe)
        self.assertIn("benchmark_explanation", pe)
        self.assertIn("gap_explanation", pe)
        self.assertIn("controls_explanation", pe)
        self.assertIn("milestone_explanation", pe)
        self.assertIn("citation_explanation", pe)

        self.assertIn("350 million", pe["burden_explanation"])
        self.assertIn("Nature", pe["citation_explanation"])

        # Test API endpoint
        resp = self.client.post("/api/paper/summarize", json={
            "text": sample_abstract,
            "title": "Engineered PETase Study",
            "identifier": "10.1038/s41586-020-2149-4",
            "authors": "Tournier, V. et al.",
            "year": 2022,
            "journal": "Nature"
        })
        self.assertEqual(resp.status_code, 200)
        api_data = resp.get_json()
        self.assertIn("parameter_explanations", api_data)
        self.assertIn("2021–2026", api_data["parameter_explanations"]["citation_explanation"])


if __name__ == "__main__":
    unittest.main()
