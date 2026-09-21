"""
BioWriter Studio: Comprehensive Scientific Proposal & Writing Portal.
Server application serving the interactive student workspace and REST API.
Includes: Search Builder, RHEV Paraphrase Lab, DOI Reference Service,
PowerPoint Slides Service, Socratic Engine, Rubric Audits, and Instructor Studio.
"""

import os
import json
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory, session
from core.search_builder import build_boolean_query, get_curated_examples
from core.socratic_engine import analyze_student_draft, generate_viva_defense_questions
from core.audit_rules import (
    calculate_full_rubric_audit,
    audit_title,
    audit_abstract,
    audit_methodology_tense,
    audit_all_writing_sections
)
from core.funnel_scaffolder import get_sentence_starters, assemble_background_narrative
from core.export_service import generate_docx_portfolio, generate_markdown_portfolio
from core.paraphrase_engine import audit_paraphrase_rhev
from core.reference_service import fetch_doi_metadata, audit_bibliography_recency
from core.slides_service import create_defense_presentation
from core.instructor_engine import get_rapid_comment_bank, compile_instructor_feedback_report
from core.impact_novelty_engine import (
    GAP_TAXONOMY,
    audit_gap_statement,
    audit_novelty_and_soundness,
    build_significance_search_queries,
    evaluate_proposal_logic_chain,
    audit_competitor_matrix_and_usp
)
from core.paper_summarizer import (
    fetch_paper_abstract_and_meta,
    deconstruct_paper,
    SAMPLE_PAPERS,
    JARGON_LEXICON
)
from core.breakthroughs_manager import (
    get_breakthroughs_catalog,
    sync_europepmc_breakthroughs,
    toggle_breakthrough_bookmark,
    CREATORS,
    COPYRIGHT_NOTICE
)
from core.auth_store import (
    register_student,
    authenticate_student,
    get_student_user,
    seed_default_users,
    verify_faculty_passcode,
    check_faculty_rate_limit,
    record_faculty_attempt,
    reset_faculty_rate_limit
)
from core.draft_store import (
    save_student_draft,
    get_student_draft,
    list_student_drafts,
    seed_default_drafts,
    toggle_draft_lock,
    dispatch_faculty_feedback,
    delete_student_draft
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app = Flask(
    __name__,
    static_folder=STATIC_DIR,
    template_folder=TEMPLATES_DIR,
    static_url_path="/static"
)
app.secret_key = os.environ.get("SECRET_KEY", "biowriter-studio-session-secret-2026")

# Enable WhiteNoise for zero-config production static assets (Render, Railway, Heroku)
try:
    from whitenoise import WhiteNoise
    app.wsgi_app = WhiteNoise(app.wsgi_app, root=STATIC_DIR, prefix="static/")
except Exception:
    pass

seed_default_users()
seed_default_drafts()

CONFIG_DIR = os.path.join(BASE_DIR, "config")
active_course_id = "BT_301"


def get_course_config(course_id: str = "BT_301"):
    filename_map = {
        "BT_301": "course_bt301.json",
        "GRAD_501": "course_grad501.json",
        "GRANT_STDF": "course_grant_stdf.json"
    }
    fname = filename_map.get(course_id, "course_bt301.json")
    fpath = os.path.join(CONFIG_DIR, fname)
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"course_id": "BT_301", "course_name": "BT_301: Introduction to Biotechnology"}


@app.route("/")
def index():
    config = get_course_config("BT_301")
    return render_template("index.html", config=config, active_course="BT_301")


@app.route("/faculty")
def faculty_view():
    config = get_course_config("BT_301")
    # If student is logged in, strictly deny access
    if session.get("role") == "student" or session.get("student_id"):
        return render_template("faculty.html", config=config, active_course="BT_301", access_denied=True, student_id=session.get("student_id")), 403
    
    is_auth = bool(session.get("faculty_authenticated"))
    return render_template("faculty.html", config=config, active_course="BT_301", access_denied=False, is_authenticated=is_auth)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(STATIC_DIR, "favicon.ico")


@app.route("/static/<path:filename>")
def custom_static_handler(filename):
    """Explicit fallback static handler ensuring 200 OK regardless of web server quirks."""
    return send_from_directory(STATIC_DIR, filename)


@app.route("/studio.css")
def serve_root_css():
    """Fail-safe direct CSS route bypassing any proxy or web-server /static/ interceptors."""
    return send_from_directory(os.path.join(STATIC_DIR, "css"), "studio.css", mimetype="text/css")


