# 🧬 BioWriter Studio • BT_301 Research & Proposal Writing Suite

> **Comprehensive Scientific Proposal Engineering, Rubric Audits, and Literature Intelligence Platform.**
> Developed & Architected by **Maya Abdelrazek & Youssef Aboulkheir** for **BT_301: Introduction to Biotechnology**.

---

## 🚀 1-Click Deployment to Vercel (Free)

This repository is pre-configured with `vercel.json` and Python serverless support.

1. Fork or upload this repository to your **GitHub** account.
2. Log into [Vercel.com](https://vercel.com) using your GitHub account.
3. Click **"Add New..."** ➔ **"Project"** ➔ Import this repository.
4. Click **"Deploy"**!
5. In ~45 seconds, your live site will be ready at `https://your-repo-name.vercel.app` with full styling and backend functionality.

---

## 📦 What's Inside This Repository

* **`app.py`**: The complete Flask web server with REST endpoints, automatic fail-safe static asset routes, and Socratic intelligence.
* **`vercel.json`**: Vercel configuration for `@vercel/python` zero-config serverless deployment.
* **`Procfile`**: Standard deployment configuration for Render, Railway, and Heroku.
* **`requirements.txt`**: Minimal, production-tested dependencies (`Flask`, `python-docx`, `python-pptx`, `requests`, `Werkzeug`, `gunicorn`, `whitenoise`).
* **`templates/`**:
  * `index.html`: The full BioWriter Studio student workspace (Research Landscape, Dynamic Gantt Scheduler, Evidence Matrix, Split Preprint view, Figures Hub, Breakthroughs).
  * `faculty.html`: The faculty grading, rubric review, and cohort evaluation dashboard.
* **`static/`**:
  * `css/studio.css`: Publication-grade styles, badge tiers, and responsive layout.
  * `js/studio.js`: Full client-side engine (dynamic Gantt visualizer, DOI decoder, live rubric audits, bill of materials recalculator).
  * `favicon.svg` & `favicon.ico`: Crisp vector brand icons.
* **`core/`**:
  * `paper_summarizer.py`: Research Landscape & Gap deconstruction engine with 6-tier scholarly cascade (Europe PMC, PubMed, Semantic Scholar, CrossRef).
  * `export_service.py`: Generates formatted Microsoft Word (`.docx`) and Markdown documents with dynamic Gantt and comparative position matrices.
  * `audit_rules.py`: Instant rubric compliance audits.
  * `auth_store.py`: Student registration and cryptographic PBKDF2 authentication with serverless `/tmp` compatibility.
  * `draft_store.py`: Server-side draft management and auto-save.
  * `breakthroughs_manager.py`: Biotechnology Breakthroughs Intelligence Suite.
  * `slides_service.py`: PowerPoint (`.pptx`) defense deck generator.
* **`config/`**: Course syllabus and rubric specifications (`BT_301`, `GRAD_501`, `GRANT_STDF`).
* **`data/`**: Pre-seeded demo user accounts and foundational breakthrough data.

---

## 💻 Running Locally (Optional)

```bash
pip install -r requirements.txt
python app.py
```
Open your browser to: `http://127.0.0.1:5000`

---

## 🛡️ Academic Framework & Copyright

**BioWriter Studio** is an academic innovation architected by **Maya Abdelrazek & Youssef Aboulkheir**.  
Protected Academic Intellectual Property • All Rights Reserved © 2026.
