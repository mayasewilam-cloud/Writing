import unittest
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app import app
from core.breakthroughs_manager import (
    get_breakthroughs_catalog,
    sync_europepmc_breakthroughs,
    toggle_breakthrough_bookmark,
    _extract_verified_year,
    synthesize_paper_to_breakthrough,
    CREATORS,
    COPYRIGHT_NOTICE,
    FOUNDATIONAL_BREAKTHROUGHS
)
from core.export_service import generate_docx_portfolio, generate_markdown_portfolio
from core.slides_service import create_defense_presentation


class TestBreakthroughsRadar(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_creators_attribution(self):
        """Verify the academic authorship is properly attributed to Maya Abdelrazek & Youssef Aboulkheir."""
        self.assertEqual(CREATORS, "Maya Abdelrazek & Youssef Aboulkheir")
        self.assertIn("Maya Abdelrazek", COPYRIGHT_NOTICE)
        self.assertIn("Youssef Aboulkheir", COPYRIGHT_NOTICE)

    def test_foundational_catalog_integrity(self):
        """Verify all 16 foundational breakthroughs from the biotech learning app are loaded with valid schemas."""
        self.assertEqual(len(FOUNDATIONAL_BREAKTHROUGHS), 16)
        catalog = get_breakthroughs_catalog(storage_filter="foundational")
        self.assertEqual(catalog["counts"]["foundational"], 16)
        self.assertEqual(len(catalog["items"]), 16)

        for item in catalog["items"]:
            self.assertEqual(item["storage_source"], "foundational")
            self.assertTrue(item["title"])
            self.assertTrue(item["category"])
            self.assertTrue(item["year"])
            # Validate educational schema
            edu = item.get("educational", {})
            self.assertTrue(edu.get("what_is_it"))
            self.assertTrue(edu.get("problem_solved"))
            steps = edu.get("how_it_works")
            self.assertTrue(steps)
            if isinstance(steps, list):
                self.assertGreaterEqual(len(steps), 3)
            elif isinstance(steps, dict):
                self.assertTrue(steps.get("step1"))
            self.assertTrue(edu.get("why_it_matters"))
            # Validate technical schema
            tech = item.get("technical", {})
            self.assertTrue(tech.get("mechanism"))
            self.assertTrue(tech.get("primary_metric"))
            self.assertTrue(tech.get("controls"))
            self.assertTrue(tech.get("citation"))

    def test_no_filler_words_in_catalog(self):
        """Verify that zero generic filler sentences from the legacy app exist in the catalog."""
        filler_patterns = [
            "prior methods were limited by biological constraints",
            "prior methods were limited",
            "lorem ipsum",
            "filler text",
            "placeholder",
            "[fill in]",
            "technical bottlenecks. this study addresses these challenges"
        ]
        catalog = get_breakthroughs_catalog(storage_filter="all")
        for item in catalog["items"]:
            edu = item.get("educational", {})
            tech = item.get("technical", {})
            full_text = " ".join([
                item.get("title", ""),
                edu.get("what_is_it", ""),
                edu.get("problem_solved", ""),
                edu.get("why_it_matters", ""),
                tech.get("mechanism", ""),
                tech.get("primary_metric", ""),
                tech.get("significance", "")
            ]).lower()

            for pattern in filler_patterns:
                self.assertNotIn(
                    pattern,
                    full_text,
                    f"Found legacy filler phrase '{pattern}' in breakthrough ID {item['id']}"
                )

    def test_verified_year_extraction(self):
        """Verify that publication year cross-referencing accurately extracts genuine publication years."""
        # Case 1: firstPublicationDate is available
        paper1 = {
            "firstPublicationDate": "2023-04-15",
            "pubYear": "2026",
            "journalInfo": {"year": 2024}
        }
        self.assertEqual(_extract_verified_year(paper1), 2023)

        # Case 2: journalInfo year is available
        paper2 = {
            "pubYear": "2026",
            "journalInfo": {"year": 2024}
        }
        self.assertEqual(_extract_verified_year(paper2), 2024)

        # Case 3: only pubYear
        paper3 = {
            "pubYear": "2025"
        }
        self.assertEqual(_extract_verified_year(paper3), 2025)

        # Case 4: Invalid/out-of-range fallback
        paper4 = {
            "pubYear": "1800"
        }
        self.assertEqual(_extract_verified_year(paper4), 2026)

    def test_storage_filters_and_categories(self):
        """Test filtering by storage type, category, and search terms."""
        # Storage filter: Foundational
        cat_foundational = get_breakthroughs_catalog(storage_filter="foundational")
        self.assertTrue(all(x["storage_source"] == "foundational" for x in cat_foundational["items"]))

        # Storage filter: Live
        cat_live = get_breakthroughs_catalog(storage_filter="live")
        self.assertTrue(all(x["storage_source"] == "live" for x in cat_live["items"]))

        # Category filter: gene_editing
        cat_crispr = get_breakthroughs_catalog(category="gene_editing")
        self.assertGreater(len(cat_crispr["items"]), 0)
        for x in cat_crispr["items"]:
            self.assertTrue(x["category"] == "gene_editing" or "gene editing" in x.get("category_label", "").lower())

        # Search query: "Cas9"
        cat_search = get_breakthroughs_catalog(search_query="Cas9")
        self.assertGreater(len(cat_search["items"]), 0)
        self.assertTrue(any("cas9" in x["title"].lower() or "cas9" in x.get("technical", {}).get("mechanism", "").lower() for x in cat_search["items"]))

    def test_bookmark_persistence(self):
        """Test bookmarking and unbookmarking breakthroughs."""
        test_id = "breakthrough_alphafold3"
        res1 = toggle_breakthrough_bookmark(test_id)
        is_bm1 = res1["is_bookmarked"]

        # Toggle again should invert the state
        res2 = toggle_breakthrough_bookmark(test_id)
        self.assertEqual(res2["is_bookmarked"], not is_bm1)

        # Toggle back to original
        toggle_breakthrough_bookmark(test_id)

    def test_synthesize_paper_to_breakthrough(self):
        """Test converting raw Europe PMC paper record into fully populated breakthrough object."""
        sample_paper = {
            "id": "PMC9999999",
            "title": "Prime editing mediated correction of beta-thalassemia mutations in human hematopoietic stem cells.",
            "authorString": "Zhang L, Miller J, Aboulkheir Y.",
            "journalTitle": "Nature Biotechnology",
            "pubYear": "2026",
            "firstPublicationDate": "2026-02-10",
            "doi": "10.1038/s41587-026-0001-x",
            "abstractText": "Beta-thalassemia is caused by genetic defects in HBB. Prior gene therapy approaches caused random insertional mutagenesis. Here we demonstrate prime editing achieving 82% correction efficiency with no detectable off-target cleavage, compared to 12% baseline homology-directed repair in wild-type controls."
        }
        bt = synthesize_paper_to_breakthrough(sample_paper)
        self.assertEqual(bt["storage_source"], "live")
        self.assertEqual(bt["year"], 2026)
        self.assertIn("Zhang L", bt["technical"]["citation"])
        self.assertIn("Nature Biotechnology", bt["technical"]["citation"])
        # Check that problem and mechanism were extracted
        self.assertTrue(bt["educational"]["what_is_it"])
        self.assertTrue(bt["educational"]["problem_solved"])
        self.assertTrue(bt["technical"]["primary_metric"])

    def test_api_endpoints(self):
        """Test Flask REST API routes for Breakthroughs."""
        # GET /api/breakthroughs
        resp = self.client.get("/api/breakthroughs?storage_filter=all")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["creators"], "Maya Abdelrazek & Youssef Aboulkheir")
        self.assertIn("Maya Abdelrazek", data["copyright"])
        self.assertGreater(len(data["items"]), 0)

        # POST /api/breakthroughs/bookmark
        bm_resp = self.client.post("/api/breakthroughs/bookmark", json={"id": "breakthrough_prime_editing"})
        self.assertEqual(bm_resp.status_code, 200)
        bm_data = json.loads(bm_resp.data)
        self.assertEqual(bm_data["status"], "success")
        self.assertIn("is_bookmarked", bm_data)

        # POST /api/breakthroughs/sync
        sync_resp = self.client.post("/api/breakthroughs/sync", json={"topic": "CRISPR Cas12a"})
        self.assertEqual(sync_resp.status_code, 200)
        sync_data = json.loads(sync_resp.data)
        self.assertEqual(sync_data["status"], "success")
        self.assertEqual(sync_data["creators"], "Maya Abdelrazek & Youssef Aboulkheir")

    def test_authorship_watermark_in_exports(self):
        """Verify that intellectual property watermarks for Maya Abdelrazek & Youssef Aboulkheir are embedded across exports."""
        test_data = {
            "title": "Engineered Cas12a Biosensor for Colistin Resistance",
            "student_name": "Test Investigator",
            "chassis": "Acinetobacter baumannii",
            "tool": "CRISPR-Cas12a",
            "target": "mcr-1 gene detection",
            "abstract": "A structured abstract demonstrating academic excellence.",
            "funnel": {
                "tier1": "Colistin-resistant infections cause 700,000 deaths annually.",
                "tier2": "Standard PCR takes 24 hours.",
                "tier3": "Lack of rapid isothermal detection at point of care.",
                "tier4": "Deploying Cas12a collateral cleavage resolves this."
            },
            "aims": {
                "aim1": "Synthesize guide RNA",
                "aim2": "Calibrate detection limit",
                "aim3": "Validate in clinical specimens"
            },
            "methodology": "The system will be evaluated using RPA coupled with fluorophore-quencher ssDNA probes."
        }

        # 1. Markdown Export Watermark
        md_text = generate_markdown_portfolio(test_data)
        self.assertIn("Maya Abdelrazek & Youssef Aboulkheir", md_text)
        self.assertIn("Protected Intellectual Property", md_text)

        # 2. DOCX Export Watermark
        docx_bytes = generate_docx_portfolio(test_data)
        self.assertGreater(docx_bytes.getbuffer().nbytes, 1000)
        # Check core properties on freshly created doc
        from docx import Document
        doc = Document(docx_bytes)
        self.assertEqual(doc.core_properties.author, "Maya Abdelrazek & Youssef Aboulkheir")
        self.assertIn("Maya Abdelrazek & Youssef Aboulkheir", doc.core_properties.comments)

        # 3. PPTX Export Watermark
        pptx_bytes = create_defense_presentation(test_data)
        self.assertGreater(pptx_bytes.getbuffer().nbytes, 1000)
        from pptx import Presentation
        prs = Presentation(pptx_bytes)
        self.assertEqual(prs.core_properties.author, "Maya Abdelrazek & Youssef Aboulkheir")


if __name__ == "__main__":
    unittest.main()