@app.route("/studio.js")
def serve_root_js():
    """Fail-safe direct JS route bypassing any proxy or web-server /static/ interceptors."""
    return send_from_directory(os.path.join(STATIC_DIR, "js"), "studio.js", mimetype="application/javascript")


@app.route("/api/writing/audit_all", methods=["POST"])
def api_audit_all_writing():
    data = request.get_json() or {}
    return jsonify(audit_all_writing_sections(data))



@app.route("/api/config", methods=["GET"])
def api_get_config():
    global active_course_id
    return jsonify(get_course_config(active_course_id))


@app.route("/api/courses", methods=["GET"])
def api_list_courses():
    courses = [
        {"id": "BT_301", "name": "BT_301: Introduction to Biotechnology (Research Proposals)"},
        {"id": "GRAD_501", "name": "GRAD_501: Senior Graduation Project & Capstone Thesis"},
        {"id": "GRANT_STDF", "name": "GRANT_STDF: National & International Grant Standard (STDF/ICGEB)"}
    ]
    return jsonify({"courses": courses, "active": active_course_id})


@app.route("/api/courses/switch", methods=["POST"])
def api_switch_course():
    global active_course_id
    data = request.get_json() or {}
    cid = data.get("course_id", "BT_301")
    if cid in ["BT_301", "GRAD_501", "GRANT_STDF"]:
        active_course_id = cid
        return jsonify({"success": True, "course": get_course_config(active_course_id)})
    return jsonify({"success": False, "error": "Unknown course ID"}), 400


@app.route("/api/search/build", methods=["POST"])
def api_build_search():
    data = request.get_json() or {}
    system = data.get("chassis") or data.get("system", "")
    tool = data.get("tool", "")
    target = data.get("target", "")
    synonyms = data.get("synonyms", {})
    result = build_boolean_query(system, tool, target, synonyms)
    return jsonify(result)


@app.route("/api/search/examples", methods=["GET"])
def api_search_examples():
    return jsonify(get_curated_examples())


@app.route("/api/paraphrase/check", methods=["POST"])
def api_check_paraphrase():
    data = request.get_json() or {}
    original = data.get("original", "")
    draft = data.get("draft", "")
    result = audit_paraphrase_rhev(original, draft)
    return jsonify(result)


@app.route("/api/reference/lookup", methods=["POST"])
def api_lookup_reference():
    data = request.get_json() or {}
    doi = data.get("doi", "")
    result = fetch_doi_metadata(doi)
    return jsonify(result)


@app.route("/api/reference/audit_recency", methods=["POST"])
def api_audit_recency():
    data = request.get_json() or {}
    refs = data.get("references", "")
    result = audit_bibliography_recency(refs)
    return jsonify(result)


@app.route("/api/starters", methods=["GET"])
def api_get_starters():
    return jsonify(get_sentence_starters())


@app.route("/api/socratic/critique", methods=["POST"])
def api_socratic_critique():
    data = request.get_json() or {}
    section = data.get("section", "Draft")
    text = data.get("text", "")
    context = data.get("context", {})
    result = analyze_student_draft(section, text, context)
    return jsonify(result)


@app.route("/api/audit/full", methods=["POST"])
def api_audit_full():
    data = request.get_json() or {}
    result = calculate_full_rubric_audit(data)
    return jsonify(result)


@app.route("/api/viva/generate", methods=["POST"])
def api_generate_viva():
    data = request.get_json() or {}
    questions = generate_viva_defense_questions(data)
    return jsonify({"questions": questions})


@app.route("/api/instructor/comments", methods=["GET"])
def api_get_instructor_comments():
    return jsonify(get_rapid_comment_bank())


@app.route("/api/instructor/report", methods=["POST"])
@app.route("/api/instructor/compile_memo", methods=["POST"])
def api_create_instructor_report():
    data = request.get_json() or {}
    student_data = data.get("student_data", {})
    codes = data.get("codes") or data.get("selected_codes") or []
    manual = data.get("manual_comments", "")
    report = compile_instructor_feedback_report(student_data, codes, manual)
    return jsonify(report)


# ==========================================================================
# Student Authentication & Session Routes
# ==========================================================================

# ==========================================================================
# Faculty Authentication Routes
# ==========================================================================
def _get_client_ip() -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"


@app.route("/api/faculty/login", methods=["POST"])
def api_faculty_login():
    client_ip = _get_client_ip()

    # 1. Check anti-brute-force rate limiter & lockout
    allowed, lock_msg, remaining_sec = check_faculty_rate_limit(client_ip)
    if not allowed:
        return jsonify({
            "success": False,
            "error": lock_msg,
            "locked": True,
            "remaining_seconds": remaining_sec
        }), 429

    data = request.get_json() or {}
    passcode = data.get("passcode") or data.get("password", "")

    # 2. Cryptographically verify passcode against PBKDF2 salted hashes
    if verify_faculty_passcode(passcode):
        record_faculty_attempt(client_ip, success=True)
        # Clear student session if one was active
        session.pop("student_id", None)
        session.pop("student_name", None)
        session["faculty_authenticated"] = True
        session["role"] = "faculty"
        session["faculty_name"] = "Course Instructor & Review Chair"
        return jsonify({"success": True, "message": "Faculty access verified.", "redirect": "/faculty"})

    # Failed attempt: record and apply 1.0s artificial throttle
    import time
    time.sleep(1.0)
    att_res = record_faculty_attempt(client_ip, success=False)
    status_code = 429 if att_res.get("locked") else 401
    return jsonify({
        "success": False,
        "error": att_res.get("message", "Invalid instructor access passcode."),
        "locked": att_res.get("locked", False),
        "attempts": att_res.get("attempts", 1),
        "remaining_tries": att_res.get("remaining_tries", 0)
    }), status_code


@app.route("/api/faculty/logout", methods=["POST"])
def api_faculty_logout():
    session.pop("faculty_authenticated", None)
    if session.get("role") == "faculty":
        session.pop("role", None)
    return jsonify({"success": True, "message": "Faculty session signed out."})


@app.route("/api/faculty/me", methods=["GET"])
def api_faculty_me():
    is_auth = bool(session.get("faculty_authenticated"))
    is_student = session.get("role") == "student"
    return jsonify({
        "authenticated": is_auth,
        "is_student": is_student,
        "student_id": session.get("student_id") if is_student else None
    })

@app.route("/api/auth/register", methods=["POST"])
def api_auth_register():
    data = request.get_json() or {}
    sid = data.get("student_id", "").strip()
    name = data.get("student_name", "").strip()
    pwd = data.get("password", "")
    result = register_student(sid, name, pwd)
    if result.get("success"):
        session["student_id"] = result["user"]["student_id"]
        session["student_name"] = result["user"]["student_name"]
        session["role"] = "student"
        draft = get_student_draft(result["user"]["student_id"])
        result["draft"] = sanitize_draft_for_student(draft) if draft else None
    return jsonify(result), (200 if result.get("success") else 400)


def sanitize_draft_for_student(draft_dict):
    """Enforces strict pedagogical No-Grades policy for students:
    strips numeric GPA and raw score fields, keeping qualitative review status,
    action items, and feedback memo intact."""
    if not draft_dict or not isinstance(draft_dict, dict):
        return draft_dict
    sanitized = json.loads(json.dumps(draft_dict))
    if "faculty_review" in sanitized and isinstance(sanitized["faculty_review"], dict):
        rev = sanitized["faculty_review"]
        rev.pop("gpa", None)
        rev.pop("raw_total", None)
        if "criterion_overrides" in rev and isinstance(rev["criterion_overrides"], dict):
            clean_overrides = {}
            for k, v in rev["criterion_overrides"].items():
                if isinstance(v, dict):
                    clean_overrides[k] = {"notes": v.get("notes", "")}
                else:
                    clean_overrides[k] = {"notes": str(v)}
            rev["criterion_overrides"] = clean_overrides
        sanitized["faculty_review"] = rev
    return sanitized


@app.route("/api/auth/login", methods=["POST"])
def api_auth_login():
    data = request.get_json() or {}
    sid = data.get("student_id", "").strip()
    pwd = data.get("password", "")
    result = authenticate_student(sid, pwd)
    if result.get("success"):
        session["student_id"] = result["user"]["student_id"]
        session["student_name"] = result["user"]["student_name"]
        session["role"] = "student"
        draft = get_student_draft(result["user"]["student_id"])
        result["draft"] = sanitize_draft_for_student(draft)
    return jsonify(result), (200 if result.get("success") else 401)


@app.route("/api/auth/logout", methods=["POST"])
def api_auth_logout():
    session.clear()
    return jsonify({"success": True, "message": "Signed out successfully."})


@app.route("/api/auth/me", methods=["GET"])
def api_auth_me():
    sid = session.get("student_id")
    if not sid:
        return jsonify({"authenticated": False})
    user = get_student_user(sid)
    if not user:
        session.clear()
        return jsonify({"authenticated": False})
    draft = get_student_draft(sid)
    return jsonify({
        "authenticated": True,
        "user": user,
        "draft": sanitize_draft_for_student(draft)
    })


@app.route("/api/student/save_draft", methods=["POST"])
def api_save_student_draft():
    data = request.get_json() or {}
    student_id = data.get("student_id", "").strip() or session.get("student_id", "")
    student_data = data.get("student_data", data)
    result = save_student_draft(student_id, student_data)
    return jsonify(result)


@app.route("/api/student/toggle_lock", methods=["POST"])
def api_student_toggle_lock():
    data = request.get_json() or {}
    student_id = data.get("student_id", "").strip() or session.get("student_id", "")
    is_locked = bool(data.get("is_locked", True))
    if not student_id:
        return jsonify({"success": False, "error": "Student ID required."}), 400
    res = toggle_draft_lock(student_id, is_locked)
    return jsonify(res)


@app.route("/api/student/drafts", methods=["GET"])
def api_list_student_drafts():
    return jsonify(list_student_drafts())


@app.route("/api/student/draft/<student_id>", methods=["GET"])
def api_get_student_draft(student_id):
    draft = get_student_draft(student_id)
    if draft:
        # If faculty is requesting, return full draft; if student is requesting, redact numeric grades
        is_faculty = bool(session.get("faculty_authenticated"))
        payload = draft if is_faculty else sanitize_draft_for_student(draft)
        return jsonify({"success": True, "draft": payload})
    return jsonify({"success": False, "error": f"Student draft '{student_id}' not found."}), 404


@app.route("/api/instructor/dispatch_feedback", methods=["POST"])
def api_instructor_dispatch_feedback():
    if not session.get("faculty_authenticated"):
        return jsonify({"success": False, "error": "Faculty authorization required to dispatch evaluation."}), 401
    
    data = request.get_json() or {}
    student_id = data.get("student_id", "").strip()
    if not student_id:
        return jsonify({"success": False, "error": "Student ID required."}), 400

    payload = data.get("feedback") if isinstance(data.get("feedback"), dict) else data
    feedback = {
        "instructor_name": payload.get("instructor_name", "BT_301 Faculty Evaluation Board"),
        "gpa": payload.get("gpa", 0.0),
        "raw_total": payload.get("raw_total", 0.0),
        "standing": payload.get("standing", "Evaluated"),
        "criterion_overrides": payload.get("criterion_overrides", {}),
        "manual_notes": payload.get("manual_notes", ""),
        "action_items": payload.get("action_items", []),
        "memo_text": payload.get("memo_text", "")
    }

    result = dispatch_faculty_feedback(student_id, feedback)
    return jsonify(result)


@app.route("/api/faculty/submission/<student_id>", methods=["DELETE", "POST"])
def api_faculty_delete_submission(student_id):
    """Deletes a student proposal submission. Requires faculty authorization."""
    if not session.get("faculty_authenticated") or session.get("role") != "faculty":
        return jsonify({"success": False, "error": "Faculty authorization required to remove submissions."}), 403

    clean_id = (student_id or "").strip()
    if not clean_id:
        return jsonify({"success": False, "error": "Student ID is required."}), 400

    result = delete_student_draft(clean_id)
    status_code = 200 if result.get("success") else 404
    return jsonify(result), status_code


@app.route("/api/export/docx", methods=["POST"])
def api_export_docx():
    data = request.get_json() or {}
    audit_results = calculate_full_rubric_audit(data)
    doc_io = generate_docx_portfolio(data, audit_results)
    
    filename = f"Proposal_Portfolio_{data.get('student_name', 'Student').replace(' ', '_')}.docx"
    return send_file(
        doc_io,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@app.route("/api/export/pptx", methods=["POST"])
def api_export_pptx():
    data = request.get_json() or {}
    audit_results = calculate_full_rubric_audit(data)
    pptx_io = create_defense_presentation(data, audit_results)
    
    filename = f"Oral_Defense_Slides_{data.get('student_name', 'Student').replace(' ', '_')}.pptx"
    return send_file(
        pptx_io,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )


@app.route("/api/export/md", methods=["POST"])
def api_export_md():
    data = request.get_json() or {}
    audit_results = calculate_full_rubric_audit(data)
    md_content = generate_markdown_portfolio(data, audit_results)
    
    filename = f"Proposal_Portfolio_{data.get('student_name', 'Student').replace(' ', '_')}.md"
    from io import BytesIO
    buf = BytesIO(md_content.encode("utf-8"))
    return send_file(
        buf,
        as_attachment=True,
        download_name=filename,
        mimetype="text/markdown"
    )


# -------------------------------------------------------------
# Impact, Novelty, Gap & Competitor API Endpoints
# -------------------------------------------------------------

@app.route("/api/impact/gap_taxonomy", methods=["GET"])
def api_get_gap_taxonomy():
    return jsonify(GAP_TAXONOMY)


@app.route("/api/impact/gap_audit", methods=["POST"])
def api_audit_gap():
    data = request.get_json() or {}
    gap_text = data.get("gap_text", "")
    gap_type = data.get("gap_type", "")
    return jsonify(audit_gap_statement(gap_text, selected_gap_type=gap_type))


@app.route("/api/impact/novelty_audit", methods=["POST"])
def api_audit_novelty():
    data = request.get_json() or {}
    return jsonify(audit_novelty_and_soundness(
        title=data.get("title", ""),
        chassis=data.get("chassis", "") or data.get("system", ""),
        tool=data.get("tool", ""),
        target=data.get("target", ""),
        hypothesis=data.get("hypothesis", ""),
        methodology=data.get("methodology", "")
    ))


@app.route("/api/impact/significance_search", methods=["POST"])
def api_significance_search():
    data = request.get_json() or {}
    return jsonify(build_significance_search_queries(
        chassis=data.get("chassis", "") or data.get("system", ""),
        tool=data.get("tool", ""),
        target=data.get("target", ""),
        project_modality=data.get("modality", "cellular")
    ))


@app.route("/api/impact/competitor_audit", methods=["POST"])
def api_audit_competitor():
    data = request.get_json() or {}
    return jsonify(audit_competitor_matrix_and_usp(
        competitor_data=data.get("competitor_data", {}),
        usp_text=data.get("usp_text", "")
    ))


@app.route("/api/impact/chain_check", methods=["POST"])
def api_check_logic_chain():
    data = request.get_json() or {}
    return jsonify(evaluate_proposal_logic_chain(data))


@app.route("/api/paper/samples", methods=["GET"])
def api_get_paper_samples():
    return jsonify(SAMPLE_PAPERS)


@app.route("/api/paper/fetch", methods=["POST"])
def api_fetch_paper():
    data = request.get_json() or {}
    identifier = data.get("identifier", "").strip()
    return jsonify(fetch_paper_abstract_and_meta(identifier))


@app.route("/api/paper/summarize", methods=["POST"])
def api_summarize_paper():
    data = request.get_json() or {}
    text = data.get("text", "")
    title = data.get("title", "")
    identifier = data.get("identifier", "")
    authors = data.get("authors", "")
    year = data.get("year")
    journal = data.get("journal", "")
    return jsonify(deconstruct_paper(
        text=text,
        title=title,
        identifier=identifier,
        authors=authors,
        year=year,
        journal=journal
    ))


@app.route("/api/breakthroughs", methods=["GET"])
def api_get_breakthroughs():
    category = request.args.get("category", "All")
    storage_filter = request.args.get("storage_filter", "all")
    search_query = request.args.get("q", "")
    data = get_breakthroughs_catalog(
        category=category,
        storage_filter=storage_filter,
        search_query=search_query
    )
    return jsonify({
        "status": "success",
        "creators": CREATORS,
        "copyright": COPYRIGHT_NOTICE,
        **data
    })


@app.route("/api/breakthroughs/sync", methods=["POST"])
def api_sync_breakthroughs():
    data = request.get_json() or {}
    topic = data.get("topic", "").strip()
    result = sync_europepmc_breakthroughs(custom_topic=topic)
    return jsonify({
        "status": "success",
        "creators": CREATORS,
        "copyright": COPYRIGHT_NOTICE,
        **result
    })


@app.route("/api/breakthroughs/bookmark", methods=["POST"])
def api_bookmark_breakthrough():
    data = request.get_json() or {}
    item_id = data.get("id", "").strip()
    if not item_id:
        return jsonify({"status": "error", "message": "Item ID is required"}), 400
    res = toggle_breakthrough_bookmark(item_id)
    return jsonify({
        "status": "success",
        **res
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
    print(f"===============================================================")
    print(f"[*] BioWriter Studio (Full Suite) running on:")
    print(f"    http://{host}:{port}")
    print(f"===============================================================")
    app.run(host=host, port=port, debug=False if os.environ.get("PORT") else True)
