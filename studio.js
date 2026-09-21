/**
 * BioWriter Studio: Comprehensive Client Controller
 * Course: BT_301 & Multi-Course Research Management
 */

const STORAGE_KEY = "bt301_biowriter_state_v4";
let currentStep = 1;
let selectedCommentCodes = new Set();

function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

let projectModels = {
  cellular: {
    name: "Cellular / Host Organism (Microbial, Yeast, Plant, Mammalian)",
    desc: "For projects expressing recombinant enzymes, pathways, or traits inside living cell lines or host organisms.",
    p1: { label: "1. Biological Host / Chassis Organism", placeholder: "e.g. Pseudomonas putida or Triticum aestivum", examples: "Pseudomonas putida, Pichia pastoris, E. coli, CHO cells" },
    p2: { label: "2. Molecular Tool / Engineered Enzyme / Gene", placeholder: "e.g. Engineered PETase or TaHKT1;5 transporter", examples: "PETase, Cas12a, endoglucanase, base editor" },
    p3: { label: "3. Target Phenomenon / Quantitative Outcome", placeholder: "e.g. Accelerated PET depolymerization", examples: "depolymerization rate, foliar salt exclusion" }
  },
  cell_free: {
    name: "In Vitro / Cell-Free Diagnostic / Biosensor (No Living Host)",
    desc: "For paper dipsticks, lateral flow assays, CRISPR diagnostics, or cell-free lysate reactions.",
    p1: { label: "1. Diagnostic System / Test Matrix / Specimen", placeholder: "e.g. Paper lateral flow strip or hospital wastewater effluent", examples: "paper lateral flow strip, lyophilized cell-free lysate, blood serum, hospital effluent" },
    p2: { label: "2. Recognition Element / Molecular Probe / Mechanism", placeholder: "e.g. CRISPR-Cas12a fluorescent reporter", examples: "Cas12a-crRNA, DNA aptamer, gold nanoparticle probe, RPA amplification" },
    p3: { label: "3. Target Biomarker / Limit of Detection (LOD)", placeholder: "e.g. mcr-1 colistin resistance gene, femtomolar LOD", examples: "mcr-1 gene, circulating microRNA, femtomolar analytical sensitivity" }
  },
  nanotech: {
    name: "Biomaterials / Nanotechnology / Drug Delivery Formulations",
    desc: "For nanoparticles, hydrogels, liposomes, and targeted therapeutic delivery vehicles.",
    p1: { label: "1. Carrier Material / Nanomaterial Matrix / Vehicle", placeholder: "e.g. Lipid nanoparticles (LNPs) or chitosan-PLGA scaffold", examples: "lipid nanoparticles (LNPs), chitosan hydrogel, mesoporous silica, PLGA" },
    p2: { label: "2. Bioactive Cargo / Functional Ligand / Release Trigger", placeholder: "e.g. siRNA cargo or pH-responsive cleavage mechanism", examples: "siRNA, CRISPR ribonucleoprotein, transferrin targeting peptide" },
    p3: { label: "3. Pathological Target / Pharmacodynamic Threshold", placeholder: "e.g. Triple-negative breast cancer oncogene silencing", examples: "intracellular delivery >80%, IC50 reduction, tumor clearance" }
  },
  environmental: {
    name: "Environmental Biotechnology / Bioremediation Matrix",
    desc: "For contaminated soils, wastewater effluents, bioreactor matrices, or immobilized biocatalysts.",
    p1: { label: "1. Contaminated Matrix / Bioreactor System", placeholder: "e.g. Membrane bioreactor effluent or industrial textile wastewater", examples: "industrial wastewater, saline agricultural drainage, contaminated soil" },
    p2: { label: "2. Biocatalytic Consortium / Immobilized Agent", placeholder: "e.g. Cross-linked laccase aggregates (CLEAs)", examples: "CLEAs, bacterial biofilm, immobilized peroxidase, biochar composite" },
    p3: { label: "3. Target Contaminant / Clearance Threshold", placeholder: "e.g. Pharmaceutical micropollutant clearance >90%", examples: "azo dye decolorization >95%, heavy metal reduction <0.1 mg/L" }
  },
  computational: {
    name: "Computational Biology / In Silico Modeling Pipeline",
    desc: "For structural bioinformatics, docking screens, AI protein redesign, or molecular dynamics.",
    p1: { label: "1. Computational Model / Macromolecular Target", placeholder: "e.g. AlphaFold predicted catalytic cleft or PDB 6EQE", examples: "AlphaFold coordinate model, PDB structure, molecular dynamics ensemble" },
    p2: { label: "2. In Silico Algorithm / Mutagenesis Strategy", placeholder: "e.g. Rosetta flex ddG free-energy profiling", examples: "Rosetta design, QM/MM simulation, virtual screening pipeline" },
    p3: { label: "3. Biophysical Metric / Predictive Benchmark", placeholder: "e.g. Binding affinity delta-G < -10 kcal/mol", examples: "binding affinity delta-G, catalytic transition state energy barrier" }
  },
  custom: {
    name: "Custom Interdisciplinary Modality",
    desc: "For hybrid, synthetic biology, or custom cross-cutting projects (e.g. Clinical Microbiome, Gut-Brain Axis, Synthetic Consortia).",
    p1: { label: "1. Experimental System / Model / Specimen", placeholder: "e.g. Clinical specimen, bioreactor matrix, animal model, or cell model", examples: "gut microbiome, hospital effluent, organoid culture, transgenic mouse" },
    p2: { label: "2. Molecular Tool / Engineered Intervention", placeholder: "e.g. Engineered synbiotic consortium, CRISPR tool, or delivery vehicle", examples: "Lactobacillus chassis, synthetic circuit, nanoparticle probe" },
    p3: { label: "3. Target Phenomenon / Quantitative Outcome", placeholder: "e.g. Targeted symptom alleviation, high-efficiency clearance, biomarker shift", examples: "calibrated biomarker threshold, >80% clearance, symptom score" }
  }
};

let currentDecodedData = null;

let projectState = {
  student_name: "",
  student_id: "",
  model_id: "cellular",
  custom_modality: "",
  keywords: "",
  title: "",
  system: "",
  chassis: "",
  tool: "",
  target: "",
  search_query: "",
  matrix: {
    yellow: "",
    blue: "",
    green: "",
    purple: "",
    red: "",
    citation: ""
  },
  decoded_paper_cache: null,
  abstract: "",
  funnel: {
    tier1: "",
    tier2: "",
    tier3: "",
    tier4: ""
  },
  overarching_aim: "",
  aims: {
    aim1: "",
    aim1_title: "",
    aim2: "",
    aim2_title: "",
    aim3: "",
    aim3_title: ""
  },
  methodology: "",
  expected_outcomes: "",
  impact: "",
  customer: "",
  market: "",
  usps: "",
  competitor_data: {
    // Exact 9 Dimensions
    principle_established: "",
    principle_recent: "",
    principle_proposed: "",
    strength_established: "",
    strength_recent: "",
    strength_proposed: "",
    limitation_established: "",
    limitation_recent: "",
    limitation_proposed: "",
    performance_established: "",
    performance_recent: "",
    performance_proposed: "",
    cost_established: "",
    cost_recent: "",
    cost_proposed: "",
    safety_established: "",
    safety_recent: "",
    safety_proposed: "",
    evidence_established: "",
    evidence_recent: "",
    evidence_proposed: "",
    gap_established: "",
    gap_recent: "",
    gap_proposed: "",
    contribution_proposed: "",
    // Legacy field compatibility
    incumbent_name: "",
    incumbent_speed: "",
    incumbent_cost: "",
    incumbent_metric: "",
    incumbent_portability: "",
    incumbent_safety: "",
    emerging_name: "",
    emerging_speed: "",
    emerging_cost: "",
    emerging_metric: "",
    emerging_portability: "",
    emerging_safety: "",
    proposed_name: "",
    proposed_speed: "",
    proposed_cost: "",
    proposed_metric: "",
    proposed_portability: "",
    proposed_safety: ""
  },
  gantt_schedule: {
    total_months: 18,
    wp1_start: 1,
    wp1_end: 6,
    wp1_gate: "",
    wp2_start: 5,
    wp2_end: 12,
    wp2_gate: "",
    wp3_start: 10,
    wp3_end: 18,
    wp3_gate: "",
    tasks: []
  },
  budget_items: {
    consumables: 18500,
    personnel: 12000,
    utilities: 4500,
    equipment: 15000
  },
  budget_materials: [],
  swot: {
    strengths: "",
    weaknesses: "",
    opportunities: "",
    threats: ""
  },
  pestel: {
    political: "",
    economic: "",
    social: "",
    technological: "",
    environmental: "",
    legal: ""
  },
  time_plan: "",
  budget: "",
  references: "",
  aims_contingencies: {
    aim1_fallback: "",
    aim2_fallback: "",
    aim3_fallback: ""
  },
  control_triad: {
    negative: "",
    positive: "",
    specificity: ""
  },
  biotech_risk_matrix: {
    off_target: "",
    toxicity: "",
    solubility: "",
    biosafety: ""
  },
  is_locked_for_grading: false,
  faculty_review: null
};

document.addEventListener("DOMContentLoaded", () => {
  loadFromStorage();
  initStepperNavigation();
  initModelSelector();
  initCourseSwitcher();
  initFormBindings();
  initPresetSelector();
  initStep1Action();
  initDoiResolver();
  initRhevParaphraseLab();
  initFunnelMadLibs();
  initDiagramGenerator();
  initBudgetCalculator();
  initRefRecencyAuditor();
  initImpactAndNoveltySuite();
  initPaperDecoder();
  initLogicChainTrack();
  initAuditAndViva();
  initInstructorStudio();
  initExportHandlers();
  initVisualStudio();
  initBreakthroughsModule();
  initHeaderAndNavigationEnhancements();
  initAuthManager();
  initGovernanceAndGuidance();
  updateLiveScore();
  updateLogicChainUI();
});

function showToast(message) {
  let toast = document.getElementById("toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "toast";
    document.body.appendChild(toast);
  }
  toast.innerText = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 3000);
}

function saveToStorage() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(projectState));
  const saveIndicator = document.getElementById("save-status");
  if (saveIndicator) saveIndicator.innerText = "All progress saved";
}

function loadFromStorage() {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved) {
    try {
      projectState = Object.assign(projectState, JSON.parse(saved));
    } catch (e) {
      console.error("Could not parse saved state", e);
    }
  }
  populateFormFields();
}


let serverSyncTimeout = null;
function triggerServerSyncDebounced() {
  if (serverSyncTimeout) clearTimeout(serverSyncTimeout);
  serverSyncTimeout = setTimeout(() => {
    if (projectState.student_id && projectState.student_id.trim()) {
      syncDraftToServer(false);
    }
  }, 3000);
}

async function syncDraftToServer(showNotification = true) {
  const sid = (projectState.student_id || "").trim();
  if (!sid) {
    if (showNotification) showToast("Please enter a Student ID / Team Code first.", "warning");
    const idEl = document.getElementById("student-id-input");
    if (idEl) idEl.focus();
    return;
  }
  try {
    const resp = await fetch("/api/student/save_draft", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        student_id: sid,
        student_data: projectState
      })
    });
    const res = await resp.json();
    if (res.success) {
      if (showNotification) {
        showToast(`✅ Proposal draft synced to server under ID ${res.student_id} (${res.updated_at})!`);
      }
      const stEl = document.querySelector(".save-status-text");
      if (stEl) stEl.innerText = `Synced to Server (${res.updated_at})`;
    }
  } catch (e) {
    console.error("Draft sync error:", e);
    if (showNotification) showToast("Network error syncing draft to server.");
  }
}

function updateMatrixExplainer(data) {
  if (!data) return;
  const explainerPanel = document.getElementById("matrix-paper-explainer-panel");
  if (!explainerPanel) return;

  // 1. Paper Title & Meta
  const elTitle = document.getElementById("matrix-exp-title");
  const elAuthors = document.getElementById("matrix-exp-authors");
  const elJournal = document.getElementById("matrix-exp-journal");
  const elYear = document.getElementById("matrix-exp-year");
  const elRecency = document.getElementById("matrix-exp-recency");

  if (elTitle) elTitle.textContent = data.title || "Primary Research Paper";
  if (elAuthors) elAuthors.textContent = "👥 " + (data.authors || "Authors");
  if (elJournal) elJournal.textContent = "🏛️ " + (data.journal || "Journal");
  if (elYear) elYear.textContent = "📅 " + (data.year || "Year n.d.");

  if (elRecency) {
    const yr = parseInt(data.year, 10);
    if (!isNaN(yr) && yr >= 2021) {
      elRecency.textContent = "✅ 2021–2026 Recency Verified";
      elRecency.style.background = "#dcfce7";
      elRecency.style.color = "#166534";
    } else {
      elRecency.textContent = "ℹ️ Benchmark Baseline Reference";
      elRecency.style.background = "#eff6ff";
      elRecency.style.color = "#1e40af";
    }
  }

  // 2. Everyday Analogy & Theme
  const elTheme = document.getElementById("matrix-exp-theme");
  const elAnalogy = document.getElementById("matrix-exp-analogy");
  if (data.plain_english_explanation) {
    if (elTheme) elTheme.textContent = data.plain_english_explanation.theme || "Biotechnology & Molecular Engineering";
    if (elAnalogy) elAnalogy.textContent = data.plain_english_explanation.core_analogy || "";
  }

  // 3. 4-Pillar Plain English Story Breakdown
  const elProblem = document.getElementById("matrix-exp-problem");
  const elSolution = document.getElementById("matrix-exp-solution");
  const elFinding = document.getElementById("matrix-exp-finding");
  const elGap = document.getElementById("matrix-exp-gap");

  if (data.plain_english_explanation) {
    if (elProblem) elProblem.textContent = data.plain_english_explanation.simple_problem || (data.executive_summary && data.executive_summary.problem) || "";
    if (elSolution) elSolution.textContent = data.plain_english_explanation.simple_solution || (data.executive_summary && data.executive_summary.intervention) || "";
    if (elFinding) elFinding.textContent = data.plain_english_explanation.simple_takeaway || (data.executive_summary && data.executive_summary.main_finding) || "";
    if (elGap) elGap.textContent = data.plain_english_explanation.simple_limitation || (data.executive_summary && data.executive_summary.limitation) || "";
  }

  // 4. Benchmark Metrics Chips
  const chipsContainer = document.getElementById("matrix-exp-metrics-chips");
  if (chipsContainer) {
    const metrics = (data.extracted_parameters && data.extracted_parameters.metric_numbers) || [];
    if (metrics.length > 0) {
      chipsContainer.innerHTML = metrics.map(m => `<span class="matrix-metric-chip">⚡ ${escapeHtml(m)}</span>`).join("");
    } else if (data.extracted_parameters && data.extracted_parameters.primary_metric_sentence) {
      chipsContainer.innerHTML = `<span class="matrix-metric-chip">⚡ ${escapeHtml(data.extracted_parameters.primary_metric_sentence.slice(0, 48))}...</span>`;
    } else {
      chipsContainer.innerHTML = `<span class="matrix-metric-chip" style="background:#f1f5f9; color:#475569;">Quantitative baseline recorded</span>`;
    }
  }

  // 5. 6 Dedicated Parameter Insight Boxes
  const pExp = data.parameter_explanations || {};
  const setInsight = (boxId, bodyId, text) => {
    const box = document.getElementById(boxId);
    const body = document.getElementById(bodyId);
    if (body && text) {
      body.textContent = text;
      if (box) {
        box.classList.add("has-content");
        box.style.display = "block";
      }
    }
  };

  setInsight("matrix-insight-yellow", "matrix-insight-yellow-body", pExp.burden_explanation);
  setInsight("matrix-insight-blue", "matrix-insight-blue-body", pExp.benchmark_explanation);
  setInsight("matrix-insight-green", "matrix-insight-green-body", pExp.gap_explanation);
  setInsight("matrix-insight-purple", "matrix-insight-purple-body", pExp.controls_explanation);
  setInsight("matrix-insight-red", "matrix-insight-red-body", pExp.milestone_explanation);
  setInsight("matrix-insight-citation", "matrix-insight-citation-body", pExp.citation_explanation);

  explainerPanel.style.display = "block";
}

function applyDecodedDataToMatrix(data) {
  if (!data || !data.extracted_parameters) return;
  const p = data.extracted_parameters;

  // 1. Parameter 1: Epidemiological / Global Burden Statistic
  if (p.burden_statistic) {
    projectState.matrix.yellow = p.burden_statistic;
    const el = document.getElementById("matrix-yellow");
    if (el) el.value = p.burden_statistic;
  }
  // 2. Parameter 2: Scientific Benchmark & Baseline Rate
  if (p.primary_metric_sentence) {
    projectState.matrix.blue = p.primary_metric_sentence;
    const el = document.getElementById("matrix-blue");
    if (el) el.value = p.primary_metric_sentence;
  }
  // 3. Parameter 3: Mechanistic Knowledge Gap / Flaw
  if (p.stated_gap) {
    projectState.matrix.green = p.stated_gap;
    const el = document.getElementById("matrix-green");
    if (el) el.value = p.stated_gap;
  }
  // 4. Parameter 4: Experimental Strategy, Model System & Verification Controls
  const ctrlVal = p.experimental_strategy || p.controls;
  if (ctrlVal) {
    projectState.matrix.purple = ctrlVal;
    const el = document.getElementById("matrix-purple");
    if (el) el.value = ctrlVal;
  }
  // 5. Parameter 5: Core Engineered Innovation & Molecular Mechanism
  const innovVal = p.key_innovation || p.target_milestone;
  if (innovVal) {
    projectState.matrix.red = innovVal;
    const el = document.getElementById("matrix-red");
    if (el) el.value = innovVal;
  }
  // 6. Parameter 6: Key Measured Findings, Evidence Proof & Calibrated Milestone
  const findingsVal = p.research_horizon || p.key_findings || (data.citations && data.citations.apa ? data.citations.apa : "");
  if (findingsVal) {
    projectState.matrix.citation = findingsVal;
    const el = document.getElementById("matrix-citation");
    if (el) el.value = findingsVal;
  }

  currentDecodedData = data;
  projectState.decoded_paper_cache = data;
  saveToStorage();
  if (typeof updateLogicChainUIDebounced === "function") updateLogicChainUIDebounced();
  if (typeof updateLiveScoreDebounced === "function") updateLiveScoreDebounced();

  updateMatrixExplainer(data);
}

function renderKeywordTags(keywords) {
  const container = document.getElementById("keywords-tags-container");
  if (!container) return;
  if (!keywords || !keywords.trim()) {
    container.innerHTML = '<span style="font-size:0.75rem; color:#94a3b8; font-style:italic;">No custom keywords typed yet.</span>';
    return;
  }
  const tags = keywords.split(",").map(t => t.trim()).filter(Boolean);
  container.innerHTML = tags.map(t => `<span style="background:#e0e7ff; color:#3730a3; padding:2px 8px; border-radius:999px; font-size:0.75rem; font-weight:600;">🏷️ ${escapeHtml(t)}</span>`).join(" ");
}

const GANTT_PALETTE = [
  { bar: "linear-gradient(90deg, #3b82f6, #60a5fa)", text: "#1e40af" },
  { bar: "linear-gradient(90deg, #10b981, #34d399)", text: "#065f46" },
  { bar: "linear-gradient(90deg, #f59e0b, #fbbf24)", text: "#92400e" },
  { bar: "linear-gradient(90deg, #8b5cf6, #a78bfa)", text: "#6d28d9" },
  { bar: "linear-gradient(90deg, #ec4899, #f472b6)", text: "#be185d" },
  { bar: "linear-gradient(90deg, #06b6d4, #22d3ee)", text: "#0e7490" },
  { bar: "linear-gradient(90deg, #6366f1, #818cf8)", text: "#3730a3" }
];

function ensureGanttTasks() {
  if (!projectState.gantt_schedule) projectState.gantt_schedule = {};
  const gs = projectState.gantt_schedule;
  const totM = Math.max(3, Math.min(60, parseInt(gs.total_months, 10) || 18));
  if (!Array.isArray(gs.tasks) || gs.tasks.length === 0) {
    const a = projectState.aims || {};
    gs.tasks = [
      {
        name: a.aim1_title ? `WP1: ${a.aim1_title}` : "WP1: Construction & Preparation",
        start: parseInt(gs.wp1_start, 10) || 1,
        end: parseInt(gs.wp1_end, 10) || Math.max(2, Math.round(totM * 0.33)),
        gate: gs.wp1_gate || "Sequence verified & vector expression confirmed"
      },
      {
        name: a.aim2_title ? `WP2: ${a.aim2_title}` : "WP2: Functional Testing & Evaluation",
        start: parseInt(gs.wp2_start, 10) || Math.max(2, Math.round(totM * 0.28)),
        end: parseInt(gs.wp2_end, 10) || Math.max(3, Math.round(totM * 0.67)),
        gate: gs.wp2_gate || "Quantitative activity & kinetic threshold achieved"
      },
      {
        name: a.aim3_title ? `WP3: ${a.aim3_title}` : "WP3: Real-World Validation & Performance",
        start: parseInt(gs.wp3_start, 10) || Math.max(3, Math.round(totM * 0.55)),
        end: parseInt(gs.wp3_end, 10) || totM,
        gate: gs.wp3_gate || "Target milestone validated in realistic operational matrix"
      }
    ];
  }
}

function syncGanttLegacyProperties() {
  if (!projectState.gantt_schedule) projectState.gantt_schedule = {};
  const gs = projectState.gantt_schedule;
  ensureGanttTasks();
  const tasks = gs.tasks || [];
  if (tasks[0]) {
    gs.wp1_start = parseInt(tasks[0].start, 10) || 1;
    gs.wp1_end = parseInt(tasks[0].end, 10) || 6;
    gs.wp1_gate = tasks[0].gate || "";
  }
  if (tasks[1]) {
    gs.wp2_start = parseInt(tasks[1].start, 10) || 5;
    gs.wp2_end = parseInt(tasks[1].end, 10) || 12;
    gs.wp2_gate = tasks[1].gate || "";
  }
  if (tasks[2]) {
    gs.wp3_start = parseInt(tasks[2].start, 10) || 10;
    gs.wp3_end = parseInt(tasks[2].end, 10) || (parseInt(gs.total_months, 10) || 18);
    gs.wp3_gate = tasks[2].gate || "";
  }
  const setV = (id, v) => { const el = document.getElementById(id); if (el) el.value = v; };
  setV("gantt-wp1-start", gs.wp1_start);
  setV("gantt-wp1-end", gs.wp1_end);
  setV("gantt-wp1-gate", gs.wp1_gate);
  setV("gantt-wp2-start", gs.wp2_start);
  setV("gantt-wp2-end", gs.wp2_end);
  setV("gantt-wp2-gate", gs.wp2_gate);
  setV("gantt-wp3-start", gs.wp3_start);
  setV("gantt-wp3-end", gs.wp3_end);
  setV("gantt-wp3-gate", gs.wp3_gate);
}

function updateGanttAimLabels() {
  const a = projectState.aims || {};
  const l1 = document.getElementById("gantt-wp1-label");
  const l2 = document.getElementById("gantt-wp2-label");
  const l3 = document.getElementById("gantt-wp3-label");
  if (l1) l1.textContent = a.aim1_title ? `WP1: ${a.aim1_title}` : "WP1: Construction & Preparation";
  if (l2) l2.textContent = a.aim2_title ? `WP2: ${a.aim2_title}` : "WP2: Functional Testing & Evaluation";
  if (l3) l3.textContent = a.aim3_title ? `WP3: ${a.aim3_title}` : "WP3: Real-World Validation & Trials";
}

function renderGanttTasksTable() {
  const tbody = document.getElementById("gantt-tasks-tbody");
  if (!tbody) return;
  ensureGanttTasks();
  const gs = projectState.gantt_schedule;
  const totM = Math.max(3, Math.min(60, parseInt(gs.total_months, 10) || 18));
  const tasks = gs.tasks || [];

  if (tasks.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:#64748b; padding:12px;">No milestone points configured. Click <strong>+ Add Timeline Milestone / Phase</strong> above to add one.</td></tr>`;
    return;
  }

  tbody.innerHTML = tasks.map((t, idx) => {
    const s = Math.max(1, Math.min(totM, parseInt(t.start, 10) || 1));
    const e = Math.max(s, Math.min(totM, parseInt(t.end, 10) || totM));
    const dur = e - s + 1;
    return `
      <tr data-task-idx="${idx}">
        <td>
          <input type="text" class="form-input gantt-task-name-input" data-idx="${idx}" value="${escapeHtml(t.name || '')}" placeholder="e.g. Phase ${idx+1}: Task description..." style="font-size:0.8rem; padding:4px 8px; width:100%;">
        </td>
        <td style="text-align:center;">
          <input type="number" class="form-input gantt-task-start-input" data-idx="${idx}" min="1" max="${totM}" value="${s}" style="font-size:0.8rem; padding:4px; width:52px; text-align:center;">
        </td>
        <td style="text-align:center;">
          <input type="number" class="form-input gantt-task-end-input" data-idx="${idx}" min="1" max="${totM}" value="${e}" style="font-size:0.8rem; padding:4px; width:52px; text-align:center;">
        </td>
        <td style="text-align:center; font-weight:700; color:#2563eb; font-size:0.78rem;">
          ${dur} mo
        </td>
        <td>
          <input type="text" class="form-input gantt-task-gate-input" data-idx="${idx}" value="${escapeHtml(t.gate || '')}" placeholder="Go/No-Go Decision Gate (e.g. ≥2-fold improvement)..." style="font-size:0.78rem; padding:4px 8px; width:100%;">
        </td>
        <td style="text-align:center;">
          <button type="button" class="btn-delete-gantt-task" data-idx="${idx}" title="Remove this timeline milestone" style="background:none; border:none; color:#ef4444; font-size:1rem; cursor:pointer; padding:2px 4px; border-radius:4px; line-height:1;">✕</button>
        </td>
      </tr>
    `;
  }).join("");

  tbody.querySelectorAll(".gantt-task-name-input").forEach(inp => {
    inp.addEventListener("input", (e) => {
      const idx = parseInt(e.target.getAttribute("data-idx"), 10);
      if (gs.tasks[idx]) {
        gs.tasks[idx].name = e.target.value;
        syncGanttLegacyProperties();
        saveToStorage();
        renderStep5GanttVisual();
      }
    });
  });

  tbody.querySelectorAll(".gantt-task-start-input").forEach(inp => {
    inp.addEventListener("input", (e) => {
      const idx = parseInt(e.target.getAttribute("data-idx"), 10);
      if (gs.tasks[idx]) {
        const val = Math.max(1, Math.min(totM, parseInt(e.target.value, 10) || 1));
        gs.tasks[idx].start = val;
        if (gs.tasks[idx].end < val) gs.tasks[idx].end = val;
        syncGanttLegacyProperties();
        saveToStorage();
        renderGanttTasksTable();
        renderStep5GanttVisual();
      }
    });
  });

  tbody.querySelectorAll(".gantt-task-end-input").forEach(inp => {
    inp.addEventListener("input", (e) => {
      const idx = parseInt(e.target.getAttribute("data-idx"), 10);
      if (gs.tasks[idx]) {
        const val = Math.max(parseInt(gs.tasks[idx].start, 10) || 1, Math.min(totM, parseInt(e.target.value, 10) || totM));
        gs.tasks[idx].end = val;
        syncGanttLegacyProperties();
        saveToStorage();
        renderGanttTasksTable();
        renderStep5GanttVisual();
      }
    });
  });

  tbody.querySelectorAll(".gantt-task-gate-input").forEach(inp => {
    inp.addEventListener("input", (e) => {
      const idx = parseInt(e.target.getAttribute("data-idx"), 10);
      if (gs.tasks[idx]) {
        gs.tasks[idx].gate = e.target.value;
        syncGanttLegacyProperties();
        saveToStorage();
        renderStep5GanttVisual();
      }
    });
  });

  tbody.querySelectorAll(".btn-delete-gantt-task").forEach(btn => {
    btn.addEventListener("click", () => {
      const idx = parseInt(btn.getAttribute("data-idx"), 10);
      if (!isNaN(idx) && gs.tasks[idx]) {
        gs.tasks.splice(idx, 1);
        syncGanttLegacyProperties();
        saveToStorage();
        renderGanttTasksTable();
        renderStep5GanttVisual();
        showToast("Timeline milestone removed.");
      }
    });
  });
}

function renderStep5GanttVisual() {
  const container = document.getElementById("step5-gantt-visual-container");
  if (!container) return;
  ensureGanttTasks();
  const gs = projectState.gantt_schedule || {};
  const totalMonths = Math.max(3, Math.min(60, parseInt(gs.total_months, 10) || 18));
  const tasks = gs.tasks || [];

  let monthHeaders = "";
  const step = totalMonths > 24 ? 2 : 1;
  for (let m = 1; m <= totalMonths; m += step) {
    monthHeaders += `<div style="flex:1; text-align:center; font-size:0.68rem; color:#64748b; border-right:1px dashed #e2e8f0; padding:2px 0;">M${m}</div>`;
  }

  const calcLeft = (start) => ((start - 1) / totalMonths * 100).toFixed(1) + "%";
  const calcWidth = (start, end) => (((end - start + 1) / totalMonths) * 100).toFixed(1) + "%";

  let tasksHtml = "";
  if (tasks.length === 0) {
    tasksHtml = `<div style="text-align:center; font-size:0.75rem; color:#64748b; padding:12px;">Add timeline milestones above to visualize work package flows.</div>`;
  } else {
    tasksHtml = tasks.map((t, i) => {
      const color = GANTT_PALETTE[i % GANTT_PALETTE.length];
      const s = Math.max(1, Math.min(totalMonths, parseInt(t.start, 10) || 1));
      const e = Math.max(s, Math.min(totalMonths, parseInt(t.end, 10) || totalMonths));
      const name = t.name || `Phase ${i + 1}`;
      const gate = t.gate ? `🏁 ${t.gate}` : '';
      return `
        <div style="margin-bottom:8px;">
          <div style="display:flex; justify-content:space-between; font-size:0.75rem; font-weight:600; color:${color.text}; margin-bottom:2px;">
            <span>${escapeHtml(name)} (M${s}–M${e})</span>
            <span style="font-size:0.7rem; color:#64748b;">${escapeHtml(gate)}</span>
          </div>
          <div style="position:relative; height:18px; background:#f1f5f9; border-radius:4px; overflow:hidden;">
            <div style="position:absolute; left:${calcLeft(s)}; width:${calcWidth(s, e)}; height:100%; background:${color.bar}; border-radius:4px;"></div>
          </div>
        </div>
      `;
    }).join("");
  }

  container.innerHTML = `
    <div style="font-size: 0.78rem; font-weight: 700; color: #1e1b4b; margin-bottom: 8px;">
      ${totalMonths}-Month Project Work Package Gantt Flow (${tasks.length} Milestone${tasks.length === 1 ? '' : 's'})
    </div>
    <div style="display:flex; border-bottom:1px solid #cbd5e1; margin-bottom:8px; background:#f1f5f9; border-radius:4px;">
      ${monthHeaders}
    </div>
    ${tasksHtml}
  `;
}

function getDefaultMaterials() {
  return [
    { item: "High-Fidelity DNA Polymerase & Master Mix (500 U)", vendor: "New England Biolabs (NEB)", catalog: "M0530L", category: "consumables", qty: 2, unit_cost: 285 },
    { item: "HiFi DNA Assembly / Gibson Cloning Master Mix (50 rxns)", vendor: "New England Biolabs (NEB)", catalog: "E2621L", category: "consumables", qty: 2, unit_cost: 360 },
    { item: "Commercial Gene Synthesis & Target Fragment (5 kb total)", vendor: "Integrated DNA Technologies (IDT)", catalog: "GENE-CUSTOM", category: "consumables", qty: 1, unit_cost: 1450 },
    { item: "Plasmid Miniprep & PCR Purification Spin Columns (250 preps)", vendor: "Qiagen", catalog: "27106", category: "consumables", qty: 3, unit_cost: 320 },
    { item: "Protein Purification Ni-NTA Agarose Resin (100 mL)", vendor: "Thermo Fisher Scientific", catalog: "R90101", category: "consumables", qty: 2, unit_cost: 640 },
    { item: "Analytical Chromatographic Standards & Solvents (HPLC Grade)", vendor: "Sigma-Aldrich / Merck", catalog: "PHR1000", category: "consumables", qty: 4, unit_cost: 410 },
    { item: "Graduate Student Research Stipends (Part-Time, 2 Semesters)", vendor: "Institutional Payroll / HR", catalog: "GRS-STIPEND", category: "personnel", qty: 2, unit_cost: 6000 },
    { item: "Temperature-Controlled Benchtop Shaker / Incubator Maintenance", vendor: "Eppendorf", catalog: "5425-SVC", category: "equipment", qty: 1, unit_cost: 4500 },
    { item: "Sanger Sequencing & Fragment Analyzer Core Facility Access", vendor: "Local / Institutional Facility", catalog: "CORE-SEQ", category: "utilities", qty: 12, unit_cost: 125 },
    { item: "Biosafety Level 2 Overhead & Hazardous Waste Compliance", vendor: "Local / Institutional Facility", catalog: "SAFETY-COMPL", category: "utilities", qty: 1, unit_cost: 3000 }
  ];
}

function renderMaterialsTable() {
  const tbody = document.getElementById("materials-budget-tbody");
  if (!tbody) return;

  if (!Array.isArray(projectState.budget_materials)) {
    projectState.budget_materials = [];
  }

  if (projectState.budget_materials.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align:center; padding:18px; color:#64748b; font-size:0.82rem;">
          No items added yet. Click <strong>+ Add Material Item</strong> to enter custom reagents or <strong>⚡ Load Standard Reagents</strong> for typical molecular biology kits.
        </td>
      </tr>
    `;
    recalculateMaterialsBudget();
    return;
  }

  let html = "";
  projectState.budget_materials.forEach((mat, idx) => {
    const qty = Math.max(1, parseInt(mat.qty, 10) || 1);
    const unitCost = Math.max(0, parseFloat(mat.unit_cost) || 0);
    const lineTotal = qty * unitCost;

    html += `
      <tr data-row-idx="${idx}" style="border-bottom:1px solid #e2e8f0;">
        <td style="padding:4px 6px;">
          <input type="text" class="form-input mat-field mat-item" data-field="item" data-idx="${idx}" value="${escapeHtml(mat.item || '')}" placeholder="e.g. Q5 High-Fidelity DNA Polymerase" style="padding:3px 6px; font-size:0.78rem; width:100%;">
        </td>
        <td style="padding:4px 6px;">
          <input type="text" class="form-input mat-field mat-vendor" list="vendor-suggestions" data-field="vendor" data-idx="${idx}" value="${escapeHtml(mat.vendor || '')}" placeholder="e.g. NEB, Thermo" style="padding:3px 6px; font-size:0.78rem; width:100%;">
        </td>
        <td style="padding:4px 6px;">
          <input type="text" class="form-input mat-field mat-catalog" data-field="catalog" data-idx="${idx}" value="${escapeHtml(mat.catalog || '')}" placeholder="SKU / Cat #" style="padding:3px 6px; font-size:0.78rem; width:100%;">
        </td>
        <td style="padding:4px 6px;">
          <select class="form-input mat-field mat-category" data-field="category" data-idx="${idx}" style="padding:3px 4px; font-size:0.75rem; width:100%;">
            <option value="consumables"${mat.category === 'consumables' ? ' selected' : ''}>Consumables</option>
            <option value="personnel"${mat.category === 'personnel' ? ' selected' : ''}>Personnel</option>
            <option value="utilities"${mat.category === 'utilities' ? ' selected' : ''}>Overhead/Util</option>
            <option value="equipment"${mat.category === 'equipment' ? ' selected' : ''}>Equipment</option>
          </select>
        </td>
        <td style="padding:4px 6px; text-align:center;">
          <input type="number" min="1" step="1" class="form-input mat-field mat-qty" data-field="qty" data-idx="${idx}" value="${qty}" style="padding:3px 4px; font-size:0.78rem; width:50px; text-align:center;">
        </td>
        <td style="padding:4px 6px; text-align:right;">
          <input type="number" min="0" step="1" class="form-input mat-field mat-cost" data-field="unit_cost" data-idx="${idx}" value="${unitCost}" style="padding:3px 4px; font-size:0.78rem; width:75px; text-align:right;">
        </td>
        <td style="padding:4px 6px; text-align:right; font-weight:700; color:#1e293b; font-size:0.8rem;" class="mat-line-total">
          $${lineTotal.toLocaleString()}
        </td>
        <td style="padding:4px 6px; text-align:center;">
          <button type="button" class="btn-del-material" data-idx="${idx}" title="Delete Item" style="background:none; border:none; color:#ef4444; font-size:0.9rem; cursor:pointer; padding:2px 4px;">✕</button>
        </td>
      </tr>
    `;
  });

  tbody.innerHTML = html;

  // Bind input listeners
  tbody.querySelectorAll(".mat-field").forEach(inp => {
    inp.addEventListener("input", (e) => {
      const idx = parseInt(e.target.getAttribute("data-idx"), 10);
      const field = e.target.getAttribute("data-field");
      if (projectState.budget_materials[idx]) {
        let val = e.target.value;
        if (field === "qty") val = parseInt(val, 10) || 1;
        if (field === "unit_cost") val = parseFloat(val) || 0;
        projectState.budget_materials[idx][field] = val;
        
        // Update line total on same row
        const row = e.target.closest("tr");
        if (row) {
          const m = projectState.budget_materials[idx];
          const lt = (parseInt(m.qty, 10) || 1) * (parseFloat(m.unit_cost) || 0);
          const totalCell = row.querySelector(".mat-line-total");
          if (totalCell) totalCell.textContent = `$${lt.toLocaleString()}`;
        }
        recalculateMaterialsBudget();
        saveToStorage();
        if (typeof updateLiveScoreDebounced === "function") updateLiveScoreDebounced();
      }
    });
  });

  tbody.querySelectorAll(".btn-del-material").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const idx = parseInt(e.target.getAttribute("data-idx"), 10);
      deleteMaterialRow(idx);
    });
  });

  recalculateMaterialsBudget();
}

function recalculateMaterialsBudget() {
  const totals = { consumables: 0, personnel: 0, utilities: 0, equipment: 0 };
  const mats = projectState.budget_materials || [];

  if (mats.length > 0) {
    mats.forEach(m => {
      const cat = totals.hasOwnProperty(m.category) ? m.category : "consumables";
      const q = Math.max(1, parseInt(m.qty, 10) || 1);
      const c = Math.max(0, parseFloat(m.unit_cost) || 0);
      totals[cat] += (q * c);
    });
    projectState.budget_items = { ...totals };
  } else {
    totals.consumables = parseFloat(projectState.budget_items?.consumables || 18500);
    totals.personnel = parseFloat(projectState.budget_items?.personnel || 12000);
    totals.utilities = parseFloat(projectState.budget_items?.utilities || 4500);
    totals.equipment = parseFloat(projectState.budget_items?.equipment || 15000);
  }

  // Sync hidden inputs
  const cEl = document.getElementById("budget-consumables");
  const pEl = document.getElementById("budget-personnel");
  const uEl = document.getElementById("budget-utilities");
  const eEl = document.getElementById("budget-equipment");
  if (cEl) cEl.value = totals.consumables;
  if (pEl) pEl.value = totals.personnel;
  if (uEl) uEl.value = totals.utilities;
  if (eEl) eEl.value = totals.equipment;

  const grandTotal = totals.consumables + totals.personnel + totals.utilities + totals.equipment;
  const totDisplay = document.getElementById("budget-total-display");
  if (totDisplay) totDisplay.textContent = `$${grandTotal.toLocaleString()}`;

  const brkDisplay = document.getElementById("budget-breakdown-display");
  if (brkDisplay) {
    const pCons = grandTotal > 0 ? Math.round((totals.consumables / grandTotal) * 100) : 0;
    const pPers = grandTotal > 0 ? Math.round((totals.personnel / grandTotal) * 100) : 0;
    const pUtil = grandTotal > 0 ? Math.round((totals.utilities / grandTotal) * 100) : 0;
    const pEquip = grandTotal > 0 ? Math.round((totals.equipment / grandTotal) * 100) : 0;
    brkDisplay.textContent = `Consumables: ${pCons}% | Personnel: ${pPers}% | Overhead: ${pUtil}% | Equipment: ${pEquip}%`;
  }
}

function addMaterialRow(itemData) {
  if (!Array.isArray(projectState.budget_materials)) projectState.budget_materials = [];
  const newItem = itemData || {
    item: "",
    vendor: "",
    catalog: "",
    category: "consumables",
    qty: 1,
    unit_cost: 100
  };
  projectState.budget_materials.push(newItem);
  renderMaterialsTable();
  saveToStorage();
}

function deleteMaterialRow(idx) {
  if (Array.isArray(projectState.budget_materials) && idx >= 0 && idx < projectState.budget_materials.length) {
    projectState.budget_materials.splice(idx, 1);
    renderMaterialsTable();
    saveToStorage();
    showToast("Material item removed.");
  }
}

function populateFormFields() {
  const setVal = (id, val) => {
    const el = document.getElementById(id);
    if (el && val !== undefined) el.value = val;
  };

  setVal("student-name-input", projectState.student_name);
  setVal("student-id-input", projectState.student_id);
  setVal("project-model-select", projectState.model_id || "cellular");
  updateModelLabels(projectState.model_id || "cellular");

  setVal("custom-modality-input", projectState.custom_modality || "");
  const customModInput = document.getElementById("custom-modality-input");
  if (customModInput) {
    customModInput.style.display = (projectState.model_id === "custom") ? "block" : "none";
  }

  setVal("project-keywords-input", projectState.keywords || "");
  renderKeywordTags(projectState.keywords || "");

  setVal("pillar-chassis", projectState.system || projectState.chassis);
  setVal("pillar-tool", projectState.tool);
  setVal("pillar-target", projectState.target);

  // Matrix
  setVal("matrix-yellow", projectState.matrix.yellow);
  setVal("matrix-blue", projectState.matrix.blue);
  setVal("matrix-green", projectState.matrix.green);
  setVal("matrix-purple", projectState.matrix.purple);
  setVal("matrix-red", projectState.matrix.red);
  setVal("matrix-citation", projectState.matrix.citation);

  // Restore Decoded Literature Intelligence & Explanations if cached
  if (projectState.decoded_paper_cache) {
    currentDecodedData = projectState.decoded_paper_cache;
    updateMatrixExplainer(projectState.decoded_paper_cache);
  }

  // Title, Abstract & Funnel
  setVal("proposal-title-input", projectState.title);
  setVal("abstract-input", projectState.abstract);
  setVal("funnel-tier1", projectState.funnel.tier1);
  setVal("funnel-tier2", projectState.funnel.tier2);
  setVal("funnel-tier3", projectState.funnel.tier3);
  setVal("funnel-tier4", projectState.funnel.tier4);

  // Aims
  setVal("funnel-overarching-aim", projectState.overarching_aim);
  setVal("aim1-input", projectState.aims.aim1);
  setVal("aim1-title", projectState.aims?.aim1_title || "");
  setVal("aim2-input", projectState.aims.aim2);
  setVal("aim2-title", projectState.aims?.aim2_title || "");
  setVal("aim3-input", projectState.aims.aim3);
  setVal("aim3-title", projectState.aims?.aim3_title || "");
  updateGanttAimLabels();

  // Deliverables & Impact
  setVal("expected-outcomes-input", projectState.expected_outcomes);
  setVal("impact-input", projectState.impact);
  setVal("customer-input", projectState.customer);
  setVal("market-input", projectState.market);
  setVal("usps-input", projectState.usps);

  // Competitor Matrix (Exact 9 Dimensions)
  const cd = projectState.competitor_data || {};
  // 1. Principle / technology
  setVal("comp-est-principle", cd.principle_established || cd.incumbent_name || "");
  setVal("comp-rec-principle", cd.principle_recent || cd.emerging_name || "");
  setVal("comp-prop-principle", cd.principle_proposed || cd.proposed_name || projectState.tool || "");
  // 2. Main strength
  setVal("comp-est-strength", cd.strength_established || "");
  setVal("comp-rec-strength", cd.strength_recent || "");
  setVal("comp-prop-strength", cd.strength_proposed || "");
  // 3. Key limitation
  setVal("comp-est-limitation", cd.limitation_established || "");
  setVal("comp-rec-limitation", cd.limitation_recent || "");
  setVal("comp-prop-limitation", cd.limitation_proposed || "");
  // 4. Performance
  setVal("comp-est-performance", cd.performance_established || cd.incumbent_speed || "");
  setVal("comp-rec-performance", cd.performance_recent || cd.emerging_speed || "");
  setVal("comp-prop-performance", cd.performance_proposed || cd.proposed_speed || "");
  // 5. Cost / resources
  setVal("comp-est-cost", cd.cost_established || cd.incumbent_cost || "");
  setVal("comp-rec-cost", cd.cost_recent || cd.emerging_cost || "");
  setVal("comp-prop-cost", cd.cost_proposed || cd.proposed_cost || "");
  // 6. Safety / sustainability
  setVal("comp-est-safety", cd.safety_established || cd.incumbent_safety || "");
  setVal("comp-rec-safety", cd.safety_recent || cd.emerging_safety || "");
  setVal("comp-prop-safety", cd.safety_proposed || cd.proposed_safety || "");
  // 7. Evidence available
  setVal("comp-est-evidence", cd.evidence_established || "");
  setVal("comp-rec-evidence", cd.evidence_recent || "");
  setVal("comp-prop-evidence", cd.evidence_proposed || "");
  // 8. Unresolved gap
  setVal("comp-est-gap", cd.gap_established || "");
  setVal("comp-rec-gap", cd.gap_recent || "");
  setVal("comp-prop-gap", cd.gap_proposed || "");
  // 9. Contribution of proposed study
  setVal("comp-prop-contribution", cd.contribution_proposed || "");

  // Legacy field backup sync
  setVal("comp-incumbent-name", cd.incumbent_name || cd.principle_established || "");
  setVal("comp-emerging-name", cd.emerging_name || cd.principle_recent || "");
  setVal("comp-proposed-name", cd.proposed_name || cd.principle_proposed || "");

  // Gantt Dynamic Duration & Scheduler Controls
  ensureGanttTasks();
  syncGanttLegacyProperties();
  const gs = projectState.gantt_schedule || {};
  const totM = Math.max(3, Math.min(60, parseInt(gs.total_months, 10) || 18));
  setVal("gantt-total-duration", totM);
  const durPreset = document.getElementById("gantt-duration-preset");
  if (durPreset) {
    durPreset.value = [6, 12, 18, 24, 36].includes(totM) ? totM.toString() : "custom";
  }
  renderGanttTasksTable();
  renderStep5GanttVisual();

  // Itemized Materials & Funding Table
  renderMaterialsTable();

  // Methods, SWOT & Timeline
  setVal("methodology-input", projectState.methodology);
  setVal("swot-s", projectState.swot.strengths);
  setVal("swot-w", projectState.swot.weaknesses);
  setVal("swot-o", projectState.swot.opportunities);
  setVal("swot-t", projectState.swot.threats);
  setVal("timeplan-input", projectState.time_plan);
  setVal("budget-input", projectState.budget);
  setVal("references-input", projectState.references);

  // Aims Contingencies (B1)
  const cont = projectState.aims_contingencies || {};
  setVal("aim1-fallback", cont.aim1_fallback);
  setVal("aim2-fallback", cont.aim2_fallback);
  setVal("aim3-fallback", cont.aim3_fallback);

  // Control Triad (B2)
  const triad = projectState.control_triad || {};
  setVal("control-negative", triad.negative);
  setVal("control-positive", triad.positive);
  setVal("control-specificity", triad.specificity);

  // Biotech FMEA Matrix (B3)
  const fmea = projectState.biotech_risk_matrix || {};
  setVal("fmea-off-target", fmea.off_target);
  setVal("fmea-toxicity", fmea.toxicity);
  setVal("fmea-solubility", fmea.solubility);
  setVal("fmea-biosafety", fmea.biosafety);

  // Proposal Lock State (Part 3.3)
  if (typeof applyLockStateToUI === "function") {
    applyLockStateToUI(Boolean(projectState.is_locked_for_grading));
  }
}

function initModelSelector() {
  const select = document.getElementById("project-model-select");
  const customInput = document.getElementById("custom-modality-input");
  if (!select) return;
  select.addEventListener("change", (e) => {
    const modelId = e.target.value;
    projectState.model_id = modelId;
    if (customInput) {
      customInput.style.display = (modelId === "custom") ? "block" : "none";
      if (modelId === "custom") customInput.focus();
    }
    updateModelLabels(modelId);
    saveToStorage();
    showToast(`Model updated: ${modelId === 'custom' ? 'Custom Interdisciplinary Modality' : (projectModels[modelId] ? projectModels[modelId].name : modelId)}`);
  });
}

function updateModelLabels(modelId) {
  const m = projectModels[modelId] || projectModels["cellular"];
  const tipEl = document.getElementById("model-description-tip");
  if (tipEl) tipEl.innerText = m.desc;

  const setHtml = (id, html) => { const el = document.getElementById(id); if (el) el.innerHTML = html; };
  const setAttr = (id, attr, val) => { const el = document.getElementById(id); if (el) el.setAttribute(attr, val); };

  setHtml("label-pillar1", m.p1.label);
  setHtml("desc-pillar1", m.p1.placeholder);
  setAttr("pillar-chassis", "placeholder", m.p1.placeholder);
  setHtml("example-pillar1", `Examples: <code>${m.p1.examples}</code>`);

  setHtml("label-pillar2", m.p2.label);
  setHtml("desc-pillar2", m.p2.placeholder);
  setAttr("pillar-tool", "placeholder", m.p2.placeholder);
  setHtml("example-pillar2", `Examples: <code>${m.p2.examples}</code>`);

  setHtml("label-pillar3", m.p3.label);
  setHtml("desc-pillar3", m.p3.placeholder);
  setAttr("pillar-target", "placeholder", m.p3.placeholder);
  setHtml("example-pillar3", `Examples: <code>${m.p3.examples}</code>`);
}

function initCourseSwitcher() {
  const select = document.getElementById("course-switcher-select");
  if (!select) return;
  select.addEventListener("change", async (e) => {
    const cid = e.target.value;
    try {
      const resp = await fetch("/api/courses/switch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ course_id: cid })
      });
      const data = await resp.json();
      if (data.success) {
        showToast(`Switched active curriculum to ${data.course.course_name}`);
        updateLiveScore();
      }
    } catch (err) {
      console.error(err);
    }
  });
}

function initFormBindings() {
  const bind = (id, callback) => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("input", (e) => {
        callback(e.target.value);
        saveToStorage();
        updateLiveScoreDebounced();
      });
    }
  };

  bind("student-name-input", v => projectState.student_name = v);
  bind("student-id-input", v => {
    projectState.student_id = v;
    triggerServerSyncDebounced();
  });
  bind("pillar-chassis", v => { projectState.system = v; projectState.chassis = v; });
  bind("pillar-tool", v => projectState.tool = v);
  bind("pillar-target", v => projectState.target = v);

  bind("matrix-yellow", v => projectState.matrix.yellow = v);
  bind("matrix-blue", v => projectState.matrix.blue = v);
  bind("matrix-green", v => projectState.matrix.green = v);
  bind("matrix-purple", v => projectState.matrix.purple = v);
  bind("matrix-red", v => projectState.matrix.red = v);
  bind("matrix-citation", v => projectState.matrix.citation = v);

  bind("proposal-title-input", v => projectState.title = v);
  bind("abstract-input", v => {
    projectState.abstract = v;
    updateWordCount("abstract-count", v, 250);
  });

  bind("funnel-tier1", v => projectState.funnel.tier1 = v);
  bind("funnel-tier2", v => projectState.funnel.tier2 = v);
  bind("funnel-tier3", v => projectState.funnel.tier3 = v);
  bind("funnel-tier4", v => projectState.funnel.tier4 = v);

  bind("custom-modality-input", v => { projectState.custom_modality = v; });
  bind("project-keywords-input", v => {
    projectState.keywords = v;
    renderKeywordTags(v);
  });

  bind("funnel-overarching-aim", v => projectState.overarching_aim = v);
  bind("aim1-input", v => projectState.aims.aim1 = v);
  bind("aim1-title", v => {
    if (!projectState.aims) projectState.aims = {};
    projectState.aims.aim1_title = v;
    updateGanttAimLabels();
    renderStep5GanttVisual();
  });
  bind("aim2-input", v => projectState.aims.aim2 = v);
  bind("aim2-title", v => {
    if (!projectState.aims) projectState.aims = {};
    projectState.aims.aim2_title = v;
    updateGanttAimLabels();
    renderStep5GanttVisual();
  });
  bind("aim3-input", v => projectState.aims.aim3 = v);
  bind("aim3-title", v => {
    if (!projectState.aims) projectState.aims = {};
    projectState.aims.aim3_title = v;
    updateGanttAimLabels();
    renderStep5GanttVisual();
  });

  bind("methodology-input", v => {
    projectState.methodology = v;
    checkTenseWarning(v);
  });

  bind("expected-outcomes-input", v => projectState.expected_outcomes = v);
  bind("impact-input", v => projectState.impact = v);
  bind("customer-input", v => projectState.customer = v);
  bind("market-input", v => projectState.market = v);
  bind("usps-input", v => projectState.usps = v);


  // Competitor Matrix (Exact 9 Dimensions)
  // 1. Principle / technology
  bind("comp-est-principle", v => { projectState.competitor_data.principle_established = v; projectState.competitor_data.incumbent_name = v; });
  bind("comp-rec-principle", v => { projectState.competitor_data.principle_recent = v; projectState.competitor_data.emerging_name = v; });
  bind("comp-prop-principle", v => { projectState.competitor_data.principle_proposed = v; projectState.competitor_data.proposed_name = v; });

  // 2. Main strength
  bind("comp-est-strength", v => projectState.competitor_data.strength_established = v);
  bind("comp-rec-strength", v => projectState.competitor_data.strength_recent = v);
  bind("comp-prop-strength", v => projectState.competitor_data.strength_proposed = v);

  // 3. Key limitation
  bind("comp-est-limitation", v => projectState.competitor_data.limitation_established = v);
  bind("comp-rec-limitation", v => projectState.competitor_data.limitation_recent = v);
  bind("comp-prop-limitation", v => projectState.competitor_data.limitation_proposed = v);

  // 4. Performance
  bind("comp-est-performance", v => { projectState.competitor_data.performance_established = v; projectState.competitor_data.incumbent_speed = v; });
  bind("comp-rec-performance", v => { projectState.competitor_data.performance_recent = v; projectState.competitor_data.emerging_speed = v; });
  bind("comp-prop-performance", v => { projectState.competitor_data.performance_proposed = v; projectState.competitor_data.proposed_speed = v; });

  // 5. Cost / resources
  bind("comp-est-cost", v => { projectState.competitor_data.cost_established = v; projectState.competitor_data.incumbent_cost = v; });
  bind("comp-rec-cost", v => { projectState.competitor_data.cost_recent = v; projectState.competitor_data.emerging_cost = v; });
  bind("comp-prop-cost", v => { projectState.competitor_data.cost_proposed = v; projectState.competitor_data.proposed_cost = v; });

  // 6. Safety / sustainability
  bind("comp-est-safety", v => { projectState.competitor_data.safety_established = v; projectState.competitor_data.incumbent_safety = v; });
  bind("comp-rec-safety", v => { projectState.competitor_data.safety_recent = v; projectState.competitor_data.emerging_safety = v; });
  bind("comp-prop-safety", v => { projectState.competitor_data.safety_proposed = v; projectState.competitor_data.proposed_safety = v; });

  // 7. Evidence available
  bind("comp-est-evidence", v => projectState.competitor_data.evidence_established = v);
  bind("comp-rec-evidence", v => projectState.competitor_data.evidence_recent = v);
  bind("comp-prop-evidence", v => projectState.competitor_data.evidence_proposed = v);

  // 8. Unresolved gap
  bind("comp-est-gap", v => projectState.competitor_data.gap_established = v);
  bind("comp-rec-gap", v => projectState.competitor_data.gap_recent = v);
  bind("comp-prop-gap", v => projectState.competitor_data.gap_proposed = v);

  // 9. Contribution of proposed study
  bind("comp-prop-contribution", v => projectState.competitor_data.contribution_proposed = v);

  // Legacy field backup bindings
  bind("comp-incumbent-name", v => { projectState.competitor_data.incumbent_name = v; projectState.competitor_data.principle_established = v; });
  bind("comp-emerging-name", v => { projectState.competitor_data.emerging_name = v; projectState.competitor_data.principle_recent = v; });
  bind("comp-proposed-name", v => { projectState.competitor_data.proposed_name = v; projectState.competitor_data.principle_proposed = v; });

  // Gantt Dynamic Duration & Scheduler Controls
  const durPreset = document.getElementById("gantt-duration-preset");
  const durInput = document.getElementById("gantt-total-duration");

  if (durPreset && !durPreset._wired) {
    durPreset._wired = true;
    durPreset.addEventListener("change", (e) => {
      const val = e.target.value;
      if (val !== "custom") {
        const months = parseInt(val, 10);
        if (durInput) durInput.value = months;
        if (!projectState.gantt_schedule) projectState.gantt_schedule = {};
        projectState.gantt_schedule.total_months = months;
        ensureGanttTasks();
        // Scale/clamp existing tasks if they exceed new total
        (projectState.gantt_schedule.tasks || []).forEach(t => {
          if (t.start > months) t.start = Math.max(1, months - 2);
          if (t.end > months) t.end = months;
        });
        syncGanttLegacyProperties();
        saveToStorage();
        renderGanttTasksTable();
        renderStep5GanttVisual();
        showToast(`Project duration set to ${months} months.`);
      }
    });
  }

  if (durInput && !durInput._wired) {
    durInput._wired = true;
    durInput.addEventListener("input", (e) => {
      const months = Math.max(3, Math.min(60, parseInt(e.target.value, 10) || 18));
      if (!projectState.gantt_schedule) projectState.gantt_schedule = {};
      projectState.gantt_schedule.total_months = months;
      if (durPreset) {
        durPreset.value = [6, 12, 18, 24, 36].includes(months) ? months.toString() : "custom";
      }
      ensureGanttTasks();
      (projectState.gantt_schedule.tasks || []).forEach(t => {
        if (t.start > months) t.start = Math.max(1, months - 2);
        if (t.end > months) t.end = months;
      });
      syncGanttLegacyProperties();
      saveToStorage();
      renderGanttTasksTable();
      renderStep5GanttVisual();
    });
  }

  // Literature Benchmark Timeline Apply Button
  const btnApplyBenchmark = document.getElementById("btn-apply-timeline-benchmark");
  if (btnApplyBenchmark && !btnApplyBenchmark._wired) {
    btnApplyBenchmark._wired = true;
    btnApplyBenchmark.addEventListener("click", () => {
      ensureGanttTasks();
      const gs = projectState.gantt_schedule || {};
      const totM = Math.max(3, Math.min(60, parseInt(gs.total_months, 10) || 18));
      const a = projectState.aims || {};

      const w1_s = 1;
      const w1_e = Math.max(2, Math.round(totM * 0.33));
      const w2_s = Math.max(2, Math.round(totM * 0.28));
      const w2_e = Math.max(w2_s + 1, Math.round(totM * 0.67));
      const w3_s = Math.max(3, Math.round(totM * 0.55));
      const w3_e = totM;

      gs.tasks = [
        {
          name: a.aim1_title ? `WP1: ${a.aim1_title}` : "WP1: Construction & Preparation",
          start: w1_s,
          end: w1_e,
          gate: "Sequence verified & vector expression confirmed"
        },
        {
          name: a.aim2_title ? `WP2: ${a.aim2_title}` : "WP2: Functional Testing & Evaluation",
          start: w2_s,
          end: w2_e,
          gate: "Quantitative activity & kinetic threshold achieved"
        },
        {
          name: a.aim3_title ? `WP3: ${a.aim3_title}` : "WP3: Real-World Validation & Performance",
          start: w3_s,
          end: w3_e,
          gate: "Target milestone validated in realistic operational matrix"
        }
      ];

      syncGanttLegacyProperties();
      saveToStorage();
      renderGanttTasksTable();
      renderStep5GanttVisual();
      showToast(`Applied literature benchmark schedule for ${totM}-month study!`);
    });
  }

  // Add Dynamic Timeline Milestone Button
  const btnAddGanttPoint = document.getElementById("btn-add-gantt-point");
  if (btnAddGanttPoint && !btnAddGanttPoint._wired) {
    btnAddGanttPoint._wired = true;
    btnAddGanttPoint.addEventListener("click", () => {
      ensureGanttTasks();
      const gs = projectState.gantt_schedule || {};
      const totM = Math.max(3, Math.min(60, parseInt(gs.total_months, 10) || 18));
      const count = (gs.tasks || []).length;
      const lastEnd = count > 0 ? (parseInt(gs.tasks[count - 1].end, 10) || 1) : 1;
      const newStart = Math.min(totM, Math.max(1, lastEnd));
      const newEnd = Math.min(totM, newStart + 3);

      if (!Array.isArray(gs.tasks)) gs.tasks = [];
      gs.tasks.push({
        name: `Milestone Phase ${count + 1}: Experimental Stage`,
        start: newStart,
        end: newEnd,
        gate: "Defined Go/No-Go Decision Gate"
      });

      syncGanttLegacyProperties();
      saveToStorage();
      renderGanttTasksTable();
      renderStep5GanttVisual();
      showToast(`Added Milestone Phase ${count + 1}! Edit duration & gate below.`);
    });
  }

  // Sync Gantt to Textplan Button
  const btnSyncGantt = document.getElementById("btn-sync-gantt-to-text");
  if (btnSyncGantt && !btnSyncGantt._wired) {
    btnSyncGantt._wired = true;
    btnSyncGantt.addEventListener("click", () => {
      ensureGanttTasks();
      const gs = projectState.gantt_schedule || {};
      const tasks = gs.tasks || [];
      const totM = Math.max(3, Math.min(60, parseInt(gs.total_months, 10) || 18));

      if (tasks.length === 0) {
        showToast("No milestones to sync. Click + Add Timeline Milestone first.");
        return;
      }

      const summary = tasks.map((t, idx) => {
        const s = t.start || 1;
        const e = t.end || totM;
        const gateStr = t.gate ? ` [Decision Gate: ${t.gate}]` : "";
        return `Phase ${idx + 1} (Months ${s}–${e}): ${t.name}.${gateStr}`;
      }).join("\n\n");

      const timeplanEl = document.getElementById("timeplan-input");
      if (timeplanEl) {
        timeplanEl.value = summary;
        projectState.time_plan = summary;
        saveToStorage();
        updateLiveScoreDebounced();
        showToast("Dynamic Gantt schedule synced to timeline summary!");
      }
    });
  }

  // Materials Table Action Buttons
  const btnAddMat = document.getElementById("btn-add-material-row");
  if (btnAddMat && !btnAddMat._wired) {
    btnAddMat._wired = true;
    btnAddMat.addEventListener("click", () => addMaterialRow());
  }

  const btnLoadMat = document.getElementById("btn-load-starter-materials");
  if (btnLoadMat && !btnLoadMat._wired) {
    btnLoadMat._wired = true;
    btnLoadMat.addEventListener("click", () => {
      projectState.budget_materials = getDefaultMaterials();
      renderMaterialsTable();
      saveToStorage();
      showToast("Standard molecular biology reagents loaded into budget!");
    });
  }

  const btnClearMat = document.getElementById("btn-clear-materials");
  if (btnClearMat && !btnClearMat._wired) {
    btnClearMat._wired = true;
    btnClearMat.addEventListener("click", () => {
      projectState.budget_materials = [];
      renderMaterialsTable();
      saveToStorage();
      showToast("Materials table cleared.");
    });
  }

  bind("swot-s", v => projectState.swot.strengths = v);
  bind("swot-w", v => { projectState.swot.weaknesses = v; checkClicheWarning(v); });
  bind("swot-o", v => projectState.swot.opportunities = v);
  bind("swot-t", v => { projectState.swot.threats = v; checkClicheWarning(v); });

  bind("timeplan-input", v => projectState.time_plan = v);
  bind("budget-input", v => projectState.budget = v);
  bind("references-input", v => projectState.references = v);

  // Aims Contingencies (B1)
  bind("aim1-fallback", v => {
    if (!projectState.aims_contingencies) projectState.aims_contingencies = {};
    projectState.aims_contingencies.aim1_fallback = v;
  });
  bind("aim2-fallback", v => {
    if (!projectState.aims_contingencies) projectState.aims_contingencies = {};
    projectState.aims_contingencies.aim2_fallback = v;
  });
  bind("aim3-fallback", v => {
    if (!projectState.aims_contingencies) projectState.aims_contingencies = {};
    projectState.aims_contingencies.aim3_fallback = v;
  });

  // Control Triad (B2)
  bind("control-negative", v => {
    if (!projectState.control_triad) projectState.control_triad = {};
    projectState.control_triad.negative = v;
  });
  bind("control-positive", v => {
    if (!projectState.control_triad) projectState.control_triad = {};
    projectState.control_triad.positive = v;
  });
  bind("control-specificity", v => {
    if (!projectState.control_triad) projectState.control_triad = {};
    projectState.control_triad.specificity = v;
  });

  // Biotech FMEA Matrix (B3)
  bind("fmea-off-target", v => {
    if (!projectState.biotech_risk_matrix) projectState.biotech_risk_matrix = {};
    projectState.biotech_risk_matrix.off_target = v;
  });
  bind("fmea-toxicity", v => {
    if (!projectState.biotech_risk_matrix) projectState.biotech_risk_matrix = {};
    projectState.biotech_risk_matrix.toxicity = v;
  });
  bind("fmea-solubility", v => {
    if (!projectState.biotech_risk_matrix) projectState.biotech_risk_matrix = {};
    projectState.biotech_risk_matrix.solubility = v;
  });
  bind("fmea-biosafety", v => {
    if (!projectState.biotech_risk_matrix) projectState.biotech_risk_matrix = {};
    projectState.biotech_risk_matrix.biosafety = v;
  });
}

function initStepperNavigation() {
  const indicators = document.querySelectorAll(".step-indicator");
  indicators.forEach(ind => {
    ind.addEventListener("click", () => goToStep(parseInt(ind.getAttribute("data-step"))));
  });

  document.querySelectorAll(".btn-step-prev").forEach(btn => {
    btn.addEventListener("click", () => goToStep(parseInt(btn.getAttribute("data-goto"))));
  });

  document.querySelectorAll(".btn-step-next").forEach(btn => {
    const target = btn.getAttribute("data-goto");
    if (target) btn.addEventListener("click", () => goToStep(parseInt(target)));
  });
}

function goToStep(stepNumber) {
  if (stepNumber < 1 || stepNumber > 6) return;
  currentStep = stepNumber;

  document.querySelectorAll(".step-panel").forEach(panel => panel.classList.remove("active"));
  const activePanel = document.getElementById(`step-panel-${stepNumber}`);
  if (activePanel) activePanel.classList.add("active");

  document.querySelectorAll(".step-indicator").forEach(ind => {
    const s = parseInt(ind.getAttribute("data-step"));
    ind.classList.remove("active");
    if (s === stepNumber) ind.classList.add("active");
    else if (s < stepNumber) ind.classList.add("completed");
  });

  window.scrollTo({ top: 0, behavior: "smooth" });
}

function initPresetSelector() {
  const select = document.getElementById("search-example-select");
  if (!select) return;
  select.addEventListener("change", async (e) => {
    const val = e.target.value;
    if (!val) return;
    try {
      const resp = await fetch("/api/search/examples");
      const examples = await resp.json();
      const chosen = examples[parseInt(val)];
      if (chosen) {
        if (chosen.model_id) {
          projectState.model_id = chosen.model_id;
          const modelSelect = document.getElementById("project-model-select");
          if (modelSelect) modelSelect.value = chosen.model_id;
          updateModelLabels(chosen.model_id);
        }
        const sysVal = chosen.system || chosen.chassis;
        document.getElementById("pillar-chassis").value = sysVal;
        document.getElementById("pillar-tool").value = chosen.tool;
        document.getElementById("pillar-target").value = chosen.target;

        projectState.system = sysVal;
        projectState.chassis = sysVal;
        projectState.tool = chosen.tool;
        projectState.target = chosen.target;
        saveToStorage();
        updateSearchLinksAndQuery();
        showToast(`Loaded ${chosen.category}: ${chosen.topic}`);
      }
    } catch (err) {
      console.error(err);
    }
  });
}

function updateSearchLinksAndQuery() {
  const chassis = (document.getElementById("pillar-chassis")?.value || projectState.chassis || projectState.system || "").trim();
  const tool = (document.getElementById("pillar-tool")?.value || projectState.tool || "").trim();
  const target = (document.getElementById("pillar-target")?.value || projectState.target || "").trim();

  let query = "";
  if (chassis && tool && target) {
    query = `("${chassis}") AND ("${tool}") AND ("${target}")`;
  } else if (chassis || tool || target) {
    const parts = [chassis, tool, target].filter(Boolean).map(p => `("${p}")`);
    query = parts.join(" AND ");
  } else {
    query = `"biotechnology" AND "enzyme" AND "yield"`;
  }

  const queryOut = document.getElementById("boolean-query-output");
  if (queryOut) queryOut.innerText = query;

  const encodedQuery = encodeURIComponent(query);
  const linkPubmed = document.getElementById("link-pubmed");
  if (linkPubmed) linkPubmed.href = `https://pubmed.ncbi.nlm.nih.gov/?term=${encodedQuery}`;

  const linkScholar = document.getElementById("link-scholar");
  if (linkScholar) linkScholar.href = `https://scholar.google.com/scholar?q=${encodedQuery}`;

  const linkEurope = document.getElementById("link-europe");
  if (linkEurope) linkEurope.href = `https://europepmc.org/search?query=${encodedQuery}`;
}

function initStep1Action() {
  const pChassis = document.getElementById("pillar-chassis");
  const pTool = document.getElementById("pillar-tool");
  const pTarget = document.getElementById("pillar-target");
  if (pChassis) pChassis.addEventListener("input", updateSearchLinksAndQuery);
  if (pTool) pTool.addEventListener("input", updateSearchLinksAndQuery);
  if (pTarget) pTarget.addEventListener("input", updateSearchLinksAndQuery);
  updateSearchLinksAndQuery();

  const btn = document.getElementById("btn-next-from-1");
  if (!btn) return;
  btn.addEventListener("click", async () => {
    const system = document.getElementById("pillar-chassis").value.trim();
    const tool = document.getElementById("pillar-tool").value.trim();
    const target = document.getElementById("pillar-target").value.trim();

    if (!system || !tool || !target) {
      showToast("Please specify all 3 research pillars.");
      return;
    }

    try {
      btn.innerText = "Formulating Search Query...";
      const resp = await fetch("/api/search/build", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chassis: system, tool, target })
      });
      const data = await resp.json();
      
      projectState.search_query = data.query;
      saveToStorage();

      document.getElementById("boolean-query-output").innerText = data.query;
      document.getElementById("link-pubmed").href = data.links.pubmed;
      document.getElementById("link-scholar").href = data.links.scholar;
      document.getElementById("link-europe").href = data.links.europe_pmc;

      goToStep(2);
      showToast("Step 2 unlocked! Review search links.");
    } catch (err) {
      console.error(err);
      showToast("Error generating search.");
    } finally {
      btn.innerText = "Lock in Research Pillars & Go to Step 2: Literature Search ➔";
    }
  });

  const btnCopy = document.getElementById("btn-copy-query");
  if (btnCopy) {
    btnCopy.addEventListener("click", () => {
      const q = document.getElementById("boolean-query-output").innerText;
      navigator.clipboard.writeText(q);
      showToast("Copied query string to clipboard!");
    });
  }
}

// DOI Auto-Resolver (Step 2)
function initDoiResolver() {
  const btn = document.getElementById("btn-fetch-doi");
  if (!btn) return;
  btn.addEventListener("click", async () => {
    const doiInput = document.getElementById("doi-lookup-input").value.trim();
    const resultsBox = document.getElementById("doi-results-box");
    if (!doiInput) {
      showToast("Please enter a DOI string.");
      return;
    }
    resultsBox.innerHTML = "<p><em>Resolving DOI via CrossRef API...</em></p>";
    try {
      const resp = await fetch("/api/reference/lookup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ doi: doiInput })
      });
      const data = await resp.json();
      if (data.success) {
        const badgeColor = data.is_recent ? "#059669" : "#dc2626";
        const badgeText = data.is_recent ? "✅ Recent (2021–2026)" : "⚠️ Older than 5 Years";
        resultsBox.innerHTML = `
          <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px; padding:12px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <strong>${data.title}</strong>
              <span style="background:${badgeColor}; color:white; font-size:0.75rem; padding:2px 8px; border-radius:4px; font-weight:700;">${badgeText}</span>
            </div>
            <div style="font-size:0.85rem; color:#475569; margin-top:4px;">${data.authors} (${data.year}) • <em>${data.journal}</em></div>
            <div style="margin-top:8px;">
              <button id="btn-insert-doi-ref" class="btn-insert-template" style="font-size:0.8rem;">+ Insert into References List</button>
            </div>
          </div>
        `;
        document.getElementById("btn-insert-doi-ref").addEventListener("click", () => {
          const refsEl = document.getElementById("references-input");
          if (refsEl) {
            refsEl.value = (refsEl.value ? refsEl.value + "\n" : "") + data.formatted_citation;
            refsEl.dispatchEvent(new Event("input"));
            showToast("Citation appended to References!");
          }
        });
      } else {
        resultsBox.innerHTML = `<p style="color:#dc2626;">Error: ${data.error}</p>`;
      }
    } catch (err) {
      console.error(err);
      resultsBox.innerHTML = "<p style='color:red;'>Failed to contact CrossRef.</p>";
    }
  });
}

// RHEV Paraphrase Gym (Step 3)
function initRhevParaphraseLab() {
  const btnHide = document.getElementById("btn-rhev-hide");
  const origTextarea = document.getElementById("rhev-original");
  if (btnHide && origTextarea) {
    btnHide.addEventListener("click", () => {
      origTextarea.classList.toggle("blurred");
      btnHide.innerText = origTextarea.classList.contains("blurred") ? "👁️ Unhide Original Text" : "👁️ Hide Original Text";
    });
  }

  const btnAudit = document.getElementById("btn-rhev-audit");
  if (btnAudit) {
    btnAudit.addEventListener("click", async () => {
      const original = document.getElementById("rhev-original").value.trim();
      const draft = document.getElementById("rhev-draft").value.trim();
      const resultsBox = document.getElementById("rhev-results-box");

      if (!original || !draft) {
        showToast("Please enter both the original sentence and your draft.");
        return;
      }

      resultsBox.innerHTML = "<p><em>Auditing n-gram overlap and Turnitin risk...</em></p>";
      try {
        const resp = await fetch("/api/paraphrase/check", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ original, draft })
        });
        const data = await resp.json();

        let badgeBg = data.risk_level === "low" ? "#10b981" : (data.risk_level === "medium" ? "#f59e0b" : "#ef4444");
        let html = `
          <div style="background:white; border:1px solid #c7d2fe; border-radius:8px; padding:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <strong>${data.verdict}</strong>
              <span style="background:${badgeBg}; color:white; font-size:0.75rem; padding:3px 8px; border-radius:4px; font-weight:800;">
                Turnitin Risk: ${data.risk_level.toUpperCase()} (${data.similarity_score}%)
              </span>
            </div>
            <p style="font-size:0.85rem; color:#334155; margin-bottom:8px;">${data.advice}</p>
        `;

        if (data.verbatim_runs && data.verbatim_runs.length > 0) {
          html += `<div style="font-size:0.8rem; color:#b91c1c;"><strong>⚠️ Verbatim Runs Flagged:</strong> ${data.verbatim_runs.map(v => `<code>"${v}"</code>`).join(", ")}</div>`;
        }
        html += `</div>`;
        resultsBox.innerHTML = html;
        showToast("Paraphrase audit complete!");
      } catch (err) {
        console.error(err);
        resultsBox.innerHTML = "<p style='color:red;'>Error running paraphrase audit.</p>";
      }
    });
  }
}

// Funnel Mad-Libs & Narrative Preview (Step 4)
function initFunnelMadLibs() {
  document.querySelectorAll(".btn-insert-template").forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-target");
      const template = btn.getAttribute("data-template");
      const targetEl = document.getElementById(targetId);
      if (targetEl) {
        targetEl.value = template;
        targetEl.dispatchEvent(new Event("input"));
        showToast("Formal sentence frame inserted.");
      }
    });
  });

  const btnPreview = document.getElementById("btn-assemble-background");
  if (btnPreview) {
    btnPreview.addEventListener("click", () => {
      const t1 = projectState.funnel.tier1.trim();
      const t2 = projectState.funnel.tier2.trim();
      const t3 = projectState.funnel.tier3.trim();
      const t4 = projectState.funnel.tier4.trim();
      const previewBox = document.getElementById("assembled-background-preview");
      if (previewBox) {
        previewBox.style.display = "block";
        previewBox.innerText = [t1, t2, t3, t4].filter(Boolean).join("\n\n") || "Fill in the 4 tiers above to view the synthesized background narrative.";
      }
    });
  }

  const btnCritiqueBg = document.getElementById("btn-critique-background");
  if (btnCritiqueBg) {
    btnCritiqueBg.addEventListener("click", async () => {
      const bgText = [projectState.funnel.tier1, projectState.funnel.tier2, projectState.funnel.tier3, projectState.funnel.tier4].join(" ");
      await runSocraticCritique("Background", bgText, "socratic-bg-results");
    });
  }
}

// Flowchart Diagram Generator (Native Scientific Vector Diagram - Step 4)
function initDiagramGenerator() {
  const btn = document.getElementById("btn-generate-diagram");
  if (!btn) return;

  const renderWorkflowDiagram = () => {
    const tool = projectState.tool || "Engineered Construct";
    const system = projectState.chassis || projectState.system || "Host Chassis / Matrix";
    const aim1 = (projectState.aims && projectState.aims.aim1) ? projectState.aims.aim1.slice(0, 42) : "In Silico Design & Mutation Modeling";
    const aim2 = (projectState.aims && projectState.aims.aim2) ? projectState.aims.aim2.slice(0, 42) : "Recombinant Screening & Kinetic Assays";
    const aim3 = (projectState.aims && projectState.aims.aim3) ? projectState.aims.aim3.slice(0, 42) : "Functional Validation & Translation";
    const metric = (projectState.matrix && projectState.matrix.blue) ? projectState.matrix.blue.slice(0, 36) : "Validated Milestone Benchmark";

    const phases = [
      { tag: "Phase 1", name: "Construct Design", detail: tool, icon: "🧬", color: "#4f46e5", bg: "#eef2ff", border: "#c7d2fe" },
      { tag: "Phase 2", name: "Host System", detail: system, icon: "🧫", color: "#0891b2", bg: "#ecfeff", border: "#a5f3fc" },
      { tag: "Phase 3", name: "Work Package 1", detail: aim1, icon: "🔬", color: "#059669", bg: "#ecfdf5", border: "#a7f3d0" },
      { tag: "Phase 4", name: "Work Package 2", detail: aim2, icon: "⚙️", color: "#d97706", bg: "#fffbeb", border: "#fde68a" },
      { tag: "Phase 5", name: "Milestone Metric", detail: metric, icon: "🎯", color: "#7c3aed", bg: "#f5f3ff", border: "#ddd6fe" }
    ];

    const viewport = document.getElementById("diagram-viewport");
    if (viewport) {
      viewport.innerHTML = `
        <div style="display: flex; align-items: stretch; justify-content: center; flex-wrap: wrap; gap: 8px; padding: 12px 6px;">
          ${phases.map((p, i) => `
            <div style="display: flex; align-items: center; gap: 8px;">
              <div style="background: ${p.bg}; border: 1.5px solid ${p.border}; border-radius: 8px; padding: 12px 14px; min-width: 150px; max-width: 175px; text-align: left; box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: transform 0.2s;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                  <span style="font-size: 0.7rem; font-weight: 800; color: ${p.color}; text-transform: uppercase; letter-spacing: 0.5px;">${p.tag}</span>
                  <span style="font-size: 1rem;">${p.icon}</span>
                </div>
                <div style="font-size: 0.82rem; font-weight: 700; color: #1e293b; margin-bottom: 3px;">${escapeHtml(p.name)}</div>
                <div style="font-size: 0.72rem; color: #64748b; line-height: 1.35; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">${escapeHtml(p.detail)}</div>
              </div>
              ${i < phases.length - 1 ? `<div style="color: #94a3b8; font-size: 1.2rem; font-weight: 800; user-select: none;">➔</div>` : ""}
            </div>
          `).join("")}
        </div>
      `;
    }
  };

  btn.addEventListener("click", () => {
    renderWorkflowDiagram();
    showToast("Experimental workflow flowchart generated!");
  });

  // Automatically render initial workflow state
  renderWorkflowDiagram();
}

// Tabulated Budget Calculator (Step 5)
function initBudgetCalculator() {
  const inputs = document.querySelectorAll(".budget-input-calc");
  const updateBudget = () => {
    const cons = parseFloat(document.getElementById("budget-consumables")?.value || 0);
    const pers = parseFloat(document.getElementById("budget-personnel")?.value || 0);
    const util = parseFloat(document.getElementById("budget-utilities")?.value || 0);
    const equip = parseFloat(document.getElementById("budget-equipment")?.value || 0);

    const total = cons + pers + util + equip;
    const totalDisplay = document.getElementById("budget-total-display");
    const breakdownDisplay = document.getElementById("budget-breakdown-display");

    if (totalDisplay) totalDisplay.innerText = `$${total.toLocaleString()}`;
    if (breakdownDisplay && total > 0) {
      const pC = Math.round((cons / total) * 100);
      const pP = Math.round((pers / total) * 100);
      const pU = Math.round((util / total) * 100);
      const pE = Math.round((equip / total) * 100);
      breakdownDisplay.innerText = `Consumables: ${pC}% | Personnel: ${pP}% | Overhead: ${pU}% | Equipment: ${pE}%`;
    }

    projectState.budget_items = {
      consumables: cons,
      personnel: pers,
      utilities: util,
      equipment: equip
    };

    const budgetSummary = `1. Consumables & Reagents: $${cons.toLocaleString()}\n2. Personnel Incentives: $${pers.toLocaleString()}\n3. Utilities & Overhead: $${util.toLocaleString()}\n4. Specialized Equipment: $${equip.toLocaleString()}\nTotal Budget: $${total.toLocaleString()}`;
    projectState.budget = budgetSummary;
    const notesEl = document.getElementById("budget-input");
    if (notesEl && !notesEl.value.includes("Consumables")) {
      notesEl.value = budgetSummary + (notesEl.value ? "\n\nJustification:\n" + notesEl.value : "");
    }
    saveToStorage();
    if (typeof activeFigure !== "undefined" && activeFigure === "donut") {
      renderActiveVisualFigure();
    }
  };

  inputs.forEach(inp => inp.addEventListener("input", updateBudget));
  updateBudget();
}

// Impact, Gap Taxonomy, Novelty & Competitor Analysis Suite
function initImpactAndNoveltySuite() {
  // Gap Taxonomy Card clicks
  const gapCards = document.querySelectorAll(".gap-taxonomy-card");
  const gapGuidance = document.getElementById("gap-guidance-box");
  const gapGuidanceMap = {
    mechanistic: "<strong>Mechanistic Gap Guidance:</strong> State the unresolved structural or biophysical phenomenon. <em>Example: 'While wild-type PETase cleaves ester bonds, the structural mechanism governing acid-induced denaturation at pH < 5.0 remains unresolved.'</em>",
    performance: "<strong>Performance Ceiling Gap Guidance:</strong> State the physical or catalytic threshold. <em>Example: 'Industrial adoption is critically constrained by enzyme thermolability (Tm < 48°C), which causes active-site unfolding within 12 hours.'</em>",
    methodological: "<strong>Methodological Deployability Gap Guidance:</strong> Contrast current laboratory bottlenecks. <em>Example: 'Standard broth microdilution requires 24–48 hours, delaying clinical interventions during acute bacteremia and septic episodes.'</em>",
    matrix: "<strong>Environmental / Matrix Gap Guidance:</strong> Contrast buffer vs real-world inhibitor matrix. <em>Example: 'Although Cas12a operates robustly in synthetic buffer, humic acids and heavy metals in industrial effluent inhibit Cas12a collateral cleavage by >85%.'</em>",
    translational: "<strong>Bioreactor Scale-Up Gap Guidance:</strong> Address mass transfer or metabolic burden at scale. <em>Example: 'High plasmid copy numbers impose severe metabolic burden, precipitating plasmid loss and a 70% drop in recombinant yield during fed-batch fermentation.'</em>"
  };

  gapCards.forEach(card => {
    card.addEventListener("click", () => {
      gapCards.forEach(c => c.classList.remove("selected"));
      card.classList.add("selected");
      const gapKey = card.getAttribute("data-gap");
      if (gapGuidance && gapGuidanceMap[gapKey]) {
        gapGuidance.innerHTML = gapGuidanceMap[gapKey];
      }
    });
  });

  // Gap Audit Button
  const btnAuditGap = document.getElementById("btn-audit-gap");
  const gapResultsBox = document.getElementById("gap-audit-results-box");
  if (btnAuditGap && gapResultsBox) {
    btnAuditGap.addEventListener("click", async () => {
      const gapText = projectState.funnel.tier3.trim();
      if (!gapText) {
        showToast("Please write a draft in Tier 3 (The Knowledge Gap) first.");
        return;
      }
      gapResultsBox.style.display = "block";
      gapResultsBox.innerHTML = "<p><em>Auditing gap phrasing and taxonomy classification...</em></p>";
      try {
        const resp = await fetch("/api/impact/gap_audit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ gap_text: gapText })
        });
        const data = await resp.json();
        let badgeColor = data.passed ? "#16a34a" : "#dc2626";
        let html = `
          <div style="background: white; border: 1px solid #bfdbfe; border-radius: 8px; padding: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <strong>${data.gap_title}</strong>
              <span style="background: ${badgeColor}; color: white; font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 4px;">
                Score: ${data.score} / 5.0 Marks
              </span>
            </div>
            <p style="font-size: 0.82rem; color: #1e293b; margin-bottom: 6px;">${data.feedback}</p>
        `;
        if (data.issues && data.issues.length > 0) {
          html += `<ul style="font-size: 0.78rem; color: #b91c1c; margin: 0; padding-left: 18px;">${data.issues.map(i => `<li>${i}</li>`).join("")}</ul>`;
        }
        if (data.recommendations && data.recommendations.length > 0) {
          html += `<div style="font-size: 0.78rem; color: #15803d; margin-top: 6px;"><strong>💡 Recommendation:</strong> ${data.recommendations[0]}</div>`;
        }
        html += `</div>`;
        gapResultsBox.innerHTML = html;
        showToast("Gap analysis complete!");
      } catch (err) {
        console.error(err);
        gapResultsBox.innerHTML = "<p style='color:red;'>Error running gap audit.</p>";
      }
    });
  }

  // Novelty & Soundness Auditor (Host-Swap Trap Detector)
  const btnAuditNovelty = document.getElementById("btn-audit-novelty");
  if (btnAuditNovelty && gapResultsBox) {
    btnAuditNovelty.addEventListener("click", async () => {
      gapResultsBox.style.display = "block";
      gapResultsBox.innerHTML = "<p><em>Auditing novelty, inventive leap, and experimental controls...</em></p>";
      try {
        const resp = await fetch("/api/impact/novelty_audit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title: projectState.title,
            chassis: projectState.system || projectState.chassis,
            tool: projectState.tool,
            target: projectState.target,
            hypothesis: projectState.funnel.tier4,
            methodology: projectState.methodology
          })
        });
        const data = await resp.json();
        let badgeColor = data.soundness_score >= 75 ? "#16a34a" : (data.soundness_score >= 50 ? "#d97706" : "#dc2626");
        let html = `
          <div style="background: white; border: 1px solid #bfdbfe; border-radius: 8px; padding: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <strong>${data.verdict}</strong>
              <span style="background: ${badgeColor}; color: white; font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 4px;">
                Soundness: ${data.soundness_score} / 100
              </span>
            </div>
        `;
        if (data.is_host_swap_trap) {
          html += `<div style="background: #fef2f2; border: 1px solid #fca5a5; color: #991b1b; padding: 8px; border-radius: 4px; font-size: 0.8rem; margin-bottom: 8px;">
            ⚠️ <strong>Host-Swap Trap Warning:</strong> Merely moving a known tool into another host without an explicit molecular modification (e.g. rational mutation, catalytic fusion, or promoter engineering) represents an incremental student exercise rather than fundable grant novelty.
          </div>`;
        }
        if (data.issues && data.issues.length > 0) {
          html += `<ul style="font-size: 0.78rem; color: #b91c1c; margin: 0; padding-left: 18px;">${data.issues.map(i => `<li>${i}</li>`).join("")}</ul>`;
        }
        if (data.strengths && data.strengths.length > 0) {
          html += `<ul style="font-size: 0.78rem; color: #15803d; margin-top: 6px; padding-left: 18px;">${data.strengths.map(s => `<li>${s}</li>`).join("")}</ul>`;
        }
        html += `</div>`;
        gapResultsBox.innerHTML = html;
        showToast("Novelty & Soundness audit complete!");
      } catch (err) {
        console.error(err);
        gapResultsBox.innerHTML = "<p style='color:red;'>Error auditing novelty.</p>";
      }
    });
  }

  // Search for Significance Queries
  const btnSearchSig = document.getElementById("btn-search-significance");
  const sigResultsBox = document.getElementById("significance-search-results-box");
  if (btnSearchSig && sigResultsBox) {
    btnSearchSig.addEventListener("click", async () => {
      sigResultsBox.style.display = "block";
      sigResultsBox.innerHTML = "<p><em>Generating epidemiological & economic burden queries...</em></p>";
      try {
        const resp = await fetch("/api/impact/significance_search", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            chassis: projectState.system || projectState.chassis,
            tool: projectState.tool,
            target: projectState.target,
            modality: projectState.model_id
          })
        });
        const data = await resp.json();
        let html = `
          <div style="background: white; border: 1px solid #a7f3d0; border-radius: 8px; padding: 12px;">
            <div style="font-weight: 700; color: #065f46; font-size: 0.85rem; margin-bottom: 6px;">
              🔍 Clickable Significance & Burden Searches:
            </div>
            <p style="font-size: 0.78rem; color: #047857; margin-bottom: 10px;">${data.guidance}</p>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <a href="${data.links.pubmed_burden}" target="_blank" class="btn-direct-link" style="background-color: #059669; font-size: 0.78rem;">
                🏥 PubMed Health Burden (DALYs/Mortality)
              </a>
              <a href="${data.links.google_market}" target="_blank" class="btn-direct-link" style="background-color: #0284c7; font-size: 0.78rem;">
                📊 Google Market Size & CAGR ($ Millions)
              </a>
              <a href="${data.links.global_orgs}" target="_blank" class="btn-direct-link" style="background-color: #4f46e5; font-size: 0.78rem;">
                🌐 WHO / FAO / World Bank Statistics
              </a>
            </div>
          </div>
        `;
        sigResultsBox.innerHTML = html;
        showToast("Significance queries ready!");
      } catch (err) {
        console.error(err);
        sigResultsBox.innerHTML = "<p style='color:red;'>Error generating significance queries.</p>";
      }
    });
  }

  // USP Template Inserter
  const btnUspTpl = document.getElementById("btn-insert-usp-template");
  if (btnUspTpl) {
    btnUspTpl.addEventListener("click", () => {
      const tool = projectState.tool.trim() || "engineered biocatalytic platform";
      const incumbent = (projectState.competitor_data && projectState.competitor_data.incumbent_name.trim()) || "conventional commercial benchmark systems";
      const template = `Unlike ${incumbent} which suffer from high operational costs and slow turnaround times, our ${tool} achieves a 4-fold increase in reaction throughput under ambient temperature, thereby reducing downstream capital expenditure by 60% and enabling decentralized deployment.`;
      const uspEl = document.getElementById("usps-input");
      if (uspEl) {
        uspEl.value = template;
        uspEl.dispatchEvent(new Event("input"));
        showToast("Proven USP formula inserted.");
      }
    });
  }

  // Audit USP Button
  const btnAuditUsp = document.getElementById("btn-audit-usp");
  const uspResultsBox = document.getElementById("usp-audit-results-box");
  if (btnAuditUsp && uspResultsBox) {
    btnAuditUsp.addEventListener("click", async () => {
      const uspText = projectState.usps.trim();
      if (!uspText) {
        showToast("Please enter a USP statement first.");
        return;
      }
      uspResultsBox.style.display = "block";
      uspResultsBox.innerHTML = "<p><em>Auditing competitive advantage and checking for strawman competitors...</em></p>";
      try {
        const resp = await fetch("/api/impact/competitor_audit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            competitor_data: projectState.competitor_data,
            usp_text: uspText
          })
        });
        const data = await resp.json();
        let badgeColor = data.passed ? "#16a34a" : "#dc2626";
        let html = `
          <div style="background: white; border: 1px solid #c7d2fe; border-radius: 8px; padding: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <strong>Competitive Advantage & USP Audit</strong>
              <span style="background: ${badgeColor}; color: white; font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 4px;">
                Score: ${data.score} / 5.0 Marks
              </span>
            </div>
            <p style="font-size: 0.82rem; color: #1e293b; margin-bottom: 6px;">${data.feedback}</p>
        `;
        if (data.issues && data.issues.length > 0) {
          html += `<ul style="font-size: 0.78rem; color: #b91c1c; margin: 0; padding-left: 18px;">${data.issues.map(i => `<li>${i}</li>`).join("")}</ul>`;
        }
        if (data.strengths && data.strengths.length > 0) {
          html += `<ul style="font-size: 0.78rem; color: #15803d; margin-top: 6px; padding-left: 18px;">${data.strengths.map(s => `<li>${s}</li>`).join("")}</ul>`;
        }
        html += `</div>`;
        uspResultsBox.innerHTML = html;
        showToast("USP audit complete!");
      } catch (err) {
        console.error(err);
        uspResultsBox.innerHTML = "<p style='color:red;'>Error auditing USP.</p>";
      }
    });
  }
}

// 10-Node Research Logic Chain Controller
function initLogicChainTrack() {
  const nodes = document.querySelectorAll(".chain-node");
  nodes.forEach(node => {
    node.addEventListener("click", () => {
      const step = parseInt(node.getAttribute("data-target-step"));
      const targetId = node.getAttribute("data-target-id");
      if (step) goToStep(step);
      if (targetId) {
        setTimeout(() => {
          const el = document.getElementById(targetId);
          if (el) {
            el.scrollIntoView({ behavior: "smooth", block: "center" });
            el.focus();
            el.style.transition = "box-shadow 0.3s ease";
            el.style.boxShadow = "0 0 0 3px rgba(37, 99, 235, 0.4)";
            setTimeout(() => { el.style.boxShadow = ""; }, 1800);
          }
        }, 150);
      }
    });
  });
}

let logicChainDebounceTimer = null;
function updateLogicChainUIDebounced() {
  clearTimeout(logicChainDebounceTimer);
  logicChainDebounceTimer = setTimeout(updateLogicChainUI, 500);
}

async function updateLogicChainUI() {
  try {
    const resp = await fetch("/api/impact/chain_check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(projectState)
    });
    const data = await resp.json();

    const healthBadge = document.getElementById("chain-health-badge");
    if (healthBadge) {
      healthBadge.innerText = `Health: ${data.chain_health_pct}% Complete (${data.filled_nodes}/10)`;
      if (data.chain_health_pct >= 80) {
        healthBadge.className = "chain-badge good";
      } else {
        healthBadge.className = "chain-badge";
      }
    }

    if (data.nodes) {
      data.nodes.forEach(n => {
        const nodeEl = document.getElementById(`node-${n.id}`);
        if (nodeEl) {
          if (n.filled) nodeEl.classList.add("filled");
          else nodeEl.classList.remove("filled");
        }
      });
    }

    const warningsBox = document.getElementById("chain-warnings-box");
    if (warningsBox) {
      if (data.warnings && data.warnings.length > 0) {
        warningsBox.style.display = "block";
        warningsBox.innerHTML = `<strong>⚠️ Narrative Coherence Notice:</strong> ${data.warnings.join(" ")}`;
      } else {
        warningsBox.style.display = "none";
      }
    }
  } catch (err) {
    // Non-blocking background sync
  }
}

// Reference Recency Auditor (Step 6)
function initRefRecencyAuditor() {
  const btn = document.getElementById("btn-audit-refs-recency");
  if (!btn) return;
  btn.addEventListener("click", async () => {
    const text = document.getElementById("references-input").value.trim();
    const box = document.getElementById("references-recency-box");
    if (!text) {
      showToast("Please enter references first.");
      return;
    }
    try {
      const resp = await fetch("/api/reference/audit_recency", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ references: text })
      });
      const data = await resp.json();
      const color = data.passed_rubric ? "#059669" : "#dc2626";
      box.innerHTML = `
        <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:6px; padding:10px; font-size:0.85rem;">
          <strong style="color:${color};">${data.feedback}</strong>
          <div style="margin-top:4px; color:#475569;">Total Citations Analyzed: ${data.total_count} (Recent: ${data.recent_count})</div>
        </div>
      `;
      showToast("Recency check complete!");
    } catch (err) {
      console.error(err);
    }
  });
}

// Socratic Critique API Call
async function runSocraticCritique(section, text, containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = "<p><em>Analyzing scientific logic and rubric compliance...</em></p>";
  try {
    const resp = await fetch("/api/socratic/critique", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ section, text, context: projectState })
    });
    const result = await resp.json();

    if (result.status === "refusal") {
      container.innerHTML = `<div class="socratic-alert" style="background:#fee2e2; border-color:#fca5a5; color:#991b1b;"><strong>${result.message}</strong></div>`;
      return;
    }

    let html = "";
    if (result.praise && result.praise.length > 0) html += `<div style="color:#065f46; font-size:0.85rem; margin-bottom:8px;"><strong>✅ Strengths:</strong> ${result.praise.join(" ")}</div>`;
    if (result.critiques && result.critiques.length > 0) html += `<div style="color:#9a3412; font-size:0.85rem; margin-bottom:8px;"><strong>⚠️ Flaws Flagged:</strong> ${result.critiques.join(" ")}</div>`;
    if (result.socratic_questions && result.socratic_questions.length > 0) {
      html += `<div class="socratic-title">🤔 Socratic Counter-Questions:</div>`;
      result.socratic_questions.forEach(q => html += `<div class="socratic-question-item"><strong>Mentor Query:</strong> ${q}</div>`);
    }
    container.innerHTML = html;
  } catch (e) {
    console.error(e);
    container.innerHTML = "<p style='color:red;'>Could not connect to Socratic engine.</p>";
  }
}

// Step 6: Full Writing Audit & Viva Voce
function initAuditAndViva() {
  const btnWritingAudit = document.getElementById("btn-run-full-writing-audit");
  if (btnWritingAudit) btnWritingAudit.addEventListener("click", async () => await runWritingAudit());

  const btnAudit = document.getElementById("btn-audit-full");
  if (btnAudit) btnAudit.addEventListener("click", async () => await runWritingAudit());

  const btnViva = document.getElementById("btn-generate-viva");
  if (btnViva) {
    btnViva.addEventListener("click", async () => {
      try {
        btnViva.innerText = "Simulating Study Section Review...";
        const resp = await fetch("/api/viva/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(projectState)
        });
        const data = await resp.json();
        renderVivaQuestions(data.questions);
        showToast("Viva Voce defense questions generated!");
      } catch (e) {
        console.error(e);
        showToast("Error generating viva questions.");
      } finally {
        btnViva.innerText = "🎙️ Simulate Viva Voce Review";
      }
    });
  }
}

async function runWritingAudit() {
  const container = document.getElementById("full-writing-audit-container") || document.getElementById("full-audit-container");
  if (!container) return;

  container.innerHTML = "<p style='color:#4f46e5; font-weight:600;'><em>🔍 Auditing all 9 proposal written sections for scientific rigor, future tense compliance, and citation recency...</em></p>";
  try {
    const resp = await fetch("/api/writing/audit_all", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(projectState)
    });
    const result = await resp.json();
    renderWritingAuditReport(result);
    showToast("Full Writing Audit complete!");
  } catch (e) {
    console.error(e);
    container.innerHTML = "<p style='color:red;'>Error running writing audit.</p>";
  }
}

function renderWritingAuditReport(data) {
  const container = document.getElementById("full-writing-audit-container") || document.getElementById("full-audit-container");
  if (!container) return;

  const s = data.summary;
  let summaryBg = "#f0fdf4";
  let summaryBorder = "#86efac";
  let summaryColor = "#166534";

  if (s.overall_status === "Revisions Recommended") {
    summaryBg = "#eff6ff";
    summaryBorder = "#93c5fd";
    summaryColor = "#1e40af";
  } else if (s.overall_status === "Draft in Progress") {
    summaryBg = "#fffbeb";
    summaryBorder = "#fde68a";
    summaryColor = "#92400e";
  }

  let html = `
    <div style="background: ${summaryBg}; border: 1px solid ${summaryBorder}; border-radius: 10px; padding: 16px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
      <div>
        <div style="font-size: 0.75rem; font-weight: 800; color: ${summaryColor}; text-transform: uppercase;">Writing Health Standing</div>
        <div style="font-size: 1.5rem; font-weight: 800; color: ${summaryColor};">${s.overall_status}</div>
      </div>
      <div style="display: flex; gap: 12px; font-size: 0.85rem;">
        <div style="background: white; padding: 8px 14px; border-radius: 6px; border: 1px solid ${summaryBorder};">
          <strong style="color: #16a34a;">${s.passed_sections}</strong> / ${s.total_sections} Passed
        </div>
        <div style="background: white; padding: 8px 14px; border-radius: 6px; border: 1px solid ${summaryBorder};">
          <strong style="color: #d97706;">${s.warning_sections}</strong> Need Polish
        </div>
        <div style="background: white; padding: 8px 14px; border-radius: 6px; border: 1px solid ${summaryBorder};">
          <strong style="color: #dc2626;">${s.incomplete_sections}</strong> Incomplete
        </div>
      </div>
    </div>

    <div style="display: flex; flex-direction: column; gap: 14px;">
  `;

  data.sections.forEach(sec => {
    let cardBorder = "#e2e8f0";
    let badgeBg = "#f1f5f9";
    let badgeColor = "#475569";
    if (sec.status === "pass") {
      cardBorder = "#bbf7d0";
      badgeBg = "#dcfce7";
      badgeColor = "#166534";
    } else if (sec.status === "warning") {
      cardBorder = "#fef08a";
      badgeBg = "#fef9c3";
      badgeColor = "#854d0e";
    } else {
      cardBorder = "#fecaca";
      badgeBg = "#fee2e2";
      badgeColor = "#991b1b";
    }

    html += `
      <div style="background: white; border: 1px solid ${cardBorder}; border-radius: 8px; padding: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <strong style="color: #1e293b; font-size: 0.95rem;">${sec.name}</strong>
          <span style="font-size: 0.75rem; font-weight: 700; background: ${badgeBg}; color: ${badgeColor}; padding: 3px 8px; border-radius: 9999px;">${sec.badge}</span>
        </div>
        <div style="font-size: 0.8rem; color: #64748b; font-style: italic; background: #f8fafc; padding: 6px 10px; border-radius: 6px; margin-bottom: 8px;">"${sec.excerpt}"</div>
    `;

    if (sec.strengths && sec.strengths.length > 0) {
      html += `<div style="font-size: 0.82rem; color: #15803d; margin-bottom: 4px;"><strong>✅ Strengths:</strong> ${sec.strengths.join(" • ")}</div>`;
    }

    if (sec.issues && sec.issues.length > 0) {
      html += `<div style="font-size: 0.82rem; color: #b91c1c; margin-bottom: 4px;"><strong>⚠️ Review Points:</strong> ${sec.issues.join(" • ")}</div>`;
    }

    if (sec.action_recommendation) {
      html += `<div style="font-size: 0.8rem; color: #4338ca; background: #eef2ff; padding: 6px 10px; border-radius: 6px; margin-top: 6px;"><strong>💡 Action:</strong> ${sec.action_recommendation}</div>`;
    }

    html += `</div>`;
  });

  html += `</div>`;
  container.innerHTML = html;
}

async function runFullAudit() {
  await runWritingAudit();
}

function renderAuditScorecard(audit) {
  const container = document.getElementById("full-audit-container");
  if (!container) return;
  const b = audit.breakdown;
  let html = `
    <div style="background:#f1f5f9; border-radius:10px; padding:16px; margin-bottom:16px; display:flex; justify-content:space-between; align-items:center;">
      <div>
        <span style="font-size:0.75rem; font-weight:800; color:#64748b; text-transform:uppercase;">Estimated BT_301 Grade</span>
        <div style="font-size:1.8rem; font-weight:800; color:#0f172a;">${audit.gpa_score} <span style="font-size:1rem; color:#64748b;">/ 10.0 GPA</span></div>
      </div>
      <div style="text-align:right;">
        <span style="font-size:0.75rem; font-weight:800; color:#64748b; text-transform:uppercase;">Cumulative Raw Marks</span>
        <div style="font-size:1.4rem; font-weight:800; color:#2563eb;">${audit.raw_total} / 85.0</div>
      </div>
    </div>

    <table class="rubric-table">
      <thead>
        <tr>
          <th>Grant Criterion</th>
          <th>Max</th>
          <th>Score</th>
          <th>Diagnostic Feedback</th>
        </tr>
      </thead>
      <tbody>
        <tr><td><strong>Title Formula</strong></td><td>2.0</td><td class="rubric-score-cell">${b.title ? b.title.score : 0}</td><td>${b.title && b.title.report ? b.title.report.feedback : ''}</td></tr>
        <tr><td><strong>Structured Abstract</strong></td><td>5.0</td><td class="rubric-score-cell">${b.abstract ? b.abstract.score : 0}</td><td>${b.abstract && b.abstract.report ? b.abstract.report.feedback : ''}</td></tr>
        <tr><td><strong>Background Funnel & Gap</strong></td><td>20.0</td><td class="rubric-score-cell">${b.background ? b.background.score : 0}</td><td>${b.background && b.background.report ? b.background.report.feedback : ''}</td></tr>
        <tr><td><strong>Specific Objectives</strong></td><td>5.0</td><td class="rubric-score-cell">${b.aims_independence ? b.aims_independence.score : 0}</td><td>${b.aims_independence && b.aims_independence.report ? b.aims_independence.report.feedback : ''}</td></tr>
        <tr><td><strong>Methodology & Controls</strong></td><td>15.0</td><td class="rubric-score-cell">${b.methodology ? b.methodology.score : 0}</td><td>${b.methodology && b.methodology.report ? b.methodology.report.feedback : ''}</td></tr>
        <tr><td><strong>Outcomes & Long-Term Impact (Sec. 10)</strong></td><td>10.0</td><td class="rubric-score-cell">${b.expected_outcomes ? b.expected_outcomes.score : 0}</td><td>${b.expected_outcomes && b.expected_outcomes.impact_included ? '✅ Includes long-term significance and deliverable targets.' : '⚠️ Detail Section 10 Impact: Why do the results matter?'}</td></tr>
        <tr><td><strong>Competitive Advantage & USPs</strong></td><td>5.0</td><td class="rubric-score-cell">${b.competitive_advantage ? b.competitive_advantage.score : 0}</td><td>${b.competitive_advantage && b.competitive_advantage.report ? b.competitive_advantage.report.feedback : ''}</td></tr>
        <tr><td><strong>Biotech SWOT & PESTEL</strong></td><td>10.0</td><td class="rubric-score-cell">${b.swot_pestel ? b.swot_pestel.score : 0}</td><td>${b.swot_pestel && b.swot_pestel.report ? b.swot_pestel.report.feedback : ''}</td></tr>
        <tr><td><strong>Gantt Timeline & Decision Gates</strong></td><td>5.0</td><td class="rubric-score-cell">${b.time_plan ? b.time_plan.score : 0}</td><td>Work packages scheduled with Go/No-Go decision milestones.</td></tr>
        <tr><td><strong>Tabulated Budget</strong></td><td>5.0</td><td class="rubric-score-cell">${b.budget ? b.budget.score : 0}</td><td>Itemized across 4 core grant funding categories.</td></tr>
        <tr><td><strong>References (60% Recency)</strong></td><td>5.0</td><td class="rubric-score-cell">${b.references ? b.references.score : 0}</td><td>Peer-reviewed citations satisfying recency standards.</td></tr>
      </tbody>
    </table>

    ${b.novelty_soundness && b.novelty_soundness.report ? `
      <div style="margin-top:14px; background:#f0fdf4; border:1px solid #86efac; border-radius:8px; padding:12px;">
        <div style="font-weight:700; color:#166534; margin-bottom:4px;">🔬 Scientific Soundness & Novelty Audit: ${b.novelty_soundness.score} / 100</div>
        <div style="font-size:0.82rem; color:#15803d;"><strong>Status:</strong> ${b.novelty_soundness.report.verdict}</div>
        ${b.novelty_soundness.report.issues && b.novelty_soundness.report.issues.length > 0 ? `
          <ul style="font-size:0.78rem; color:#b91c1c; margin:4px 0; padding-left:18px;">${b.novelty_soundness.report.issues.map(i => `<li>${i}</li>`).join('')}</ul>
        ` : ''}
      </div>
    ` : ''}
  `;
  container.innerHTML = html;
}

function renderVivaQuestions(questions) {
  const container = document.getElementById("viva-results-container");
  if (!container) return;
  let html = "";
  questions.forEach(q => {
    html += `
      <div class="viva-box">
        <div style="font-size:0.75rem; font-weight:800; color:#a21caf; text-transform:uppercase; margin-bottom:4px;">${q.category}</div>
        <div class="viva-question">"${q.question}"</div>
        <div class="viva-hint"><strong>Study Section Benchmark:</strong> ${q.eval_criteria}</div>
      </div>
    `;
  });
  container.innerHTML = html;
}

// Faculty Studio Mode (Comment Bank)
function initInstructorStudio() {
  const btnToggle = document.getElementById("btn-toggle-instructor");
  const panel = document.getElementById("instructor-studio-panel");
  if (btnToggle && panel) {
    btnToggle.addEventListener("click", async () => {
      panel.style.display = panel.style.display === "none" ? "block" : "none";
      btnToggle.innerText = panel.style.display === "none" ? "👨‍🏫 Faculty View" : "👨‍🏫 Exit Faculty View";
      if (panel.style.display === "block") {
        await loadCommentBankChips();
        panel.scrollIntoView({ behavior: "smooth" });
      }
    });
  }

  const btnGenMemo = document.getElementById("btn-generate-instructor-memo");
  if (btnGenMemo) {
    btnGenMemo.addEventListener("click", async () => {
      const manual = document.getElementById("instructor-manual-notes").value;
      const memoOutput = document.getElementById("instructor-memo-output");
      try {
        const resp = await fetch("/api/instructor/report", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            student_data: projectState,
            codes: Array.from(selectedCommentCodes),
            manual_comments: manual
          })
        });
        const data = await resp.json();
        memoOutput.style.display = "block";
        memoOutput.innerText = data.memo_text;
        showToast("Faculty Evaluation Memo generated!");
      } catch (err) {
        console.error(err);
      }
    });
  }
}

async function loadCommentBankChips() {
  const container = document.getElementById("instructor-comment-bank-chips");
  if (!container || container.children.length > 0) return;
  try {
    const resp = await fetch("/api/instructor/comments");
    const bank = await resp.json();
    let html = "";
    for (const cat in bank) {
      bank[cat].forEach(item => {
        html += `<button class="instructor-chip" data-code="${item.code}">[${item.code}] ${item.label}</button>`;
      });
    }
    container.innerHTML = html;
    container.querySelectorAll(".instructor-chip").forEach(chip => {
      chip.addEventListener("click", () => {
        const code = chip.getAttribute("data-code");
        if (selectedCommentCodes.has(code)) {
          selectedCommentCodes.delete(code);
          chip.classList.remove("selected");
        } else {
          selectedCommentCodes.add(code);
          chip.classList.add("selected");
        }
      });
    });
  } catch (err) {
    console.error(err);
  }
}

function updateWordCount(id, text, limit) {
  const el = document.getElementById(id);
  if (!el) return;
  const count = text.trim() ? text.trim().split(/\s+/).length : 0;
  el.innerText = `${count} / ${limit} words`;
  el.style.color = count > limit ? "#dc2626" : "#64748b";
}

function checkTenseWarning(text) {
  const alertEl = document.getElementById("tense-warning");
  if (!alertEl) return;
  const pastMatches = text.match(/\b(was incubated|were inoculated|was performed|were collected|was added|were analyzed)\b/gi);
  if (pastMatches && pastMatches.length > 0) {
    alertEl.style.display = "block";
    alertEl.innerHTML = `⚠️ <strong>Tense Alert (Rubric Item 11)</strong>: Found past-tense phrase "<em>${pastMatches[0]}</em>". Grant methodology must be in FUTURE TENSE ("will be incubated", "will be analyzed").`;
  } else {
    alertEl.style.display = "none";
  }
}

function checkClicheWarning(text) {
  const alertEl = document.getElementById("cliche-warning");
  if (!alertEl) return;
  const cliches = ["we are students", "lack of experience", "not enough time", "budget might run out", "beginners"];
  const lower = text.toLowerCase();
  const found = cliches.find(c => lower.includes(c));
  if (found) {
    alertEl.style.display = "block";
    alertEl.innerHTML = `⚠️ <strong>Reviewer Trap</strong>: Avoid student cliché "<em>${found}</em>". Focus on biochemical or technical failure modes.`;
  } else {
    alertEl.style.display = "none";
  }
}

let scoreTimeout = null;
function updateLiveScoreDebounced() {
  clearTimeout(scoreTimeout);
  scoreTimeout = setTimeout(updateLiveScore, 600);
}

async function updateLiveScore() {
    renderLiveManuscript();
    renderActiveVisualFigure();

  try {
    const resp = await fetch("/api/audit/full", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(projectState)
    });
    const audit = await resp.json();
    updateHeaderScores(audit.raw_total, audit.gpa_score, audit);
  } catch (e) {}
}

function updateHeaderScores(raw, gpa, audit) {
  // 1. Calculate milestone completion nodes (0 to 10)
  let nodes = 0;
  if (projectState.title && (projectState.chassis || projectState.system) && projectState.tool) nodes += 1;
  if (projectState.matrix && (projectState.matrix.blue || projectState.matrix.yellow || projectState.matrix.citation)) nodes += 1;
  if (projectState.funnel && projectState.funnel.tier1 && projectState.funnel.tier2) nodes += 1;
  if (projectState.funnel && projectState.funnel.tier3 && projectState.funnel.tier4) nodes += 1;
  if (projectState.aims && projectState.aims.aim1 && projectState.aims.aim2 && projectState.aims.aim3) nodes += 1;
  if (projectState.methodology && projectState.methodology.length > 30) nodes += 1;
  if (projectState.control_triad && projectState.control_triad.negative && projectState.control_triad.positive) nodes += 1;
  if (projectState.impact || (projectState.expected_outcomes && projectState.expected_outcomes.length > 20)) nodes += 1;
  if (projectState.usps || (projectState.competitor_data && projectState.competitor_data.proposed_name)) nodes += 1;
  if (projectState.swot && projectState.swot.strengths && projectState.swot.weaknesses) nodes += 1;

  const pct = Math.round((nodes / 10.0) * 100);

  // 2. Qualitative Scientific Readiness (STRICT NO-GRADE POLICY)
  let readinessLabel = "🌱 Formulating";
  let readinessColor = "#4338ca";
  if (pct >= 80) {
    readinessLabel = "🌟 Grant-Ready";
    readinessColor = "#16a34a";
  } else if (pct >= 50) {
    readinessLabel = "🌿 Developing";
    readinessColor = "#2563eb";
  }

  // Update top proposal meta card
  const badgeEl = document.getElementById("header-readiness-badge");
  if (badgeEl) {
    badgeEl.innerText = readinessLabel;
    badgeEl.style.color = readinessColor;
  }

  const summaryEl = document.getElementById("header-readiness-summary");
  if (summaryEl) {
    summaryEl.innerText = `Milestones: ${nodes}/10 Complete`;
  }

  // Update Left Sidebar Circular Gauge (Shows percentage completed, NO GRADES)
  const scoreNumEl = document.getElementById("sidebar-readiness-number");
  if (scoreNumEl) scoreNumEl.innerText = `${pct}%`;

  const ringFill = document.getElementById("sidebar-ring-fill");
  if (ringFill) {
    const circumference = 238.76;
    const offset = circumference * (1 - Math.min(100, Math.max(0, pct)) / 100);
    ringFill.style.strokeDashoffset = offset;
  }

  const gaugeBadge = document.getElementById("gauge-status-badge");
  if (gaugeBadge) {
    if (pct >= 80) {
      gaugeBadge.innerText = "Grant-Ready";
      gaugeBadge.style.background = "#dcfce7";
      gaugeBadge.style.color = "#15803d";
    } else if (pct >= 50) {
      gaugeBadge.innerText = "Developing";
      gaugeBadge.style.background = "#e0f2fe";
      gaugeBadge.style.color = "#0369a1";
    } else {
      gaugeBadge.innerText = "Formulating";
      gaugeBadge.style.background = "#fef3c7";
      gaugeBadge.style.color = "#b45309";
    }
  }

  // Update Sidebar Rubric Breakdown Items (Checklist status, NO POINTS)
  const tEl = document.getElementById("score-item-title");
  if (tEl) tEl.innerText = (projectState.title && projectState.tool) ? "✅ Ready" : "Pending";

  const litEl = document.getElementById("score-item-lit");
  if (litEl) litEl.innerText = (projectState.matrix && projectState.matrix.blue) ? "✅ Ready" : "Pending";

  const funEl = document.getElementById("score-item-funnel");
  if (funEl) {
    const fn = projectState.funnel || {};
    const fnCount = [fn.tier1, fn.tier2, fn.tier3, fn.tier4].filter(Boolean).length;
    funEl.innerText = fnCount >= 4 ? "✅ Ready" : (fnCount > 0 ? "⏳ In Progress" : "Pending");
  }

  const aimsEl = document.getElementById("score-item-aims");
  if (aimsEl) {
    const aims = projectState.aims || {};
    const aCount = [aims.aim1, aims.aim2, aims.aim3].filter(Boolean).length;
    const triadCount = (projectState.control_triad && projectState.control_triad.negative) ? 1 : 0;
    aimsEl.innerText = (aCount >= 3 && triadCount) ? "✅ Ready" : (aCount > 0 ? "⏳ In Progress" : "Pending");
  }

  const absEl = document.getElementById("score-item-abs");
  if (absEl) absEl.innerText = (projectState.abstract && projectState.abstract.length > 50) ? "✅ Ready" : "Pending";

  // Trigger Prerequisite & Next Action recalculations
  if (typeof evaluateStepPrerequisites === "function") evaluateStepPrerequisites();
  if (typeof updateNextActionGuidance === "function") updateNextActionGuidance(nodes, pct);
}

// Document & Slide Exporters
function initExportHandlers() {
  const triggerDocx = async () => {
    try {
      showToast("Generating Word document...");
      const resp = await fetch("/api/export/docx", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(projectState)
      });
      const blob = await resp.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `BT301_Proposal_${(projectState.student_name || "Student").replace(/\s+/g, "_")}.docx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      showToast("Word (.docx) downloaded!");
    } catch (e) {
      console.error(e);
      showToast("Error downloading Word file.");
    }
  };

  const triggerPptx = async () => {
    try {
      showToast("Building 16:9 Defense Presentation Deck...");
      const resp = await fetch("/api/export/pptx", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(projectState)
      });
      const blob = await resp.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `Oral_Defense_Slides_${(projectState.student_name || "Student").replace(/\s+/g, "_")}.pptx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      showToast("Oral Defense Slides (.pptx) downloaded!");
    } catch (e) {
      console.error(e);
      showToast("Error downloading slides.");
    }
  };

  const btnDocx = document.getElementById("btn-export-docx");
  if (btnDocx) btnDocx.addEventListener("click", triggerDocx);

  const btnFinalDocx = document.getElementById("btn-final-export-docx");
  if (btnFinalDocx) btnFinalDocx.addEventListener("click", triggerDocx);

  const btnPptx = document.getElementById("btn-export-pptx");
  if (btnPptx) btnPptx.addEventListener("click", triggerPptx);

  const btnFinalPptx = document.getElementById("btn-final-export-pptx");
  if (btnFinalPptx) btnFinalPptx.addEventListener("click", triggerPptx);

  const btnMd = document.getElementById("btn-export-md");
  if (btnMd) {
    btnMd.addEventListener("click", async () => {
      try {
        showToast("Generating Markdown...");
        const resp = await fetch("/api/export/md", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(projectState)
        });
        const blob = await resp.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `BT301_Proposal_${(projectState.student_name || "Student").replace(/\s+/g, "_")}.md`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        showToast("Markdown (.md) downloaded!");
      } catch (e) {
        console.error(e);
        showToast("Error downloading Markdown file.");
      }
    });
  }
}

// ==========================================================================
// Scientific Paper Decoder & Evidence Extractor
// ==========================================================================
function initPaperDecoder() {
  const openBtn = document.getElementById("btn-open-paper-decoder");
  const closeBtn = document.getElementById("btn-close-paper-decoder");
  const modal = document.getElementById("paper-decoder-modal");

  if (openBtn) {
    openBtn.addEventListener("click", () => {
      goToStep(1);
      setTimeout(() => {
        const card = document.getElementById("card-paper-decoder");
        if (card) {
          card.scrollIntoView({ behavior: "smooth", block: "start" });
          const idInp = document.getElementById("paper-id-input");
          if (idInp) idInp.focus();
        }
      }, 120);
    });
  }

  if (closeBtn && modal) {
    closeBtn.addEventListener("click", () => {
      modal.style.display = "none";
    });
  }

  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) modal.style.display = "none";
    });
  }

  // Word counter
  const textInput = document.getElementById("paper-text-input");
  const titleInput = document.getElementById("paper-title-input");
  const idInput = document.getElementById("paper-id-input");
  const wordCountEl = document.getElementById("paper-word-count");

  if (textInput && wordCountEl) {
    textInput.addEventListener("input", () => {
      const words = textInput.value.trim() ? textInput.value.trim().split(/\s+/).length : 0;
      wordCountEl.innerText = `${words} words`;
    });
  }

  // Presets (Section 2 Decoder)
  const presetBtns = document.querySelectorAll(".paper-presets-bar .btn-preset");
  presetBtns.forEach(btn => {
    btn.addEventListener("click", async () => {
      const pKey = btn.getAttribute("data-preset");
      try {
        const resp = await fetch("/api/paper/samples");
        const samples = await resp.json();
        const sample = samples[pKey];
        if (sample) {
          if (titleInput) titleInput.value = sample.title;
          if (textInput) {
            textInput.value = sample.abstract;
            textInput.dispatchEvent(new Event("input"));
          }
          if (idInput) idInput.value = sample.doi;
          showToast(`Loaded: ${sample.title.slice(0, 30)}...`);
          runDecodePaper({
            text: sample.abstract,
            title: sample.title,
            identifier: sample.doi,
            authors: sample.authors,
            year: sample.year,
            journal: sample.journal
          });
        }
      } catch (err) {
        console.error(err);
        showToast("Error loading sample paper.");
      }
    });
  });

  // Helper: Fetch and automatically run decode
  async function triggerFetchAndDecode(rawId) {
    if (!rawId) {
      showToast("Enter a DOI or PubMed ID first.");
      return;
    }
    // Clean identifier client-side
    let cleanId = rawId.trim().replace(/^["'<\(\[{]+|["'>\)\]}]+$/g, "");
    cleanId = cleanId.replace(/^https?:\/\/(?:dx\.)?doi\.org\//i, "");
    cleanId = cleanId.replace(/^https?:\/\/pubmed\.ncbi\.nlm\.nih\.gov\//i, "");
    cleanId = cleanId.replace(/^doi\s*[:=]\s*/i, "");
    cleanId = cleanId.replace(/^pmid\s*[:=]\s*/i, "").replace(/\/+$/, "").trim();

    if (idInput) idInput.value = cleanId;

    if (fetchBtn) {
      fetchBtn.disabled = true;
      fetchBtn.innerText = "Fetching...";
    }
    if (decodeBtn) {
      decodeBtn.disabled = true;
      decodeBtn.innerText = "Fetching & Decoding...";
    }

    try {
      const resp = await fetch("/api/paper/fetch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ identifier: cleanId })
      });
      const data = await resp.json();
      if (data.success) {
        if (titleInput) titleInput.value = data.title;

        // Publisher notice or TLDR banner
        const noticeEl = document.getElementById("paper-fetch-notice");
        if (noticeEl) {
          if (data.publisher_restricted || data.is_tldr) {
            noticeEl.style.display = "block";
            noticeEl.innerHTML = `<strong>ℹ️ Publisher Notice:</strong> ${data.publisher_note || 'The publisher restricts automated API access to the full chapter abstract. Retrieved verified research summary / TLDR.'}`;
          } else {
            noticeEl.style.display = "none";
          }
        }

        if (data.abstract && data.abstract.trim().length > 15) {
          if (textInput) {
            textInput.value = data.abstract;
            textInput.dispatchEvent(new Event("input"));
          }
          showToast("Paper metadata & summary retrieved! Decoding parameters...");
          await runDecodePaper({
            text: data.abstract,
            title: data.title,
            identifier: data.id || cleanId,
            authors: data.authors,
            year: data.year,
            journal: data.journal
          });
        } else {
          showToast(`Paper found: "${data.title.slice(0, 35)}...". Please paste abstract below to decode.`);
          if (textInput) {
            textInput.focus();
            textInput.placeholder = "Paste the abstract text for this paper here to decode it...";
          }
        }
      } else {
        showToast(data.error || "Paper not found. Check the DOI or paste abstract directly.");
      }
    } catch (e) {
      console.error(e);
      showToast("Network error fetching paper.");
    } finally {
      if (fetchBtn) {
        fetchBtn.disabled = false;
        fetchBtn.innerText = "⬇ Fetch Abstract";
      }
      if (decodeBtn) {
        decodeBtn.disabled = false;
        decodeBtn.innerText = "🔍 Decode & Extract Parameters";
      }
    }
  }

  // Fetch DOI/PMID button
  const fetchBtn = document.getElementById("btn-fetch-paper-meta");
  if (fetchBtn) {
    fetchBtn.addEventListener("click", async () => {
      const idVal = (idInput ? idInput.value : "").trim();
      await triggerFetchAndDecode(idVal);
    });
  }

  // Enter key inside DOI/PMID input triggers auto-fetch & decode
  if (idInput) {
    idInput.addEventListener("keydown", async (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        const idVal = idInput.value.trim();
        await triggerFetchAndDecode(idVal);
      }
    });
  }

  // Run Decode button
  const decodeBtn = document.getElementById("btn-run-paper-decode");
  if (decodeBtn) {
    decodeBtn.addEventListener("click", async () => {
      const text = textInput ? textInput.value.trim() : "";
      const title = titleInput ? titleInput.value.trim() : "";
      const identifier = idInput ? idInput.value.trim() : "";

      // If abstract is empty but DOI/identifier is provided, automatically fetch and decode!
      if ((!text || text.split(/\s+/).length < 15) && identifier) {
        await triggerFetchAndDecode(identifier);
        return;
      }

      if (!text || text.split(/\s+/).length < 15) {
        showToast("Enter a DOI above or paste an abstract of at least 15 words.");
        return;
      }
      runDecodePaper({ text, title, identifier });
    });
  }

  // Tab switching
  const tabBtns = document.querySelectorAll(".decoder-tab-btn");
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".decoder-tab-content").forEach(c => c.classList.remove("active"));
      btn.classList.add("active");
      const tabId = btn.getAttribute("data-tab");
      const targetContent = document.getElementById(`tab-content-${tabId}`);
      if (targetContent) targetContent.classList.add("active");
    });
  });

  async function runDecodePaper(payload) {
    const resultsContainer = document.getElementById("paper-results-container");
    if (decodeBtn) {
      decodeBtn.disabled = true;
      decodeBtn.innerText = "Analyzing...";
    }
    try {
      const resp = await fetch("/api/paper/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await resp.json();
      if (data.status === "error") {
        showToast(data.message);
        return;
      }
      currentDecodedData = data;
      renderDecodedResults(data);
      if (resultsContainer) resultsContainer.style.display = "block";
      updateMatrixExplainer(data);
      projectState.decoded_paper_cache = data;
      saveToStorage();
      showToast("Paper deconstructed into proposal evidence!");
    } catch (e) {
      console.error(e);
      showToast("Error analyzing paper.");
    } finally {
      if (decodeBtn) {
        decodeBtn.disabled = false;
        decodeBtn.innerText = "🔍 Decode & Extract Parameters";
      }
    }
  }

  function renderDecodedResults(data) {
    // Citation preview
    const citPreview = document.getElementById("paper-res-citation-preview");
    if (citPreview) {
      citPreview.innerText = data.citations ? data.citations.apa : (data.title || "Unknown Paper");
    }

    // 3-Sentence Summary (Academic)
    const pProblem = document.getElementById("res-exec-problem");
    const pSolution = document.getElementById("res-exec-solution");
    const pFinding = document.getElementById("res-exec-finding");
    const pLimitation = document.getElementById("res-exec-limitation");
    if (pProblem) pProblem.innerText = data.executive_summary.problem;
    if (pSolution) pSolution.innerText = data.executive_summary.intervention;
    if (pFinding) pFinding.innerText = data.executive_summary.main_finding;
    if (pLimitation) pLimitation.innerText = data.executive_summary.limitation || "None explicitly stated in abstract.";

    // ELI-Undergrad Box & Plain-English 4-Pillars
    const eliTheme = document.getElementById("res-eli-theme");
    const eliAnalogy = document.getElementById("res-eli-analogy");
    const eliProblem = document.getElementById("res-eli-problem");
    const eliSolution = document.getElementById("res-eli-solution");
    const eliTakeaway = document.getElementById("res-eli-takeaway");
    const eliLimitation = document.getElementById("res-eli-limitation");

    if (eliTheme) eliTheme.innerText = `💡 How to Understand This: ${data.plain_english_explanation.theme}`;
    if (eliAnalogy) eliAnalogy.innerText = data.plain_english_explanation.core_analogy;
    if (eliProblem) eliProblem.innerText = data.plain_english_explanation.simple_problem;
    if (eliSolution) eliSolution.innerText = data.plain_english_explanation.simple_solution;
    if (eliTakeaway) eliTakeaway.innerText = data.plain_english_explanation.simple_takeaway;
    if (eliLimitation) eliLimitation.innerText = data.plain_english_explanation.simple_limitation;

    // Jargon Buster
    const jargonCont = document.getElementById("res-jargon-container");
    if (jargonCont) {
      if (data.jargon_buster && data.jargon_buster.length > 0) {
        jargonCont.innerHTML = data.jargon_buster.map(j => `
          <div class="jargon-card">
            <div class="jargon-term">🧩 ${j.term}</div>
            <div class="jargon-def">${j.simple_def}</div>
            <div class="jargon-analogy">${j.analogy}</div>
          </div>
        `).join("");
      } else {
        jargonCont.innerHTML = `<p style="font-size: 0.8rem; color: #64748b; font-style: italic;">No highly specialized biotechnology jargon tags detected in this excerpt.</p>`;
      }
    }

    // Parameters
    const params = data.extracted_parameters || {};
    const setVal = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.innerText = val || "None detected";
    };
    setVal("res-param-chassis", params.chassis);
    setVal("res-param-tool", params.tool);
    setVal("res-param-metrics", params.primary_metric_sentence);
    setVal("res-param-controls", params.controls);
    setVal("res-param-burden", params.burden_statistic);
    setVal("res-param-milestone", params.target_milestone);
    setVal("res-param-gap", params.stated_gap);

    // Proposal Mapping Recommendations
    const recsCont = document.getElementById("res-proposal-recs-container");
    if (recsCont && data.proposal_recommendations) {
      recsCont.innerHTML = data.proposal_recommendations.map(r => `
        <div style="background: white; border-left: 3px solid #7c3aed; padding: 6px 10px; border-radius: 4px; font-size: 0.8rem;">
          <strong style="color: #6b21a8;">${r.section}:</strong>
          <span style="color: #334155;"> ${r.guidance}</span>
        </div>
      `).join("");
    }

    // Socratic RHEV Prompt
    const rhevBox = document.getElementById("res-rhev-prompt-box");
    if (rhevBox) {
      rhevBox.innerText = data.rhev_challenge;
    }

    // Tab 4: Research Landscape & Gap Story Rendering
    const land = data.three_stage_landscape || {};
    const art = land.stage1_state_of_the_art || {};
    const gap = land.stage2_unresolved_gap || {};
    const opp = land.stage3_research_opportunity || {};

    const elArtApproach = document.getElementById("res-land-art-approach");
    const elArtBenchmark = document.getElementById("res-land-art-benchmark");
    const elArtEvidence = document.getElementById("res-land-art-evidence");
    const elGapStatement = document.getElementById("res-land-gap-statement");
    const elOppStatement = document.getElementById("res-land-opp-statement");
    const elOppStrategy = document.getElementById("res-land-opp-strategy");
    const elOppMilestone = document.getElementById("res-land-opp-milestone");

    if (elArtApproach) elArtApproach.innerText = art.approach || params.tool || "Published experimental intervention";
    if (elArtBenchmark) elArtBenchmark.innerText = art.benchmark || params.primary_metric_sentence || "Empirical baseline rate reported in literature";
    if (elArtEvidence) elArtEvidence.innerText = art.citation || (data.citations && data.citations.apa ? data.citations.apa : (data.title || "Peer-reviewed publication"));
    if (elGapStatement) elGapStatement.innerText = gap.statement || params.stated_gap || (data.executive_summary && data.executive_summary.limitation) || "Operational constraint identified in literature";
    if (elOppStatement) elOppStatement.innerText = opp.opportunity_statement || "Investigate engineered intervention to surpass published benchmark and overcome the stated gap.";
    if (elOppStrategy) elOppStrategy.innerText = opp.test_strategy || params.controls || "Model testing with positive benchmark reference and negative vehicle blank.";
    if (elOppMilestone) elOppMilestone.innerText = opp.target_milestone || params.target_milestone || "Calibrated improvement over literature baseline";

    // Literature Position Map
    const posMap = data.position_map || {};
    const elLitEst = document.getElementById("lit-map-established");
    const elLitGap = document.getElementById("lit-map-gap");
    const elLitPaper = document.getElementById("lit-map-paper");
    const elLitProp = document.getElementById("lit-map-proposed");

    if (elLitEst) elLitEst.innerText = posMap.stage1_established || "Standard baseline technology";
    if (elLitGap) elLitGap.innerText = posMap.stage2_gap || (params.stated_gap ? params.stated_gap.slice(0, 90) + "..." : "Operational / mechanistic flaw");
    if (elLitPaper) elLitPaper.innerText = posMap.stage3_this_paper || (data.title ? data.title.slice(0, 90) + "..." : "Published benchmark study");
    if (elLitProp) elLitProp.innerText = posMap.stage4_proposed || "Proposed engineered solution & target milestone";

    // From Paper -> Proposal Synthesizer (6 points)
    const synth = data.from_paper_to_proposal || {};
    const elSynEst = document.getElementById("synth-point-established");
    const elSynBench = document.getElementById("synth-point-benchmark");
    const elSynLim = document.getElementById("synth-point-limitation");
    const elSynOpp = document.getElementById("synth-point-opportunity");
    const elSynCont = document.getElementById("synth-point-contribution");
    const elSynCheck = document.getElementById("synth-validation-checklist");

    if (elSynEst) elSynEst.innerText = synth.established_knowledge || "Demonstrated baseline biological mechanism in literature.";
    if (elSynBench) elSynBench.innerText = synth.current_benchmark || params.primary_metric_sentence || "Reported quantitative performance level.";
    if (elSynLim) elSynLim.innerText = synth.limitation || params.stated_gap || "Identified operational bottleneck requiring a new approach.";
    if (elSynOpp) elSynOpp.innerText = synth.research_opportunity || "Address the unaddressed literature gap.";
    if (elSynCont) elSynCont.innerText = synth.proposed_contribution || "Rational engineering intervention & validation.";

    if (elSynCheck) {
      const checklist = synth.required_validation_checklist || [
        "Include positive benchmark control (e.g. wild-type reference)",
        "Include negative vehicle / buffer blank control",
        "Verify activity in operational matrix / physiological conditions",
        "Target calibrated quantitative improvement (e.g. ≥2-fold or +10°C Tm)"
      ];
      elSynCheck.innerHTML = checklist.map((item) => `
        <label style="display: flex; align-items: flex-start; gap: 6px; background: #ffffff; padding: 6px 10px; border-radius: 6px; border: 1px solid #d1fae5; cursor: pointer;">
          <input type="checkbox" checked style="margin-top: 3px;">
          <span style="color: #065f46; line-height: 1.35;">${escapeHtml(item)}</span>
        </label>
      `).join("");
    }
  }

  // Copy Citation
  const copyCitBtn = document.getElementById("btn-copy-citation");
  if (copyCitBtn) {
    copyCitBtn.addEventListener("click", () => {
      if (currentDecodedData && currentDecodedData.citations) {
        navigator.clipboard.writeText(currentDecodedData.citations.apa);
        showToast("APA Citation copied to clipboard!");
      }
    });
  }

  // Transfer Chassis
  const transChassis = document.getElementById("transfer-chassis-btn");
  if (transChassis) {
    transChassis.addEventListener("click", () => {
      if (currentDecodedData && currentDecodedData.extracted_parameters) {
        const val = currentDecodedData.extracted_parameters.chassis;
        projectState.chassis = val;
        projectState.system = val;
        const el = document.getElementById("pillar-chassis");
        if (el) el.value = val;
        saveToStorage();
        updateLiveScoreDebounced();
        updateLogicChainUIDebounced();
        showToast(`Transferred Chassis to Step 1: "${val}"`);
      }
    });
  }

  // Transfer Tool
  const transTool = document.getElementById("transfer-tool-btn");
  if (transTool) {
    transTool.addEventListener("click", () => {
      if (currentDecodedData && currentDecodedData.extracted_parameters) {
        const val = currentDecodedData.extracted_parameters.tool;
        projectState.tool = val;
        const el = document.getElementById("pillar-tool");
        if (el) el.value = val;
        saveToStorage();
        updateLiveScoreDebounced();
        updateLogicChainUIDebounced();
        showToast(`Transferred Tool to Step 1: "${val}"`);
      }
    });
  }

  // Auto-fill entire matrix from decoded paper in Step 2 / Section 3
  const btnAutoFill = document.getElementById("btn-autofill-matrix");
  if (btnAutoFill) {
    btnAutoFill.addEventListener("click", async () => {
      if (!currentDecodedData || !currentDecodedData.extracted_parameters) {
        showToast("Loading benchmark paper (Nature 2020) to auto-fill & explain...");
        try {
          const resp = await fetch("/api/paper/samples");
          const samples = await resp.json();
          const sample = samples["petase"];
          if (sample) {
            await runDecodePaper({
              text: sample.abstract,
              title: sample.title,
              identifier: sample.doi,
              authors: sample.authors,
              year: sample.year,
              journal: sample.journal
            });
            if (currentDecodedData) {
              applyDecodedDataToMatrix(currentDecodedData);
              showToast("Loaded PETase benchmark & auto-filled 6 parameters with explanations!");
              return;
            }
          }
        } catch (e) {
          console.error(e);
        }
        showToast("Please put a paper above or choose a preset.");
        return;
      }

      applyDecodedDataToMatrix(currentDecodedData);
      showToast("Auto-filled all 6 Evidence Matrix parameters with paper explanations!");
    });
  }

  // Section 3: Toggle dedicated quick paper tools bar
  const btnTogglePaperTools = document.getElementById("btn-toggle-matrix-paper-tools");
  const matrixToolsBar = document.getElementById("matrix-paper-tools-bar");
  if (btnTogglePaperTools && matrixToolsBar) {
    btnTogglePaperTools.addEventListener("click", () => {
      const isHidden = window.getComputedStyle(matrixToolsBar).display === "none";
      matrixToolsBar.style.display = isHidden ? "block" : "none";
      if (isHidden) {
        const qInp = document.getElementById("matrix-quick-paper-input");
        if (qInp) qInp.focus();
      }
    });
  }

  // Section 3: Quick Benchmark Presets (PETase, Cas12a, Wheat)
  const matrixPresetBtns = document.querySelectorAll(".btn-matrix-preset");
  matrixPresetBtns.forEach(btn => {
    btn.addEventListener("click", async (e) => {
      e.stopPropagation();
      const pKey = btn.getAttribute("data-preset");
      const origText = btn.textContent;
      btn.disabled = true;
      btn.textContent = "⏳ Analyzing...";
      try {
        const resp = await fetch("/api/paper/samples");
        const samples = await resp.json();
        const sample = samples[pKey];
        if (sample) {
          showToast(`Decoding: ${sample.title.slice(0, 32)}...`);
          await runDecodePaper({
            text: sample.abstract,
            title: sample.title,
            identifier: sample.doi,
            authors: sample.authors,
            year: sample.year,
            journal: sample.journal
          });
          if (currentDecodedData) {
            applyDecodedDataToMatrix(currentDecodedData);
            showToast("Paper decoded! Evidence Matrix and in-depth explanations populated.");
          }
        }
      } catch (err) {
        console.error(err);
        showToast("Error loading paper preset.");
      } finally {
        btn.disabled = false;
        btn.textContent = origText;
      }
    });
  });

  // Section 3: Quick Paper Decoder & Explainer Handler
  const btnMatrixDecode = document.getElementById("btn-matrix-decode-paper");
  const matrixQuickInput = document.getElementById("matrix-quick-paper-input");

  async function handleMatrixQuickDecode() {
    const raw = matrixQuickInput ? matrixQuickInput.value.trim() : "";
    if (!raw) {
      showToast("Enter a DOI, PubMed ID, or paper abstract first.");
      if (matrixQuickInput) matrixQuickInput.focus();
      return;
    }

    if (btnMatrixDecode) {
      btnMatrixDecode.disabled = true;
      btnMatrixDecode.textContent = "⏳ Analyzing Paper...";
    }

    try {
      const isIdentifier = /^(10\.\d{4,9}\/|https?:\/\/|pmid:|\d{6,9}$)/i.test(raw) || raw.split(/\s+/).length < 15;
      if (isIdentifier) {
        let cleanId = raw.replace(/^["'<\(\[{]+|["'>\)\]}]+$/g, "")
          .replace(/^https?:\/\/(?:dx\.)?doi\.org\//i, "")
          .replace(/^https?:\/\/pubmed\.ncbi\.nlm\.nih\.gov\//i, "")
          .replace(/^doi\s*[:=]\s*/i, "")
          .replace(/^pmid\s*[:=]\s*/i, "")
          .replace(/\/+$/, "").trim();

        const fetchResp = await fetch("/api/paper/fetch", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ identifier: cleanId })
        });
        const fetched = await fetchResp.json();
        if (fetched.success && fetched.abstract && fetched.abstract.trim().length > 15) {
          await runDecodePaper({
            text: fetched.abstract,
            title: fetched.title,
            identifier: fetched.id || cleanId,
            authors: fetched.authors,
            year: fetched.year,
            journal: fetched.journal
          });
          if (currentDecodedData) {
            applyDecodedDataToMatrix(currentDecodedData);
            showToast("Paper decoded! Summary and explanations populated.");
          }
        } else if (fetched.success) {
          await runDecodePaper({
            text: fetched.abstract || fetched.title,
            title: fetched.title,
            identifier: fetched.id || cleanId,
            authors: fetched.authors,
            year: fetched.year,
            journal: fetched.journal
          });
          if (currentDecodedData) {
            applyDecodedDataToMatrix(currentDecodedData);
            showToast("Paper metadata decoded and explanations generated!");
          }
        } else {
          showToast(fetched.error || "Paper not found. Paste abstract text directly.");
        }
      } else {
        // Pasted abstract
        await runDecodePaper({
          text: raw,
          title: "Pasted Research Abstract",
          identifier: ""
        });
        if (currentDecodedData) {
          applyDecodedDataToMatrix(currentDecodedData);
          showToast("Paper abstract analyzed! Evidence Matrix & explanations populated.");
        }
      }
    } catch (err) {
      console.error(err);
      showToast("Error processing paper.");
    } finally {
      if (btnMatrixDecode) {
        btnMatrixDecode.disabled = false;
        btnMatrixDecode.textContent = "🔍 Decode Paper & Explain Everything";
      }
    }
  }

  if (btnMatrixDecode) {
    btnMatrixDecode.addEventListener("click", handleMatrixQuickDecode);
  }

  if (matrixQuickInput) {
    matrixQuickInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleMatrixQuickDecode();
      }
    });
  }

  // Section 3: Toggle Summary View
  const btnToggleExp = document.getElementById("btn-toggle-matrix-exp-details");
  const expGrid = document.getElementById("matrix-exp-story-grid");
  if (btnToggleExp && expGrid) {
    btnToggleExp.addEventListener("click", () => {
      const isHidden = window.getComputedStyle(expGrid).display === "none";
      expGrid.style.display = isHidden ? "grid" : "none";
      btnToggleExp.textContent = isHidden ? "👁️ Hide Summary View" : "👁️ Show Summary View";
    });
  }

  // Transfer Burden to Step 2 Matrix Parameter 1
  const transBurden = document.getElementById("transfer-burden-btn");
  if (transBurden) {
    transBurden.addEventListener("click", () => {
      if (currentDecodedData && currentDecodedData.extracted_parameters) {
        const val = currentDecodedData.extracted_parameters.burden_statistic;
        if (val) {
          projectState.matrix.yellow = val;
          const el = document.getElementById("matrix-yellow");
          if (el) el.value = val;
          saveToStorage();
          updateLiveScoreDebounced();
          updateLogicChainUIDebounced();
          showToast("Transferred Global Burden Statistic to Step 2 Evidence Matrix (Parameter 1)!");
        }
      }
    });
  }

  // Transfer Milestone / Key Innovation to Step 2 Matrix Parameter 5
  const transMilestone = document.getElementById("transfer-milestone-btn");
  if (transMilestone) {
    transMilestone.addEventListener("click", () => {
      if (currentDecodedData && currentDecodedData.extracted_parameters) {
        const val = currentDecodedData.extracted_parameters.key_innovation || currentDecodedData.extracted_parameters.target_milestone;
        if (val) {
          projectState.matrix.red = val;
          const el = document.getElementById("matrix-red");
          if (el) el.value = val;
          saveToStorage();
          updateLiveScoreDebounced();
          updateLogicChainUIDebounced();
          showToast("Transferred Key Innovation to Step 2 Evidence Matrix (Parameter 5)!");
        }
      }
    });
  }

  // Transfer Findings & Horizon to Step 2 Matrix Parameter 6
  const transFindings = document.getElementById("transfer-findings-btn");
  if (transFindings) {
    transFindings.addEventListener("click", () => {
      if (currentDecodedData && currentDecodedData.extracted_parameters) {
        const p = currentDecodedData.extracted_parameters;
        const cit = (currentDecodedData.citations && currentDecodedData.citations.apa)
          ? currentDecodedData.citations.apa
          : (currentDecodedData.doi ? `DOI: ${currentDecodedData.doi}` : "");
        let val = p.key_findings || p.primary_metric_sentence || "";
        if (p.research_horizon) {
          val += (val ? " | Target horizon: " : "") + p.research_horizon;
        }
        if (cit) {
          val += (val ? ` [${cit}]` : `[${cit}]`);
        }
        if (val) {
          projectState.matrix.citation = val;
          const el = document.getElementById("matrix-citation");
          if (el) el.value = val;
          saveToStorage();
          updateLiveScoreDebounced();
          updateLogicChainUIDebounced();
          showToast("Transferred Findings & Horizon to Step 2 Evidence Matrix (Parameter 6)!");
        }
      }
    });
  }

  // Transfer Metric to Step 2 Evidence Matrix
  const transMetric = document.getElementById("transfer-metric-btn");
  if (transMetric) {
    transMetric.addEventListener("click", () => {
      if (currentDecodedData && currentDecodedData.extracted_parameters) {
        const val = currentDecodedData.extracted_parameters.primary_metric_sentence;
        projectState.matrix.blue = val;
        const el = document.getElementById("matrix-blue");
        if (el) el.value = val;
        saveToStorage();
        updateLiveScoreDebounced();
        updateLogicChainUIDebounced();
        showToast("Transferred Metric to Step 2 Evidence Matrix (Parameter 2: Baseline Rate)!");
      }
    });
  }

  // Transfer Metric to Step 3 Funnel Tier 2
  const transMetricFunnel = document.getElementById("transfer-metric-funnel-btn");
  if (transMetricFunnel) {
    transMetricFunnel.addEventListener("click", () => {
      if (currentDecodedData && currentDecodedData.extracted_parameters) {
        const val = currentDecodedData.extracted_parameters.primary_metric_sentence;
        projectState.funnel.tier2 = val;
        const el = document.getElementById("funnel-tier2");
        if (el) el.value = val;
        saveToStorage();
        updateLiveScoreDebounced();
        updateLogicChainUIDebounced();
        showToast("Transferred Benchmark to Step 3 Background Funnel (Tier 2: Scientific Benchmark)!");
      }
    });
  }

  // Transfer Controls to Step 2 Matrix & Step 4 Methodology
  const transControls = document.getElementById("transfer-controls-btn");
  if (transControls) {
    transControls.addEventListener("click", () => {
      if (currentDecodedData && currentDecodedData.extracted_parameters) {
        const val = currentDecodedData.extracted_parameters.controls;
        projectState.matrix.purple = val;
        const el = document.getElementById("matrix-purple");
        if (el) el.value = val;
        if (!projectState.methodology.includes("Controls:")) {
          projectState.methodology = (projectState.methodology ? projectState.methodology + "\n" : "") + `Controls: ${val}`;
          const methEl = document.getElementById("methodology-input");
          if (methEl) methEl.value = projectState.methodology;
        }
        saveToStorage();
        updateLiveScoreDebounced();
        updateLogicChainUIDebounced();
        showToast("Transferred Controls to Step 2 Matrix & Step 4 Methodology!");
      }
    });
  }

  // Transfer Gap to Step 2 Matrix & Step 3 Funnel Tier 3
  const transGap = document.getElementById("transfer-gap-btn");
  if (transGap) {
    transGap.addEventListener("click", () => {
      if (currentDecodedData && currentDecodedData.extracted_parameters) {
        const val = currentDecodedData.extracted_parameters.stated_gap;
        projectState.matrix.green = val;
        projectState.funnel.tier3 = val;
        const mEl = document.getElementById("matrix-green");
        if (mEl) mEl.value = val;
        const fEl = document.getElementById("funnel-tier3");
        if (fEl) fEl.value = val;
        saveToStorage();
        updateLiveScoreDebounced();
        updateLogicChainUIDebounced();
        showToast("Transferred Gap to Step 2 Matrix & Step 3 Funnel (Tier 3)!");
      }
    });
  }

  // Transfer to Research Landscape & Comparative Position
  const transComp = document.getElementById("transfer-competitor-btn");
  if (transComp) {
    transComp.addEventListener("click", () => {
      if (currentDecodedData && currentDecodedData.extracted_parameters) {
        const p = currentDecodedData.extracted_parameters;
        if (!projectState.competitor_data) projectState.competitor_data = {};
        const cd = projectState.competitor_data;

        const authorStr = currentDecodedData.authors ? currentDecodedData.authors.split(',')[0].trim() : 'Published Study';
        const yearStr = currentDecodedData.year ? ` (${currentDecodedData.year})` : '';
        const paperName = p.tool ? `${p.tool} (${authorStr}${yearStr})` : `${authorStr}${yearStr}`;

        cd.principle_recent = paperName;
        cd.emerging_name = paperName;

        if (p.primary_metric_sentence) {
          cd.performance_recent = p.primary_metric_sentence.slice(0, 100);
          cd.emerging_speed = cd.performance_recent;
        }
        if (p.stated_gap) {
          cd.limitation_recent = p.stated_gap.slice(0, 120);
          cd.gap_recent = p.stated_gap.slice(0, 120);
          cd.emerging_drawback = cd.limitation_recent;
        }
        if (currentDecodedData.citations && currentDecodedData.citations.apa) {
          cd.evidence_recent = currentDecodedData.citations.apa.slice(0, 120);
        } else if (currentDecodedData.journal) {
          cd.evidence_recent = `${currentDecodedData.journal} (${currentDecodedData.year || ''})`;
        }

        const elPrinciple = document.getElementById("comp-rec-principle");
        if (elPrinciple) elPrinciple.value = cd.principle_recent;
        const elPerf = document.getElementById("comp-rec-performance");
        if (elPerf) elPerf.value = cd.performance_recent || "";
        const elLimit = document.getElementById("comp-rec-limitation");
        if (elLimit) elLimit.value = cd.limitation_recent || "";
        const elGap = document.getElementById("comp-rec-gap");
        if (elGap) elGap.value = cd.gap_recent || "";
        const elEvid = document.getElementById("comp-rec-evidence");
        if (elEvid) elEvid.value = cd.evidence_recent || "";

        saveToStorage();
        updateLiveScoreDebounced();
        showToast("Imported into Research Landscape & Comparative Position (Step 5)!");
      }
    });
  }

  // Append to References
  const btnAppendRef = document.getElementById("btn-append-to-references");
  if (btnAppendRef) {
    btnAppendRef.addEventListener("click", () => {
      if (currentDecodedData && currentDecodedData.citations) {
        const cit = currentDecodedData.citations.apa;
        if (!projectState.references.includes(cit)) {
          projectState.references = (projectState.references.trim() ? projectState.references.trim() + "\n" : "") + cit;
          const refEl = document.getElementById("references-input");
          if (refEl) refEl.value = projectState.references;
          saveToStorage();
          updateLiveScoreDebounced();
          updateLogicChainUIDebounced();
          showToast("Appended to Step 6 Bibliography!");
        } else {
          showToast("Reference is already in your bibliography.");
        }
      }
    });
  }

  // Transfer to Step 2 RHEV Lab
  const btnTransferRhev = document.getElementById("btn-transfer-to-rhev-lab");
  if (btnTransferRhev) {
    btnTransferRhev.addEventListener("click", () => {
      const draftEl = document.getElementById("paper-socratic-draft-input");
      const draft = draftEl ? draftEl.value.trim() : "";
      const text = textInput ? textInput.value.trim() : "";
      const origEl = document.getElementById("rhev-original");
      const studentEl = document.getElementById("rhev-draft");
      if (origEl && text) origEl.value = text.slice(0, 350);
      if (studentEl && draft) studentEl.value = draft;
      if (modal) modal.style.display = "none";
      goToStep(2);
      setTimeout(() => {
        const target = document.getElementById("rhev-original");
        if (target) {
          target.scrollIntoView({ behavior: "smooth", block: "center" });
          target.focus();
        }
      }, 150);
      showToast("Transferred to Step 2 RHEV Paraphrase Gym!");
    });
  }
}







/* ==========================================================================
   Scientific Visual Outputs & Multi-View Studio Engine
   ========================================================================== */

let activeFigure = "pipeline";
let activePalette = "indigo";
let activePipelineMode = "pipeline";

function initVisualStudio() {
  // 1. View Mode Switcher
  const btnStudio = document.getElementById("btn-view-studio");
  const btnSplit = document.getElementById("btn-view-split");
  const btnVisuals = document.getElementById("btn-view-visuals");
  const btnBreakthroughs = document.getElementById("btn-view-breakthroughs");
  const btnOpenVisualHub = document.getElementById("btn-open-visual-hub");

  if (btnStudio) btnStudio.addEventListener("click", () => setViewMode("studio"));
  if (btnSplit) btnSplit.addEventListener("click", () => setViewMode("split"));
  if (btnVisuals) btnVisuals.addEventListener("click", () => setViewMode("visuals"));
  if (btnBreakthroughs) btnBreakthroughs.addEventListener("click", () => setViewMode("breakthroughs"));
  if (btnOpenVisualHub) btnOpenVisualHub.addEventListener("click", () => setViewMode("visuals"));

  // 2. Figure Tab Switcher
  document.querySelectorAll(".btn-fig-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".btn-fig-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      activeFigure = tab.getAttribute("data-fig") || "pipeline";
      renderActiveVisualFigure();
    });
  });

  // 3. Palette Switcher
  document.querySelectorAll(".btn-palette").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".btn-palette").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activePalette = btn.getAttribute("data-palette") || "indigo";
      renderActiveVisualFigure();
    });
  });

  // 4. Print & Copy controls
  const btnPrintFig = document.getElementById("btn-print-fig");
  if (btnPrintFig) {
    btnPrintFig.addEventListener("click", () => {
      if (activeFigure === "pitch") {
        window.print();
      } else {
        const stage = document.getElementById("visual-stage-container");
        if (stage) {
          const printWin = window.open("", "_blank");
          printWin.document.write(`<html><head><title>BioWriter Scientific Figure</title><link rel="stylesheet" href="/static/css/studio.css"></head><body style="background:white; padding:30px;">${stage.innerHTML}</body></html>`);
          printWin.document.close();
          setTimeout(() => { printWin.print(); printWin.close(); }, 500);
        }
      }
    });
  }

  const btnCopyFig = document.getElementById("btn-copy-fig");
  if (btnCopyFig) {
    btnCopyFig.addEventListener("click", () => {
      const stage = document.getElementById("visual-stage-container");
      if (stage) {
        navigator.clipboard.writeText(stage.innerText).then(() => {
          showToast("Figure summary copied to clipboard!");
        });
      }
    });
  }

  // Initial render of visual figure and live manuscript
  renderLiveManuscript();
  renderActiveVisualFigure();
}

function setViewMode(mode) {
  const btnStudio = document.getElementById("btn-view-studio");
  const btnSplit = document.getElementById("btn-view-split");
  const btnVisuals = document.getElementById("btn-view-visuals");
  const btnBreakthroughs = document.getElementById("btn-view-breakthroughs");
  const ws = document.getElementById("studio-workspace");
  const btView = document.getElementById("view-container-breakthroughs");

  [btnStudio, btnSplit, btnVisuals, btnBreakthroughs].forEach(btn => {
    if (btn) btn.classList.remove("active");
  });

  const guidanceBar = document.getElementById("studio-floating-guidance-bar");

  if (mode === "breakthroughs") {
    document.body.classList.remove("split-view-active");
    if (btnBreakthroughs) btnBreakthroughs.classList.add("active");
    if (ws) ws.style.display = "none";
    if (btView) btView.style.display = "block";
    if (guidanceBar) guidanceBar.style.display = "none";
    loadBreakthroughsCatalog();
    showToast("Switched to Biotechnology Breakthroughs Radar");
    return;
  }

  // If leaving breakthroughs, hide breakthroughs and reveal workspace
  if (btView) btView.style.display = "none";
  if (ws && currentAuthUser) ws.style.display = "grid";

  // Manage persistent milestone bar visibility
  if (guidanceBar) {
    if (mode !== "studio" || sessionStorage.getItem("biowriter_guidance_dismissed") === "true") {
      guidanceBar.style.display = "none";
    } else if (currentAuthUser) {
      guidanceBar.style.display = "block";
    }
  }

  if (mode === "studio") {
    document.body.classList.remove("split-view-active");
    if (btnStudio) btnStudio.classList.add("active");
    showToast("Switched to Focused Studio Mode");
  } else if (mode === "split") {
    document.body.classList.add("split-view-active");
    if (btnSplit) btnSplit.classList.add("active");
    renderLiveManuscript();
    showToast("Switched to Live Split-Screen Manuscript Mode");
  } else if (mode === "visuals") {
    document.body.classList.remove("split-view-active");
    if (btnVisuals) btnVisuals.classList.add("active");
    goToStep(6);
    const card = document.getElementById("card-visual-figures-hub");
    if (card) {
      setTimeout(() => {
        card.scrollIntoView({ behavior: "smooth", block: "start" });
        card.style.boxShadow = "0 0 0 3px #0284c7, 0 10px 25px rgba(0,0,0,0.1)";
        setTimeout(() => card.style.boxShadow = "", 1800);
      }, 150);
    }
    renderActiveVisualFigure();
    showToast("Opened Scientific Visual Outputs & Figures Hub!");
  }
}

// ==========================================================================
// 1. Live Academic Manuscript Renderer
// ==========================================================================
function renderLiveManuscript() {
  const setEl = (id, text) => {
    const el = document.getElementById(id);
    if (el) el.innerText = text || "";
  };
  const setHtml = (id, html) => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = html || "";
  };

  setEl("manu-title", projectState.title || "Proposal Title Not Yet Specified");
  setEl("manu-author", projectState.student_name || "Principal Investigator & Research Team");
  const currentModality = (projectState.model_id === "custom" && projectState.custom_modality)
    ? projectState.custom_modality
    : (projectModels[projectState.model_id]?.name?.split("(")[0]?.trim() || "Biotechnology Research");
  setEl("manu-modality", currentModality);

  // Abstract & word count
  const absText = projectState.abstract || "No structured abstract drafted yet.";
  setEl("manu-abstract", absText);
  const wCount = absText.trim().split(/\s+/).filter(Boolean).length;
  setEl("manu-abstract-count", `${wCount} words (${wCount <= 250 ? 'Compliant' : 'Exceeds 250w'})`);

  // Background Funnel
  const fn = projectState.funnel || {};
  let bgHtml = "";
  if (fn.tier1) bgHtml += `<p style="margin-bottom:6px;"><strong>1. Problem Burden:</strong> ${escapeHtml(fn.tier1)}</p>`;
  if (fn.tier2) bgHtml += `<p style="margin-bottom:6px;"><strong>2. Current Status:</strong> ${escapeHtml(fn.tier2)}</p>`;
  if (fn.tier3) bgHtml += `<p style="margin-bottom:6px;"><strong>3. Biophysical Gap:</strong> <span style="background:#fee2e2; padding:1px 4px; border-radius:3px;">${escapeHtml(fn.tier3)}</span></p>`;
  if (fn.tier4) bgHtml += `<p style="margin-bottom:6px;"><strong>4. Hypothesis:</strong> <span style="background:#dcfce7; padding:1px 4px; border-radius:3px;">${escapeHtml(fn.tier4)}</span></p>`;
  setHtml("manu-background", bgHtml || "<em>Draft your 4 background funnel tiers in Step 3 to populate this section.</em>");

  // Aims
  const aims = projectState.aims || {};
  let aimsHtml = "";
  if (aims.aim1) aimsHtml += `<p style="margin-bottom:6px;"><strong>Objective 1 (WP1${aims.aim1_title ? ': ' + escapeHtml(aims.aim1_title) : ''}):</strong> ${escapeHtml(aims.aim1)}</p>`;
  if (aims.aim2) aimsHtml += `<p style="margin-bottom:6px;"><strong>Objective 2 (WP2${aims.aim2_title ? ': ' + escapeHtml(aims.aim2_title) : ''}):</strong> ${escapeHtml(aims.aim2)}</p>`;
  if (aims.aim3) aimsHtml += `<p style="margin-bottom:6px;"><strong>Objective 3 (WP3${aims.aim3_title ? ': ' + escapeHtml(aims.aim3_title) : ''}):</strong> ${escapeHtml(aims.aim3)}</p>`;
  setHtml("manu-aims", aimsHtml || "<em>Formulate your 3 specific objectives in Step 4 to populate this section.</em>");

  // Methodology & Controls
  let methHtml = projectState.methodology ? `<p style="margin-bottom:8px;">${escapeHtml(projectState.methodology)}</p>` : "";
  if (projectState.matrix && projectState.matrix.purple) {
    methHtml += `<p style="font-size:0.8rem; background:#f5f3ff; border-left:3px solid #7c3aed; padding:6px 10px; border-radius:4px;"><strong>Essential Experimental Controls:</strong> ${escapeHtml(projectState.matrix.purple)}</p>`;
  }
  setHtml("manu-methodology", methHtml || "<em>Detail your future-tense experimental protocols and controls in Step 4.</em>");

  // Table 1: Work Packages, Milestones & Controls
  const tableBody = document.getElementById("manu-table-body");
  if (tableBody) {
    const a1 = (aims && aims.aim1_title) ? aims.aim1_title : (aims && aims.aim1 ? aims.aim1.slice(0, 50) + "..." : "Construction & Preparation");
    const a2 = (aims && aims.aim2_title) ? aims.aim2_title : (aims && aims.aim2 ? aims.aim2.slice(0, 50) + "..." : "Functional Testing & Evaluation");
    const a3 = (aims && aims.aim3_title) ? aims.aim3_title : (aims && aims.aim3 ? aims.aim3.slice(0, 50) + "..." : "Real-World Validation & Performance");
    
    const gs = projectState.gantt_schedule || {};
    const m1 = gs.wp1_gate || (projectState.matrix && projectState.matrix.blue ? projectState.matrix.blue : "Target yield / sequence verified");
    const m2 = gs.wp2_gate || "Activity recovery / baseline improvement";
    const m3 = gs.wp3_gate || (projectState.matrix && projectState.matrix.red ? projectState.matrix.red : "Validated performance milestone");
    
    const c1 = (projectState.matrix && projectState.matrix.purple) ? projectState.matrix.purple : "Vehicle / negative control";
    const c2 = "Native unengineered baseline reference";
    const c3 = "Matrix / mock negative control";

    tableBody.innerHTML = `
      <tr>
        <td><strong>WP 1</strong></td>
        <td>${escapeHtml(a1)}</td>
        <td><span style="background:#e0f2fe; color:#0369a1; padding:2px 6px; border-radius:3px; font-weight:700;">${escapeHtml(m1)}</span></td>
        <td>${escapeHtml(c1)}</td>
      </tr>
      <tr>
        <td><strong>WP 2</strong></td>
        <td>${escapeHtml(a2)}</td>
        <td><span style="background:#e0f2fe; color:#0369a1; padding:2px 6px; border-radius:3px; font-weight:700;">${escapeHtml(m2)}</span></td>
        <td>${escapeHtml(c2)}</td>
      </tr>
      <tr>
        <td><strong>WP 3</strong></td>
        <td>${escapeHtml(a3)}</td>
        <td><span style="background:#e0f2fe; color:#0369a1; padding:2px 6px; border-radius:3px; font-weight:700;">${escapeHtml(m3)}</span></td>
        <td>${escapeHtml(c3)}</td>
      </tr>
    `;
  }

  // Figure 1 Mini Callout Preview
  const figPreview = document.getElementById("manu-figure-preview");
  if (figPreview) {
    const chassis = projectState.chassis || projectState.system || "Host Chassis";
    const tool = projectState.tool || "Molecular Tool";
    const target = projectState.target || "Phenotypic Target";
    figPreview.innerHTML = `
      <div style="display:flex; align-items:center; justify-content:center; gap:8px; flex-wrap:wrap; font-size:0.78rem;">
        <span style="background:#f0fdf4; border:1px solid #86efac; color:#15803d; padding:4px 8px; border-radius:6px; font-weight:700;">🦠 ${escapeHtml(chassis)}</span>
        <span style="color:#94a3b8; font-weight:800;">➔</span>
        <span style="background:#faf5ff; border:1px solid #d8b4fe; color:#7e22ce; padding:4px 8px; border-radius:6px; font-weight:700;">✂️ ${escapeHtml(tool)}</span>
        <span style="color:#94a3b8; font-weight:800;">➔</span>
        <span style="background:#eff6ff; border:1px solid #93c5fd; color:#1d4ed8; padding:4px 8px; border-radius:6px; font-weight:700;">🎯 ${escapeHtml(target)}</span>
      </div>
    `;
  }

  // Deliverables & Impact
  const imp = projectState.impact_data || {};
  let impHtml = "";
  if (imp.academic) impHtml += `<p style="margin-bottom:4px;"><strong>Academic:</strong> ${escapeHtml(imp.academic)}</p>`;
  if (imp.economic) impHtml += `<p style="margin-bottom:4px;"><strong>Economic:</strong> ${escapeHtml(imp.economic)}</p>`;
  if (imp.societal) impHtml += `<p style="margin-bottom:4px;"><strong>Societal:</strong> ${escapeHtml(imp.societal)}</p>`;
  if (!impHtml && projectState.impact) impHtml = `<p>${escapeHtml(projectState.impact)}</p>`;
  setHtml("manu-impact", impHtml || "<em>Define your 3-tier long-term impact in Step 5.</em>");

  // Competitor & USP
  const comp = projectState.competitor_data || {};
  let compHtml = "";
  if (projectState.usps || comp.usp) {
    compHtml += `<p style="background:#ecfdf5; border-left:3px solid #059669; padding:8px 12px; border-radius:4px; margin-bottom:10px;"><strong>Unique Selling Proposition (USP):</strong> ${escapeHtml(projectState.usps || comp.usp)}</p>`;
  }
  const pEst = comp.principle_established || comp.incumbent_name;
  const pProp = comp.principle_proposed || comp.proposed_name || projectState.tool;
  if (pEst || pProp) {
    compHtml += `
      <div style="overflow-x:auto; margin-top:8px;">
        <table style="width:100%; font-size:0.75rem; border-collapse:collapse; border:1px solid #cbd5e1;">
          <thead>
            <tr style="background:#f1f5f9; text-align:left;">
              <th style="padding:4px 6px; border:1px solid #cbd5e1; width:22%;">Dimension</th>
              <th style="padding:4px 6px; border:1px solid #cbd5e1; width:26%;">Established</th>
              <th style="padding:4px 6px; border:1px solid #cbd5e1; width:26%;">Recent</th>
              <th style="padding:4px 6px; border:1px solid #cbd5e1; width:26%; background:#ecfdf5;">Proposed</th>
            </tr>
          </thead>
          <tbody>
            <tr><td style="padding:4px 6px; border:1px solid #cbd5e1;"><strong>Principle / tech</strong></td><td style="padding:4px 6px; border:1px solid #cbd5e1;">${escapeHtml(pEst || '—')}</td><td style="padding:4px 6px; border:1px solid #cbd5e1;">${escapeHtml(comp.principle_recent || comp.emerging_name || '—')}</td><td style="padding:4px 6px; border:1px solid #cbd5e1; background:#f0fdf4;">${escapeHtml(pProp || '—')}</td></tr>
            <tr><td style="padding:4px 6px; border:1px solid #cbd5e1;"><strong>Main strength</strong></td><td style="padding:4px 6px; border:1px solid #cbd5e1;">${escapeHtml(comp.strength_established || '—')}</td><td style="padding:4px 6px; border:1px solid #cbd5e1;">${escapeHtml(comp.strength_recent || '—')}</td><td style="padding:4px 6px; border:1px solid #cbd5e1; background:#f0fdf4;">${escapeHtml(comp.strength_proposed || '—')}</td></tr>
            <tr><td style="padding:4px 6px; border:1px solid #cbd5e1;"><strong>Key limitation</strong></td><td style="padding:4px 6px; border:1px solid #cbd5e1;">${escapeHtml(comp.limitation_established || '—')}</td><td style="padding:4px 6px; border:1px solid #cbd5e1;">${escapeHtml(comp.limitation_recent || '—')}</td><td style="padding:4px 6px; border:1px solid #cbd5e1; background:#f0fdf4;">${escapeHtml(comp.limitation_proposed || '—')}</td></tr>
            <tr><td style="padding:4px 6px; border:1px solid #cbd5e1;"><strong>Performance</strong></td><td style="padding:4px 6px; border:1px solid #cbd5e1;">${escapeHtml(comp.performance_established || comp.incumbent_speed || '—')}</td><td style="padding:4px 6px; border:1px solid #cbd5e1;">${escapeHtml(comp.performance_recent || comp.emerging_speed || '—')}</td><td style="padding:4px 6px; border:1px solid #cbd5e1; background:#f0fdf4;">${escapeHtml(comp.performance_proposed || comp.proposed_speed || '—')}</td></tr>
            <tr><td style="padding:4px 6px; border:1px solid #cbd5e1;"><strong>Cost / resources</strong></td><td style="padding:4px 6px; border:1px solid #cbd5e1;">${escapeHtml(comp.cost_established || comp.incumbent_cost || '—')}</td><td style="padding:4px 6px; border:1px solid #cbd5e1;">${escapeHtml(comp.cost_recent || comp.emerging_cost || '—')}</td><td style="padding:4px 6px; border:1px solid #cbd5e1; background:#f0fdf4;">${escapeHtml(comp.cost_proposed || comp.proposed_cost || '—')}</td></tr>
            <tr><td style="padding:4px 6px; border:1px solid #cbd5e1;"><strong>Safety / sustainability</strong></td><td style="padding:4px 6px; border:1px solid #cbd5e1;">${escapeHtml(comp.safety_established || comp.incumbent_safety || '—')}</td><td style="padding:4px 6px; border:1px solid #cbd5e1;">${escapeHtml(comp.safety_recent || comp.emerging_safety || '—')}</td><td style="padding:4px 6px; border:1px solid #cbd5e1; background:#f0fdf4;">${escapeHtml(comp.safety_proposed || comp.proposed_safety || '—')}</td></tr>
            <tr><td style="padding:4px 6px; border:1px solid #cbd5e1;"><strong>Evidence available</strong></td><td style="padding:4px 6px; border:1px solid #cbd5e1;">${escapeHtml(comp.evidence_established || '—')}</td><td style="padding:4px 6px; border:1px solid #cbd5e1;">${escapeHtml(comp.evidence_recent || '—')}</td><td style="padding:4px 6px; border:1px solid #cbd5e1; background:#f0fdf4;">${escapeHtml(comp.evidence_proposed || '—')}</td></tr>
            <tr><td style="padding:4px 6px; border:1px solid #cbd5e1; background:#fef2f2;"><strong>Unresolved gap</strong></td><td style="padding:4px 6px; border:1px solid #cbd5e1; background:#fef2f2;">${escapeHtml(comp.gap_established || '—')}</td><td style="padding:4px 6px; border:1px solid #cbd5e1; background:#fef2f2;">${escapeHtml(comp.gap_recent || '—')}</td><td style="padding:4px 6px; border:1px solid #cbd5e1; background:#fef2f2;">${escapeHtml(comp.gap_proposed || '—')}</td></tr>
            <tr><td style="padding:4px 6px; border:1px solid #cbd5e1; background:#f0fdf4;"><strong>Contribution of study</strong></td><td style="padding:4px 6px; border:1px solid #cbd5e1; text-align:center;">—</td><td style="padding:4px 6px; border:1px solid #cbd5e1; text-align:center;">—</td><td style="padding:4px 6px; border:1px solid #cbd5e1; background:#dcfce7; font-weight:600;">${escapeHtml(comp.contribution_proposed || projectState.usps || '—')}</td></tr>
          </tbody>
        </table>
      </div>
    `;
  }
  setHtml("manu-competitors", compHtml || "<em>Define your competitor landscape and USP in Step 5.</em>");

  // References
  const refs = projectState.references ? escapeHtml(projectState.references).replace(/\n/g, "<br>") : "<em>Paste your reference list in Step 6.</em>";
  setHtml("manu-references", refs);

  // Wire Print and Copy Buttons (Option C)
  const btnPrint = document.getElementById("btn-print-manuscript");
  if (btnPrint && !btnPrint._wired) {
    btnPrint._wired = true;
    btnPrint.addEventListener("click", () => window.print());
  }

  const btnCopy = document.getElementById("btn-copy-manuscript");
  if (btnCopy && !btnCopy._wired) {
    btnCopy._wired = true;
    btnCopy.addEventListener("click", () => {
      const fullText = `NATURE BIOTECHNOLOGY PREPRINT\n\nTitle: ${projectState.title || 'Untitled Proposal'}\nAuthors: ${projectState.student_name || 'Anonymous'}\n\nSTRUCTURED ABSTRACT:\n${projectState.abstract || ''}\n\n1. INTRODUCTION & GAP:\n${projectState.funnel ? Object.values(projectState.funnel).join('\n') : ''}\n\n2. SPECIFIC OBJECTIVES:\n${projectState.aims ? Object.values(projectState.aims).join('\n') : ''}\n\n3. METHODOLOGY & CONTROLS:\n${projectState.methodology || ''}\n\nREFERENCES:\n${projectState.references || ''}`;
      navigator.clipboard.writeText(fullText).then(() => {
        showToast("Full preprint manuscript copied to clipboard!");
      });
    });
  }
}

// ==========================================================================
// 2. Active Figure Dispatcher
// ==========================================================================
function renderActiveVisualFigure() {
  const container = document.getElementById("visual-stage-container");
  if (!container) return;

  if (activeFigure === "pipeline") {
    container.innerHTML = renderPipelineHtml();
    wirePipelineToggles();
  } else if (activeFigure === "donut") {
    container.innerHTML = renderDonutHtml();
  } else if (activeFigure === "pitch") {
    container.innerHTML = renderPitchSheetHtml();
  } else {
    activeFigure = "pipeline";
    container.innerHTML = renderPipelineHtml();
    wirePipelineToggles();
  }
}

// ==========================================================================
// 3. Output 1: 4-Pillar Publication Graphical Abstract
// ==========================================================================
function renderGraphicalAbstractHtml() {
  const title = projectState.title ? projectState.title.trim() : "(Project Title Defined in Step 1)";
  const pi = projectState.student_name ? projectState.student_name.trim() : "Principal Investigator & Research Team";
  const modality = (projectState.model_id === "custom" && projectState.custom_modality) 
    ? projectState.custom_modality 
    : (projectModels[projectState.model_id]?.name?.split("(")[0]?.trim() || "Biotechnology Research");

  let problem = "";
  if (projectState.funnel && projectState.funnel.tier1 && projectState.funnel.tier1.trim()) {
    problem = projectState.funnel.tier1.trim();
  } else if (projectState.matrix && projectState.matrix.yellow && projectState.matrix.yellow.trim()) {
    problem = projectState.matrix.yellow.trim();
  } else {
    problem = "(Define epidemiological or scientific problem burden in Step 2 or Step 3)";
  }
  if (problem.length > 130) problem = problem.slice(0, 130) + "...";

  const chassis = projectState.chassis || projectState.system || "(Host organism / test specimen defined in Step 1)";
  const tool = projectState.tool || "(Molecular tool / engineered intervention defined in Step 1)";
  
  let metric = "";
  if (projectState.matrix && projectState.matrix.blue && projectState.matrix.blue.trim()) {
    metric = projectState.matrix.blue.trim();
  } else if (projectState.matrix && projectState.matrix.red && projectState.matrix.red.trim()) {
    metric = projectState.matrix.red.trim();
  } else if (projectState.target && projectState.target.trim()) {
    metric = projectState.target.trim();
  } else {
    metric = "(Target metric / baseline benchmark in Step 2)";
  }

  let gap = "";
  if (projectState.funnel && projectState.funnel.tier3 && projectState.funnel.tier3.trim()) {
    gap = projectState.funnel.tier3.trim();
  } else if (projectState.matrix && projectState.matrix.green && projectState.matrix.green.trim()) {
    gap = projectState.matrix.green.trim();
  } else if (projectState.competitor_data && projectState.competitor_data.gap_established) {
    gap = projectState.competitor_data.gap_established;
  } else {
    gap = "(Unresolved mechanistic or technical gap in Step 2/Step 3)";
  }
  if (gap.length > 120) gap = gap.slice(0, 120) + "...";

  let breakthrough = "";
  if (projectState.matrix && projectState.matrix.red && projectState.matrix.red.trim()) {
    breakthrough = projectState.matrix.red.trim();
  } else if (projectState.usps && projectState.usps.trim()) {
    breakthrough = projectState.usps.trim();
  } else if (projectState.competitor_data && projectState.competitor_data.contribution_proposed) {
    breakthrough = projectState.competitor_data.contribution_proposed;
  } else {
    breakthrough = "(Proposed breakthrough & novel mechanism formulated in Step 4/Step 5)";
  }
  if (breakthrough.length > 130) breakthrough = breakthrough.slice(0, 130) + "...";

  let impactText = projectState.impact || projectState.expected_outcomes || "";
  let acadImpact = "High-impact peer-reviewed publication & open dataset";
  let econImpact = "Field-deployable translational performance advantage";
  let socImpact = "Addressing key healthcare, environmental, or agrarian challenge";
  if (impactText) {
    const lines = impactText.split("\n").map(l => l.trim()).filter(Boolean);
    if (lines.length >= 1 && lines[0].length > 5) acadImpact = lines[0].slice(0, 50);
    if (lines.length >= 2 && lines[1].length > 5) econImpact = lines[1].slice(0, 50);
    if (lines.length >= 3 && lines[2].length > 5) socImpact = lines[2].slice(0, 50);
  }

  const headerGradients = {
    indigo: "linear-gradient(135deg, #1e1b4b 0%, #4338ca 100%)",
    emerald: "linear-gradient(135deg, #064e3b 0%, #059669 100%)",
    cyan: "linear-gradient(135deg, #0c4a6e 0%, #0284c7 100%)"
  };
  const headerBg = headerGradients[activePalette] || headerGradients.indigo;

  return `
    <div class="ga-container" id="printable-ga-figure">
      <div class="ga-header-strip" style="background: ${headerBg};">
        <div>
          <div style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1px; color: #a5f3fc; font-weight: 700;">
            Publication Graphical Abstract • BT_301 Grant Portfolio
          </div>
          <div class="ga-title-text">${escapeHtml(title)}</div>
        </div>
        <div style="text-align: right;">
          <span style="background: rgba(255,255,255,0.2); padding: 4px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 700;">
            ${escapeHtml(modality)}
          </span>
          <div style="font-size: 0.75rem; color: #e2e8f0; margin-top: 4px;">PI: ${escapeHtml(pi)}</div>
        </div>
      </div>

      <!-- 4 Pillars Grid -->
      <div class="ga-grid">
        <!-- 1. Problem -->
        <div class="ga-pillar-card p-problem">
          <div class="ga-pillar-tag" style="color: #b91c1c;">
            <span>🎯 1. Target Problem</span>
          </div>
          <div class="ga-pillar-content">${escapeHtml(problem)}</div>
        </div>

        <!-- 2. Biological Chassis -->
        <div class="ga-pillar-card p-chassis">
          <div class="ga-pillar-tag" style="color: #047857;">
            <span>🧫 2. Biological Chassis / System</span>
          </div>
          <div class="ga-pillar-content"><strong>Host / Matrix:</strong> ${escapeHtml(chassis)}</div>
        </div>

        <!-- 3. Molecular Tool -->
        <div class="ga-pillar-card p-tool">
          <div class="ga-pillar-tag" style="color: #1d4ed8;">
            <span>🧬 3. Molecular Tool / Intervention</span>
          </div>
          <div class="ga-pillar-content">${escapeHtml(tool)}</div>
        </div>

        <!-- 4. Quantitative Metric -->
        <div class="ga-pillar-card p-metric">
          <div class="ga-pillar-tag" style="color: #b45309;">
            <span>📊 4. Empirical Benchmark</span>
          </div>
          <div class="ga-pillar-content" style="font-size:0.8rem; color:#475569;">Quantitative Target Metric:</div>
          <div class="ga-stat-badge">${escapeHtml(metric)}</div>
        </div>
      </div>

      <!-- Mechanism Flow Ribbon -->
      <div style="background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 12px 18px; display: flex; align-items: center; justify-content: space-between; gap: 12px; font-size: 0.8rem; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 200px; background: white; padding: 8px 12px; border-radius: 6px; border-left: 3px solid #ef4444;">
          <strong style="color: #b91c1c;">Identified Gap:</strong> ${escapeHtml(gap)}
        </div>
        <div style="font-size: 1.2rem; color: #4338ca; font-weight: 800;">➔</div>
        <div style="flex: 1; min-width: 200px; background: white; padding: 8px 12px; border-radius: 6px; border-left: 3px solid #10b981;">
          <strong style="color: #047857;">Proposed Breakthrough:</strong> ${escapeHtml(breakthrough)}
        </div>
      </div>

      <!-- 3-Tier Impact Footer -->
      <div class="ga-impact-bar">
        <div><strong>3-Tier Expected Impact:</strong></div>
        <div style="background: white; padding: 3px 8px; border-radius: 4px; border: 1px solid #cbd5e1;">🎓 <strong>Academic:</strong> ${escapeHtml(acadImpact)}</div>
        <div style="background: white; padding: 3px 8px; border-radius: 4px; border: 1px solid #cbd5e1;">💼 <strong>Economic:</strong> ${escapeHtml(econImpact)}</div>
        <div style="background: white; padding: 3px 8px; border-radius: 4px; border: 1px solid #cbd5e1;">🌍 <strong>Societal:</strong> ${escapeHtml(socImpact)}</div>
      </div>
    </div>
  `;
}

// ==========================================================================
// 4. Output 2: 6-Axis Scientific Rigor Radar Chart
// ==========================================================================
function renderRigorRadarHtml() {
  // Calculate dimension scores (0 to 1) based on real proposal completion
  const s1 = (projectState.funnel && projectState.funnel.tier1 && projectState.funnel.tier3) ? 0.90 : 0.40;
  const s2 = (projectState.matrix && projectState.matrix.blue) ? 0.85 : 0.35;
  const s3 = (projectState.funnel && projectState.funnel.tier4) ? 0.88 : 0.45;
  const s4 = (projectState.aims && projectState.aims.aim1 && projectState.aims.aim2 && projectState.aims.aim3) ? 0.95 : 0.40;
  const s5 = (projectState.methodology && projectState.methodology.length > 50) ? 0.85 : 0.30;
  const s6 = (projectState.references && projectState.references.length > 30) ? 0.80 : 0.35;

  const scores = [s1, s2, s3, s4, s5, s6];
  const labels = [
    "1. Novelty & Gap",
    "2. Evidence & Benchmarks",
    "3. Inverted Funnel",
    "4. Aims Decoupling",
    "5. Methodology & Controls",
    "6. References & Rigor"
  ];

  const cx = 200, cy = 200, radius = 130;
  const numAxes = 6;
  const angleStep = (2 * Math.PI) / numAxes;

  // Grid rings (20%, 40%, 60%, 80%, 100%)
  let gridPolys = "";
  for (let level = 0.2; level <= 1.05; level += 0.2) {
    let pts = [];
    for (let i = 0; i < numAxes; i++) {
      const ang = i * angleStep - Math.PI / 2;
      const x = cx + radius * level * Math.cos(ang);
      const y = cy + radius * level * Math.sin(ang);
      pts.push(`${x.toFixed(1)},${y.toFixed(1)}`);
    }
    gridPolys += `<polygon points="${pts.join(' ')}" fill="none" stroke="#e2e8f0" stroke-width="1.5" />`;
  }

  // Radial axes lines & labels
  let axesLines = "";
  let textLabels = "";
  for (let i = 0; i < numAxes; i++) {
    const ang = i * angleStep - Math.PI / 2;
    const x = cx + radius * Math.cos(ang);
    const y = cy + radius * Math.sin(ang);
    axesLines += `<line x1="${cx}" y1="${cy}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" stroke="#cbd5e1" stroke-dasharray="3,3" />`;

    // Label position (pushed slightly outward)
    const lx = cx + (radius + 24) * Math.cos(ang);
    const ly = cy + (radius + 18) * Math.sin(ang);
    const anchor = (Math.abs(Math.cos(ang)) < 0.2) ? "middle" : (Math.cos(ang) > 0 ? "start" : "end");
    textLabels += `<text x="${lx.toFixed(1)}" y="${ly.toFixed(1)}" text-anchor="${anchor}" font-size="10" font-weight="700" fill="#334155">${labels[i]}</text>`;
  }

  // Ideal target polygon (dashed blue)
  let idealPts = [];
  for (let i = 0; i < numAxes; i++) {
    const ang = i * angleStep - Math.PI / 2;
    const x = cx + radius * 0.9 * Math.cos(ang);
    const y = cy + radius * 0.9 * Math.sin(ang);
    idealPts.push(`${x.toFixed(1)},${y.toFixed(1)}`);
  }

  // Student proposal polygon
  let studentPts = [];
  let dots = "";
  for (let i = 0; i < numAxes; i++) {
    const ang = i * angleStep - Math.PI / 2;
    const val = scores[i];
    const x = cx + radius * val * Math.cos(ang);
    const y = cy + radius * val * Math.sin(ang);
    studentPts.push(`${x.toFixed(1)},${y.toFixed(1)}`);
    dots += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="4.5" fill="#4338ca" stroke="#ffffff" stroke-width="1.5" />`;
  }

  const avgScore = Math.round((scores.reduce((a, b) => a + b, 0) / 6) * 100);

  return `
    <div class="radar-wrapper">
      <div style="background: white; border-radius: 12px; padding: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
        <svg width="400" height="400" viewBox="0 0 400 400" style="overflow: visible;">
          ${gridPolys}
          ${axesLines}
          <!-- Ideal Benchmark Polygon -->
          <polygon points="${idealPts.join(' ')}" fill="rgba(59, 130, 246, 0.08)" stroke="#3b82f6" stroke-width="1.5" stroke-dasharray="4,4" />
          <!-- Student Polygon -->
          <polygon points="${studentPts.join(' ')}" fill="rgba(79, 70, 229, 0.25)" stroke="#4338ca" stroke-width="2.5" />
          ${dots}
          ${textLabels}
        </svg>
      </div>

      <div class="radar-legend-box">
        <div style="font-size: 0.8rem; text-transform: uppercase; font-weight: 800; color: #4338ca; margin-bottom: 4px;">Proposal Health Index</div>
        <div style="font-size: 2rem; font-weight: 800; color: #1e1b4b; margin-bottom: 8px;">${avgScore}% Balanced</div>

        <div style="font-size: 0.82rem; color: #475569; line-height: 1.5; margin-bottom: 12px;">
          <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
            <span style="width:12px; height:12px; background:#4338ca; border-radius:2px;"></span>
            <strong>Your Proposal Rigor Profile</strong>
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="width:12px; height:12px; border:2px dashed #3b82f6; border-radius:2px;"></span>
            <strong>Target NIH/STDF Grant Benchmark</strong>
          </div>
        </div>

        <div style="background: #f8fafc; border-left: 3px solid #10b981; padding: 8px 12px; border-radius: 4px; font-size: 0.78rem;">
          <strong>💡 Strength:</strong> Clear work package independence across 3 specific aims.
        </div>
        <div style="background: #f8fafc; border-left: 3px solid #f59e0b; padding: 8px 12px; border-radius: 4px; font-size: 0.78rem; margin-top: 6px;">
          <strong>🔍 Area for Polish:</strong> Ensure empirical baseline metric ($T_m, k_{cat}$) is fully specified in Step 2.
        </div>
      </div>
    </div>
  `;
}

// ==========================================================================
// 5. Output 3: Experimental Pipeline Diagram
// ==========================================================================
function renderPipelineHtml() {
  const aims = projectState.aims || {};
  const a1 = aims.aim1 || "(Define Aim 1 objective in Step 4)";
  const a2 = aims.aim2 || "(Define Aim 2 objective in Step 4)";
  const a3 = aims.aim3 || "(Define Aim 3 objective in Step 4)";
  const t1 = aims.aim1_title || "Phase 1 • Construction & Preparation (WP1)";
  const t2 = aims.aim2_title || "Phase 2 • Functional Testing & Evaluation (WP2)";
  const t3 = aims.aim3_title || "Phase 3 • Real-World Validation & Trials (WP3)";
  const totM = Math.max(3, Math.min(60, parseInt(projectState.gantt_schedule?.total_months, 10) || 18));

  let controls = "";
  if (projectState.matrix && projectState.matrix.purple && projectState.matrix.purple.trim()) {
    controls = projectState.matrix.purple.trim();
  } else if (projectState.control_triad && (projectState.control_triad.positive || projectState.control_triad.negative)) {
    controls = `Positive: ${projectState.control_triad.positive || "Benchmark"} | Negative: ${projectState.control_triad.negative || "Vehicle control"}`;
  } else {
    controls = "Essential experimental controls: Positive benchmark, negative vehicle, and specificity standards.";
  }

  return `
    <div style="width: 100%; max-width: 900px; display: flex; flex-direction: column; align-items: center;">
      <!-- Pipeline Mode Switcher -->
      <div style="display: flex; gap: 8px; margin-bottom: 16px;">
        <button type="button" class="btn-pipeline-toggle active" data-mode="pipeline" style="background:#4338ca; color:white; border:none; padding:5px 14px; border-radius:6px; font-size:0.8rem; font-weight:700; cursor:pointer;">
          🧪 3-Phase Work Package Pipeline
        </button>
        <button type="button" class="btn-pipeline-toggle" data-mode="gantt" style="background:#f1f5f9; color:#475569; border:1px solid #cbd5e1; padding:5px 14px; border-radius:6px; font-size:0.8rem; font-weight:700; cursor:pointer;">
          📅 ${totM}-Month Gantt Milestones
        </button>
      </div>

      <div id="pipeline-content-stage" style="width:100%;">
        ${renderPipelineCardsHtml(a1, a2, a3, t1, t2, t3, controls)}
      </div>
    </div>
  `;
}

function renderPipelineCardsHtml(a1, a2, a3, t1, t2, t3, controls) {
  const gs = projectState.gantt_schedule || {};
  const g1 = gs.wp1_gate ? `Checkpoint: ${gs.wp1_gate}` : "Checkpoint: Sequence / Model Verification";
  const g2 = gs.wp2_gate ? `Checkpoint: ${gs.wp2_gate}` : "Checkpoint: Quantitative Activity Assay";
  const g3 = gs.wp3_gate ? `Checkpoint: ${gs.wp3_gate}` : "Checkpoint: Operational Validation & Matrix Trial";

  return `
    <div class="pipeline-flow">
      <!-- WP1 Node -->
      <div class="pipeline-node" style="border-top: 4px solid #3b82f6;">
        <div class="pipeline-node-title">${escapeHtml(t1)}</div>
        <p style="font-size:0.84rem; color:#334155; line-height:1.4;">${escapeHtml(a1)}</p>
        <div class="pipeline-control-tag">${escapeHtml(g1)}</div>
      </div>

      <div style="font-size: 1.4rem; color: #4338ca; font-weight: 800;">➔</div>

      <!-- WP2 Node -->
      <div class="pipeline-node" style="border-top: 4px solid #10b981;">
        <div class="pipeline-node-title">${escapeHtml(t2)}</div>
        <p style="font-size:0.84rem; color:#334155; line-height:1.4;">${escapeHtml(a2)}</p>
        <div class="pipeline-control-tag" style="background:#e0f2fe; color:#0369a1;">${escapeHtml(g2)}</div>
      </div>

      <div style="font-size: 1.4rem; color: #4338ca; font-weight: 800;">➔</div>

      <!-- WP3 Node -->
      <div class="pipeline-node" style="border-top: 4px solid #f59e0b;">
        <div class="pipeline-node-title">${escapeHtml(t3)}</div>
        <p style="font-size:0.84rem; color:#334155; line-height:1.4;">${escapeHtml(a3)}</p>
        <div class="pipeline-control-tag" style="background:#fef3c7; color:#92400e;">${escapeHtml(g3)}</div>
      </div>
    </div>

    <!-- Essential Controls Bar -->
    <div style="width: 100%; max-width: 880px; margin-top: 18px; background: white; border: 1px solid #cbd5e1; border-left: 4px solid #8b5cf6; padding: 12px 16px; border-radius: 8px; font-size: 0.84rem;">
      <strong style="color: #6d28d9;">Essential Controls Integrated Into Pipeline:</strong>
      <div style="color: #334155; margin-top: 4px;">${escapeHtml(controls)}</div>
    </div>
  `;
}

function renderGanttTimelineHtml() {
  ensureGanttTasks();
  const gs = projectState.gantt_schedule || {};
  const totalMonths = Math.max(3, Math.min(60, parseInt(gs.total_months, 10) || 18));
  const tasks = gs.tasks || [];

  const calcLeft = (start) => ((start - 1) / totalMonths * 100).toFixed(1) + "%";
  const calcWidth = (start, end) => (((end - start + 1) / totalMonths) * 100).toFixed(1) + "%";

  let monthHeaders = "";
  const step = totalMonths > 24 ? 2 : 1;
  for (let m = 1; m <= totalMonths; m += step) {
    monthHeaders += `<div style="flex:1; text-align:center; font-size:0.68rem; color:#64748b; border-right:1px dashed #e2e8f0; padding:2px 0;">M${m}</div>`;
  }

  let tasksHtml = "";
  if (tasks.length === 0) {
    tasksHtml = `<div style="text-align:center; font-size:0.8rem; color:#64748b; padding:16px;">No timeline milestones added. Define milestones in Step 5 to render here.</div>`;
  } else {
    tasksHtml = tasks.map((t, i) => {
      const color = GANTT_PALETTE[i % GANTT_PALETTE.length];
      const s = Math.max(1, Math.min(totalMonths, parseInt(t.start, 10) || 1));
      const e = Math.max(s, Math.min(totalMonths, parseInt(t.end, 10) || totalMonths));
      const name = t.name || `Phase ${i + 1}`;
      const gate = t.gate ? `<div style="font-size:0.72rem; color:${color.text}; margin-top:3px;">🏁 <strong>Go/No-Go Gate:</strong> ${escapeHtml(t.gate)}</div>` : '';

      return `
        <div>
          <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
            <strong style="color:${color.text};">${escapeHtml(name)}</strong>
            <span style="color:#64748b; font-weight:600;">Months ${s} – ${e}</span>
          </div>
          <div style="background:#e2e8f0; border-radius:6px; height:20px; overflow:hidden; position:relative;">
            <div style="position:absolute; left:${calcLeft(s)}; width:${calcWidth(s, e)}; background:${color.bar}; height:100%; border-radius:4px;"></div>
          </div>
          ${gate}
        </div>
      `;
    }).join("");
  }

  return `
    <div style="width: 100%; max-width: 880px; background: white; border-radius: 10px; border: 1px solid #cbd5e1; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 12px;">
        <div style="font-size: 0.92rem; font-weight: 800; color: #1e1b4b;">Project Execution Timeline (${totalMonths}-Month Staged Schedule)</div>
        <span style="font-size:0.75rem; color:#64748b; font-weight:600;">${tasks.length} Milestone${tasks.length === 1 ? '' : 's'}</span>
      </div>
      <div style="display:flex; border-bottom:1px solid #cbd5e1; margin-bottom:12px; background:#f8fafc; border-radius:4px;">
        ${monthHeaders}
      </div>
      <div style="display: flex; flex-direction: column; gap: 14px; font-size: 0.8rem;">
        ${tasksHtml}
      </div>
    </div>
  `;
}

function wirePipelineToggles() {
  document.querySelectorAll(".btn-pipeline-toggle").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".btn-pipeline-toggle").forEach(b => {
        b.classList.remove("active");
        b.style.background = "#f1f5f9";
        b.style.color = "#475569";
        b.style.border = "1px solid #cbd5e1";
      });
      btn.classList.add("active");
      btn.style.background = "#4338ca";
      btn.style.color = "white";
      btn.style.border = "none";

      const mode = btn.getAttribute("data-mode");
      const stage = document.getElementById("pipeline-content-stage");
      if (stage) {
        if (mode === "gantt") {
          stage.innerHTML = renderGanttTimelineHtml();
        } else {
          const aims = projectState.aims || {};
          const a1 = aims.aim1 || "(Define Aim 1 objective in Step 4)";
          const a2 = aims.aim2 || "(Define Aim 2 objective in Step 4)";
          const a3 = aims.aim3 || "(Define Aim 3 objective in Step 4)";
          const t1 = aims.aim1_title || "Phase 1 • Construction & Preparation (WP1)";
          const t2 = aims.aim2_title || "Phase 2 • Functional Testing & Evaluation (WP2)";
          const t3 = aims.aim3_title || "Phase 3 • Real-World Validation & Trials (WP3)";
          let controls = "";
          if (projectState.matrix && projectState.matrix.purple && projectState.matrix.purple.trim()) {
            controls = projectState.matrix.purple.trim();
          } else if (projectState.control_triad && (projectState.control_triad.positive || projectState.control_triad.negative)) {
            controls = `Positive: ${projectState.control_triad.positive || "Benchmark"} | Negative: ${projectState.control_triad.negative || "Vehicle control"}`;
          } else {
            controls = "Essential experimental controls: Positive benchmark, negative vehicle, and specificity standards.";
          }
          stage.innerHTML = renderPipelineCardsHtml(a1, a2, a3, t1, t2, t3, controls);
        }
      }
    });
  });
}

// ==========================================================================
// 6. Output 4: 2x2 Competitor Landscape Positioning Map
// ==========================================================================
function renderQuadrantHtml() {
  const comp = projectState.competitor_data || {};
  const incumbent = comp.principle_established || comp.incumbent_name || "Established Gold Standard";
  const emerging = comp.principle_recent || comp.emerging_name || "Recent Published Alternative";
  const proposed = comp.principle_proposed || comp.proposed_name || projectState.tool || "Proposed Solution";
  const usp = projectState.usps || comp.contribution_proposed || "(Define Unique Selling Proposition in Step 5)";

  return `
    <div class="quadrant-container">
      <div style="font-size: 0.9rem; font-weight: 800; color: #1e1b4b; margin-bottom: 8px;">2x2 Competitor Strategic Positioning Map</div>
      <div style="font-size: 0.8rem; color: #64748b; margin-bottom: 14px;">Visualizing performance vs. operational cost & complexity:</div>

      <div style="position: relative; width: 100%; height: 320px; background: #f8fafc; border: 2px solid #cbd5e1; border-radius: 8px; margin-bottom: 14px; overflow: hidden;">
        <!-- Center Axis Lines -->
        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 2px; background: #94a3b8;"></div>
        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 2px; background: #94a3b8;"></div>

        <!-- Quadrant Labels -->
        <div style="position: absolute; top: 8px; left: 12px; font-size: 0.68rem; font-weight: 800; color: #94a3b8; text-transform: uppercase;">High Cost • High Speed</div>
        <div style="position: absolute; top: 8px; right: 12px; font-size: 0.68rem; font-weight: 800; color: #16a34a; text-transform: uppercase; background: #dcfce7; padding: 2px 6px; border-radius: 4px;">★ Innovation Sweet Spot</div>
        <div style="position: absolute; bottom: 8px; left: 12px; font-size: 0.68rem; font-weight: 800; color: #94a3b8; text-transform: uppercase;">High Cost • Slow (Legacy)</div>
        <div style="position: absolute; bottom: 8px; right: 12px; font-size: 0.68rem; font-weight: 800; color: #94a3b8; text-transform: uppercase;">Low Cost • Low Performance</div>

        <!-- 1. Incumbent Point (Bottom Left) -->
        <div style="position: absolute; left: 22%; top: 68%; transform: translate(-50%, -50%); text-align: center;">
          <div style="width: 16px; height: 16px; background: #ef4444; border: 2px solid white; border-radius: 50%; margin: 0 auto; box-shadow: 0 2px 5px rgba(0,0,0,0.2);"></div>
          <div style="font-size: 0.72rem; font-weight: 700; color: #b91c1c; margin-top: 3px; max-width: 120px;">${escapeHtml(incumbent)}</div>
        </div>

        <!-- 2. Emerging Competitor Point (Middle) -->
        <div style="position: absolute; left: 52%; top: 58%; transform: translate(-50%, -50%); text-align: center;">
          <div style="width: 16px; height: 16px; background: #f59e0b; border: 2px solid white; border-radius: 50%; margin: 0 auto; box-shadow: 0 2px 5px rgba(0,0,0,0.2);"></div>
          <div style="font-size: 0.72rem; font-weight: 700; color: #b45309; margin-top: 3px; max-width: 120px;">${escapeHtml(emerging)}</div>
        </div>

        <!-- 3. Proposed Solution Point (Top Right - Sweet Spot) -->
        <div style="position: absolute; left: 80%; top: 22%; transform: translate(-50%, -50%); text-align: center;">
          <div style="width: 22px; height: 22px; background: #10b981; border: 3px solid white; border-radius: 50%; margin: 0 auto; box-shadow: 0 3px 8px rgba(16, 185, 129, 0.5); animation: pulse 2s infinite;"></div>
          <div style="font-size: 0.76rem; font-weight: 800; color: #047857; margin-top: 4px; background: white; padding: 2px 6px; border-radius: 4px; border: 1px solid #86efac; max-width: 140px;">${escapeHtml(proposed)}</div>
        </div>
      </div>

      <!-- USP Banner -->
      <div style="background: #ecfdf5; border-left: 4px solid #10b981; padding: 10px 14px; border-radius: 6px; font-size: 0.85rem;">
        <strong style="color: #047857;">Unique Selling Proposition (USP):</strong>
        <div style="color: #1e293b; margin-top: 2px;">${escapeHtml(usp)}</div>
      </div>
    </div>
  `;
}

// ==========================================================================
// 7. Output 5: Budget Donut Chart
// ==========================================================================
function renderDonutHtml() {
  const bi = projectState.budget_items || {};
  const cons = parseFloat(bi.consumables !== undefined ? bi.consumables : (document.getElementById("budget-consumables")?.value || 18500));
  const pers = parseFloat(bi.personnel !== undefined ? bi.personnel : (document.getElementById("budget-personnel")?.value || 12000));
  const util = parseFloat(bi.utilities !== undefined ? bi.utilities : (document.getElementById("budget-utilities")?.value || 4500));
  const equip = parseFloat(bi.equipment !== undefined ? bi.equipment : (document.getElementById("budget-equipment")?.value || 15000));

  const budget = [
    { category: "1. Consumables & Reagents", amount: cons },
    { category: "2. Personnel Incentives", amount: pers },
    { category: "3. Utilities & Overhead", amount: util },
    { category: "4. Specialized Equipment", amount: equip }
  ];

  let total = cons + pers + util + equip;
  if (total <= 0) total = 50000;

  const colors = ["#3b82f6", "#10b981", "#8b5cf6", "#f59e0b"];

  const cx = 140, cy = 140, rOuter = 110, rInner = 65;
  let currentAngle = 0;
  let paths = "";
  let legendItems = "";

  budget.forEach((item, idx) => {
    const amt = item.amount;
    const pct = Math.round((amt / total) * 100);
    const sliceDeg = (amt / total) * 360;
    const endAngle = currentAngle + sliceDeg;

    const startRad = (currentAngle - 90) * (Math.PI / 180);
    const endRad = (endAngle - 90) * (Math.PI / 180);

    const x1 = cx + rOuter * Math.cos(startRad);
    const y1 = cy + rOuter * Math.sin(startRad);
    const x2 = cx + rOuter * Math.cos(endRad);
    const y2 = cy + rOuter * Math.sin(endRad);

    const x3 = cx + rInner * Math.cos(endRad);
    const y3 = cy + rInner * Math.sin(endRad);
    const x4 = cx + rInner * Math.cos(startRad);
    const y4 = cy + rInner * Math.sin(startRad);

    const largeArc = sliceDeg > 180 ? 1 : 0;
    const color = colors[idx % colors.length];

    if (sliceDeg > 0.5) {
      const d = `M ${x1.toFixed(1)} ${y1.toFixed(1)} A ${rOuter} ${rOuter} 0 ${largeArc} 1 ${x2.toFixed(1)} ${y2.toFixed(1)} L ${x3.toFixed(1)} ${y3.toFixed(1)} A ${rInner} ${rInner} 0 ${largeArc} 0 ${x4.toFixed(1)} ${y4.toFixed(1)} Z`;
      paths += `<path d="${d}" fill="${color}" stroke="#ffffff" stroke-width="2" />`;
    }

    legendItems += `
      <div class="donut-legend-item" style="margin-bottom:6px; display:flex; align-items:center; gap:8px;">
        <div class="donut-color-dot" style="width:12px; height:12px; border-radius:3px; background: ${color};"></div>
        <div style="flex: 1; font-size:0.8rem;"><strong>${escapeHtml(item.category)}</strong>: $${amt.toLocaleString()} (${pct}%)</div>
      </div>
    `;

    currentAngle = endAngle;
  });

  return `
    <div style="background: white; border-radius: 12px; padding: 24px; border: 1px solid #e2e8f0; width: 100%; max-width: 680px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
      <div style="font-size: 0.9rem; font-weight: 800; color: #1e1b4b; margin-bottom: 4px;">Direct Cost Resource Allocation Donut Chart</div>
      <div style="font-size: 0.8rem; color: #64748b; margin-bottom: 18px;">Total Proposal Budget: <strong>$${total.toLocaleString()} USD</strong></div>

      <div class="donut-layout">
        <div style="position: relative; width: 280px; height: 280px;">
          <svg width="280" height="280" viewBox="0 0 280 280">
            ${paths}
          </svg>
          <div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; pointer-events: none;">
            <div style="font-size: 0.75rem; color: #64748b; font-weight: 700; text-transform: uppercase;">Total</div>
            <div style="font-size: 1.25rem; font-weight: 800; color: #1e1b4b;">$${total.toLocaleString()}</div>
          </div>
        </div>

        <div class="donut-legend" style="flex: 1; min-width: 220px;">
          ${legendItems}
          <div style="margin-top: 12px; background: #f0fdf4; border-left: 3px solid #10b981; padding: 6px 10px; border-radius: 4px; font-size: 0.75rem; color: #166534;">
            ✅ <strong>Agency Feasibility:</strong> Itemized budget tabulates real resource needs according to standard funding guidelines.
          </div>
        </div>
      </div>
    </div>
  `;
}

// ==========================================================================
// 8. Output 6: 1-Page Nature-Style Executive Pitch Sheet
// ==========================================================================
function renderPitchSheetHtml() {
  const title = projectState.title ? projectState.title.trim() : "(Project Title Defined in Step 1)";
  const pi = projectState.student_name ? projectState.student_name.trim() : "Principal Investigator & Research Team";
  
  let abs = "";
  if (projectState.abstract && projectState.abstract.trim()) {
    abs = projectState.abstract.trim();
  } else if (projectState.funnel && projectState.funnel.tier1 && projectState.funnel.tier1.trim()) {
    abs = projectState.funnel.tier1.trim() + " " + (projectState.funnel.tier4 || "");
  } else {
    abs = "(Executive abstract and project problem statement drafted in Step 3 / Step 6)";
  }

  const aims = projectState.aims || {};
  const t1 = aims.aim1_title || "Construction & Preparation";
  const t2 = aims.aim2_title || "Functional Testing & Evaluation";
  const t3 = aims.aim3_title || "Real-World Validation & Performance Trial";
  const a1 = aims.aim1 || "Initial assembly, modeling or synthesis.";
  const a2 = aims.aim2 || "Functional testing and baseline assays.";
  const a3 = aims.aim3 || "Operational validation and real-world trials.";

  let metric = "";
  if (projectState.matrix && projectState.matrix.red && projectState.matrix.red.trim()) {
    metric = projectState.matrix.red.trim();
  } else if (projectState.matrix && projectState.matrix.blue && projectState.matrix.blue.trim()) {
    metric = projectState.matrix.blue.trim();
  } else if (projectState.target && projectState.target.trim()) {
    metric = projectState.target.trim();
  } else {
    metric = "(Target quantitative success milestone)";
  }

  let impactStatement = "";
  if (projectState.impact && projectState.impact.trim()) {
    impactStatement = projectState.impact.trim();
  } else if (projectState.expected_outcomes && projectState.expected_outcomes.trim()) {
    impactStatement = projectState.expected_outcomes.trim();
  } else {
    impactStatement = "(Long-term societal and translational return formulated in Step 5)";
  }

  const bi = projectState.budget_items || {};
  const cons = parseFloat(bi.consumables !== undefined ? bi.consumables : 18500);
  const pers = parseFloat(bi.personnel !== undefined ? bi.personnel : 12000);
  const util = parseFloat(bi.utilities !== undefined ? bi.utilities : 4500);
  const equip = parseFloat(bi.equipment !== undefined ? bi.equipment : 15000);
  const total = cons + pers + util + equip;

  return `
    <div class="pitch-sheet-wrapper" id="printable-pitch-sheet">
      <!-- Header -->
      <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 3px solid #0f172a; padding-bottom: 12px; margin-bottom: 16px;">
        <div>
          <div style="font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1.5px; color: #0284c7;">
            EXECUTIVE GRANT PITCH BRIEF • BT_301 BIOTECHNOLOGY
          </div>
          <h1 style="font-size: 1.35rem; font-weight: 800; color: #0f172a; margin: 4px 0 6px 0; line-height: 1.3;">
            ${escapeHtml(title)}
          </h1>
          <div style="font-size: 0.84rem; color: #475569;">
            <strong>Principal Investigator:</strong> ${escapeHtml(pi)} | <strong>Submission Date:</strong> September 2026
          </div>
        </div>
        <div style="text-align: right;">
          <span style="background: #dbeafe; color: #1e40af; font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 999px;">
            Agency Standard
          </span>
        </div>
      </div>

      <!-- 2-Column Pitch Content -->
      <div style="display: grid; grid-template-columns: 3fr 2fr; gap: 20px; margin-bottom: 16px;">
        <div>
          <div style="font-size: 0.8rem; font-weight: 800; text-transform: uppercase; color: #334155; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px; margin-bottom: 6px;">
            Executive Abstract & Problem Statement
          </div>
          <p style="font-size: 0.85rem; color: #1e293b; line-height: 1.55;">${escapeHtml(abs)}</p>

          <div style="font-size: 0.8rem; font-weight: 800; text-transform: uppercase; color: #334155; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px; margin: 12px 0 6px 0;">
            Specific Work Packages
          </div>
          <div style="font-size: 0.82rem; color: #334155; display: flex; flex-direction: column; gap: 6px;">
            <div><strong>WP1 (${escapeHtml(t1)}):</strong> ${escapeHtml(a1)}</div>
            <div><strong>WP2 (${escapeHtml(t2)}):</strong> ${escapeHtml(a2)}</div>
            <div><strong>WP3 (${escapeHtml(t3)}):</strong> ${escapeHtml(a3)}</div>
          </div>
        </div>

        <div style="display: flex; flex-direction: column; gap: 12px;">
          <!-- Benchmark Box -->
          <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #f59e0b; padding: 12px; border-radius: 6px;">
            <div style="font-size: 0.74rem; font-weight: 800; text-transform: uppercase; color: #b45309;">Quantitative Success Milestone</div>
            <div style="font-size: 1.05rem; font-weight: 800; color: #78350f; margin-top: 4px;">${escapeHtml(metric)}</div>
          </div>

          <!-- Impact Box -->
          <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #10b981; padding: 12px; border-radius: 6px;">
            <div style="font-size: 0.74rem; font-weight: 800; text-transform: uppercase; color: #047857;">Long-Term Societal Return</div>
            <div style="font-size: 0.8rem; color: #1e293b; margin-top: 4px;">
              ${escapeHtml(impactStatement)}
            </div>
          </div>

          <!-- Budget Box -->
          <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #3b82f6; padding: 12px; border-radius: 6px;">
            <div style="font-size: 0.74rem; font-weight: 800; text-transform: uppercase; color: #1d4ed8;">Estimated Budget</div>
            <div style="font-size: 1rem; font-weight: 800; color: #1e3a8a; margin-top: 2px;">$${total.toLocaleString()} USD Direct Costs</div>
          </div>
        </div>
      </div>

      <!-- Signoff -->
      <div style="border-top: 1px solid #cbd5e1; padding-top: 10px; display: flex; justify-content: space-between; font-size: 0.78rem; color: #64748b;">
        <div>Certified for Academic Review • BT_301 Study Section</div>
        <div>Principal Investigator Signoff: ______________________</div>
      </div>
    </div>
  `;
}


function initHeaderAndNavigationEnhancements() {
  // Export Dropdown
  const exportTrigger = document.getElementById("btn-export-trigger");
  const exportMenu = document.getElementById("export-menu");
  if (exportTrigger && exportMenu) {
    exportTrigger.addEventListener("click", (e) => {
      e.stopPropagation();
      const isOpen = exportMenu.classList.toggle("open");
      exportTrigger.classList.toggle("active", isOpen);
    });

    document.addEventListener("click", (e) => {
      if (!exportTrigger.contains(e.target) && !exportMenu.contains(e.target)) {
        exportMenu.classList.remove("open");
        exportTrigger.classList.remove("active");
      }
    });

    // Close on option click
    exportMenu.querySelectorAll(".export-menu-item").forEach(item => {
      item.addEventListener("click", () => {
        exportMenu.classList.remove("open");
        exportTrigger.classList.remove("active");
      });
    });
  }

  // Paper Decoder shortcut button
  const btnPaperDecoder = document.getElementById("btn-open-paper-decoder");
  if (btnPaperDecoder) {
    btnPaperDecoder.addEventListener("click", () => {
      goToStep(2);
      const card = document.getElementById("card-paper-decoder");
      if (card) {
        setTimeout(() => {
          card.scrollIntoView({ behavior: "smooth", block: "start" });
          card.style.boxShadow = "0 0 0 3px #0284c7, 0 8px 24px rgba(0,0,0,0.1)";
          setTimeout(() => card.style.boxShadow = "", 1800);
        }, 150);
      }
    });
  }

  // Auto-assemble Title from 3 Pillars
  const btnAssembleTitle = document.getElementById("btn-assemble-title-from-pillars");
  if (btnAssembleTitle) {
    btnAssembleTitle.addEventListener("click", () => {
      const tool = (projectState.tool || document.getElementById("pillar-tool")?.value || "").trim();
      const chassis = (projectState.chassis || document.getElementById("pillar-chassis")?.value || "").trim();
      const target = (projectState.target || document.getElementById("pillar-target")?.value || "").trim();

      if (!tool || !chassis) {
        showToast("Please specify your Tool and Chassis in Pillar 1 & 2 first.");
        return;
      }

      const generatedTitle = `Engineered ${tool} in ${chassis} to Accelerate ${target || "Target Performance"} for Sustainable Bioprocess Application`;
      const titleInput = document.getElementById("proposal-title-input");
      if (titleInput) {
        titleInput.value = generatedTitle;
        projectState.title = generatedTitle;
        saveToStorage();
        updateLiveScore();
        showToast("Formula title assembled from your research pillars!");
      }
    });
  }

  // Logic Chain Collapse/Expand Toggle
  const chainToggleBtn = document.getElementById("btn-toggle-logic-chain");
  const chainTrack = document.getElementById("logic-chain-track");
  const chainSubtitle = document.querySelector(".logic-chain-subtitle");
  if (chainToggleBtn && chainTrack) {
    chainToggleBtn.addEventListener("click", () => {
      const isCollapsed = chainTrack.classList.toggle("collapsed");
      if (chainSubtitle) chainSubtitle.style.display = isCollapsed ? "none" : "inline";
      chainToggleBtn.innerHTML = isCollapsed ? "▸ Show Roadmap" : "▾ Hide Roadmap";
      chainToggleBtn.classList.toggle("collapsed", isCollapsed);
      showToast(isCollapsed ? "Logic Chain Roadmap collapsed" : "Logic Chain Roadmap expanded");
    });
  }
}


// ==========================================================================
// STUDENT AUTHENTICATION & ACCESS CONTROLLER (GATE & MODAL)
// ==========================================================================

let currentAuthUser = null;

function initAuthManager() {
  // Check active session on load
  checkAuthStatus();

  // --- Gate Tabs & Forms ---
  const gateTabIn = document.getElementById("gate-tab-signin");
  const gateTabReg = document.getElementById("gate-tab-register");
  if (gateTabIn) gateTabIn.addEventListener("click", () => switchGateTab("signin"));
  if (gateTabReg) gateTabReg.addEventListener("click", () => switchGateTab("register"));

  const gateFormIn = document.getElementById("gate-form-signin");
  if (gateFormIn) {
    gateFormIn.addEventListener("submit", (e) => {
      e.preventDefault();
      const sid = (document.getElementById("gate-signin-id").value || "").trim();
      const pwd = (document.getElementById("gate-signin-pwd").value || "").trim();
      if (!sid || !pwd) {
        showGateAlert("Please enter both Student ID and Password.", "error");
        return;
      }
      handleSignInSubmit(sid, pwd, true);
    });
  }

  const gateFormReg = document.getElementById("gate-form-register");
  if (gateFormReg) {
    gateFormReg.addEventListener("submit", (e) => {
      e.preventDefault();
      const sid = (document.getElementById("gate-reg-id").value || "").trim();
      const sname = (document.getElementById("gate-reg-name").value || "").trim();
      const pwd = (document.getElementById("gate-reg-pwd").value || "").trim();
      const pwdConf = (document.getElementById("gate-reg-pwd-confirm").value || "").trim();

      if (!sid || !sname || !pwd) {
        showGateAlert("Please fill in all required fields.", "error");
        return;
      }
      if (pwd.length < 4) {
        showGateAlert("Password must be at least 4 characters.", "error");
        return;
      }
      if (pwd !== pwdConf) {
        showGateAlert("Passwords do not match. Please re-check.", "error");
        return;
      }
      handleRegisterSubmit(sid, sname, pwd, true);
    });
  }

  // Gate Quick-Fill Chips (Pre-fill Student ID)
  document.querySelectorAll(".btn-quick-fill").forEach(btn => {
    btn.addEventListener("click", () => {
      const sid = btn.getAttribute("data-id");
      const idInput = document.getElementById("gate-signin-id");
      const pwdInput = document.getElementById("gate-signin-pwd");
      if (idInput) idInput.value = sid;
      if (pwdInput) {
        pwdInput.focus();
      }
    });
  });

  // Secret Faculty Access Shortcut: Ctrl + Shift + F
  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === "F" || e.key === "f")) {
      e.preventDefault();
      window.location.href = "/faculty";
    }
  });

  // --- Modal Wiring (Fallback / Account Switch) ---
  const btnOpenModal = document.getElementById("btn-open-auth-modal");
  if (btnOpenModal) {
    btnOpenModal.addEventListener("click", () => openAuthModal("signin"));
  }

  const btnCloseModal = document.getElementById("btn-auth-close");
  if (btnCloseModal) {
    btnCloseModal.addEventListener("click", closeAuthModal);
  }

  const overlay = document.getElementById("auth-modal-overlay");
  if (overlay) {
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) closeAuthModal();
    });
  }

  const tabIn = document.getElementById("tab-btn-signin");
  const tabReg = document.getElementById("tab-btn-register");
  if (tabIn) tabIn.addEventListener("click", () => switchAuthTab("signin"));
  if (tabReg) tabReg.addEventListener("click", () => switchAuthTab("register"));

  const formIn = document.getElementById("form-auth-signin");
  if (formIn) {
    formIn.addEventListener("submit", (e) => {
      e.preventDefault();
      const sid = (document.getElementById("signin-student-id").value || "").trim();
      const pwd = (document.getElementById("signin-password").value || "").trim();
      if (!sid || !pwd) {
        showAuthAlert("Please enter both Student ID and Password.", "error");
        return;
      }
      handleSignInSubmit(sid, pwd, false);
    });
  }

  const formReg = document.getElementById("form-auth-register");
  if (formReg) {
    formReg.addEventListener("submit", (e) => {
      e.preventDefault();
      const sid = (document.getElementById("reg-student-id").value || "").trim();
      const sname = (document.getElementById("reg-student-name").value || "").trim();
      const pwd = (document.getElementById("reg-password").value || "").trim();
      const pwdConf = (document.getElementById("reg-password-confirm").value || "").trim();

      if (!sid || !sname || !pwd) {
        showAuthAlert("Please fill in all required fields.", "error");
        return;
      }
      if (pwd.length < 4) {
        showAuthAlert("Password must be at least 4 characters.", "error");
        return;
      }
      if (pwd !== pwdConf) {
        showAuthAlert("Passwords do not match.", "error");
        return;
      }
      handleRegisterSubmit(sid, sname, pwd, false);
    });
  }

  // Universal Show/Hide Password Toggles (both modal & gate)
  document.querySelectorAll(".btn-toggle-pwd").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const targetId = btn.getAttribute("data-target");
      const input = document.getElementById(targetId);
      if (input) {
        if (input.type === "password") {
          input.type = "text";
          btn.innerText = "🙈";
        } else {
          input.type = "password";
          btn.innerText = "👁️";
        }
      }
    });
  });

  // User Profile Dropdown & Logout
  const profileTrigger = document.getElementById("btn-user-profile-trigger");
  const menu = document.getElementById("auth-user-menu");
  if (profileTrigger && menu) {
    profileTrigger.addEventListener("click", (e) => {
      e.stopPropagation();
      menu.classList.toggle("show");
    });

    document.addEventListener("click", (e) => {
      if (!profileTrigger.contains(e.target) && !menu.contains(e.target)) {
        menu.classList.remove("show");
      }
    });
  }

  const btnLogout = document.getElementById("btn-action-logout");
  if (btnLogout) {
    btnLogout.addEventListener("click", handleLogout);
  }

  const btnDirectLogout = document.getElementById("btn-student-direct-logout");
  if (btnDirectLogout) {
    btnDirectLogout.addEventListener("click", handleLogout);
  }

  // Cloud Draft Sync Button
  const btnSyncDraft = document.getElementById("btn-sync-server-draft");
  if (btnSyncDraft) {
    btnSyncDraft.addEventListener("click", async () => {
      await saveStudentDraftToServer(true);
    });
  }
}

async function checkAuthStatus() {
  try {
    const resp = await fetch("/api/auth/me");
    const res = await resp.json();
    if (res.authenticated && res.user) {
      setAuthenticatedUser(res.user, res.draft);
    } else {
      setUnauthenticatedUser();
    }
  } catch (e) {
    console.error("Failed to check auth status", e);
    setUnauthenticatedUser();
  }
}

function setAuthenticatedUser(user, draftData) {
  currentAuthUser = user;

  // 1. Hide the auth gate
  const gate = document.getElementById("student-auth-gate");
  if (gate) gate.style.display = "none";

  // 2. Reveal the workspace!
  const ws = document.getElementById("studio-workspace");
  if (ws) ws.style.display = "grid";

  // 3. Reveal top navbar tools
  const viewSelector = document.getElementById("view-mode-selector");
  if (viewSelector) viewSelector.style.display = "flex";
  const expDropdown = document.getElementById("export-dropdown-wrapper");
  if (expDropdown) expDropdown.style.display = "block";
  const btnDecoder = document.getElementById("btn-open-paper-decoder");
  if (btnDecoder) btnDecoder.style.display = "inline-flex";

  // 4. Update navbar profile
  const btnOpen = document.getElementById("btn-open-auth-modal");
  const wrap = document.getElementById("auth-user-dropdown-wrap");
  if (btnOpen) btnOpen.style.display = "none";
  if (wrap) wrap.style.display = "block";

  const dispName = document.getElementById("user-display-name");
  if (dispName) dispName.innerText = user.student_id;

  const menuName = document.getElementById("menu-student-name");
  if (menuName) menuName.innerText = user.student_name;

  const menuId = document.getElementById("menu-student-id");
  if (menuId) menuId.innerText = user.student_id;

  const saveStatus = document.getElementById("save-status");
  if (saveStatus) saveStatus.innerText = "● Cloud Auto-Sync Active";

  // 5. Prefill & lock Student ID input on Proposal Meta Card
  const idInput = document.getElementById("student-id-input");
  if (idInput) {
    idInput.value = user.student_id;
    idInput.readOnly = true;
    idInput.style.background = "#f1f5f9";
  }

  const nameInput = document.getElementById("student-name-input");
  if (nameInput && (!projectState.student_name || projectState.student_name.includes("BT_301"))) {
    nameInput.value = user.student_name;
    projectState.student_name = user.student_name;
  }

  projectState.student_id = user.student_id;

  // 6. If cloud draft exists, apply it
  if (draftData) {
    applyCloudDraftToWorkspace(draftData);
  }
}

function setUnauthenticatedUser() {
  currentAuthUser = null;

  // 1. Hide the workspace so signed-out students CANNOT see the page itself!
  const ws = document.getElementById("studio-workspace");
  if (ws) ws.style.display = "none";

  // 2. Hide top actions that only apply to active workspace
  const viewSelector = document.getElementById("view-mode-selector");
  if (viewSelector) viewSelector.style.display = "none";
  const expDropdown = document.getElementById("export-dropdown-wrapper");
  if (expDropdown) expDropdown.style.display = "none";
  const btnDecoder = document.getElementById("btn-open-paper-decoder");
  if (btnDecoder) btnDecoder.style.display = "none";

  // 3. Show the dedicated Student Auth Gate
  const gate = document.getElementById("student-auth-gate");
  if (gate) gate.style.display = "flex";

  // 4. Update navbar indicators
  const btnOpen = document.getElementById("btn-open-auth-modal");
  const wrap = document.getElementById("auth-user-dropdown-wrap");
  if (btnOpen) btnOpen.style.display = "none";
  if (wrap) wrap.style.display = "none";

  const saveStatus = document.getElementById("save-status");
  if (saveStatus) saveStatus.innerText = "🔒 Sign In Required to Access Workspace";

  const idInput = document.getElementById("student-id-input");
  if (idInput) {
    idInput.readOnly = false;
    idInput.style.background = "";
  }
}

function switchGateTab(tab) {
  const tabIn = document.getElementById("gate-tab-signin");
  const tabReg = document.getElementById("gate-tab-register");
  const formIn = document.getElementById("gate-form-signin");
  const formReg = document.getElementById("gate-form-register");

  hideGateAlert();

  if (tab === "signin") {
    if (tabIn) tabIn.classList.add("active");
    if (tabReg) tabReg.classList.remove("active");
    if (formIn) formIn.style.display = "block";
    if (formReg) formReg.style.display = "none";
    setTimeout(() => {
      const el = document.getElementById("gate-signin-id");
      if (el) el.focus();
    }, 100);
  } else {
    if (tabReg) tabReg.classList.add("active");
    if (tabIn) tabIn.classList.remove("active");
    if (formReg) formReg.style.display = "block";
    if (formIn) formIn.style.display = "none";
    setTimeout(() => {
      const el = document.getElementById("gate-reg-id");
      if (el) el.focus();
    }, 100);
  }
}

function showGateAlert(message, type = "error") {
  const banner = document.getElementById("gate-auth-alert-banner");
  if (banner) {
    banner.className = `auth-alert-banner ${type}`;
    banner.innerText = message;
    banner.style.display = "block";
  }
}

function hideGateAlert() {
  const banner = document.getElementById("gate-auth-alert-banner");
  if (banner) banner.style.display = "none";
}

function openAuthModal(tab = "signin") {
  const overlay = document.getElementById("auth-modal-overlay");
  if (overlay) overlay.style.display = "flex";
  switchAuthTab(tab);
  hideAuthAlert();
}

function closeAuthModal() {
  const overlay = document.getElementById("auth-modal-overlay");
  if (overlay) overlay.style.display = "none";
}

function switchAuthTab(tab) {
  const tabIn = document.getElementById("tab-btn-signin");
  const tabReg = document.getElementById("tab-btn-register");
  const formIn = document.getElementById("form-auth-signin");
  const formReg = document.getElementById("form-auth-register");

  hideAuthAlert();

  if (tab === "signin") {
    if (tabIn) tabIn.classList.add("active");
    if (tabReg) tabReg.classList.remove("active");
    if (formIn) formIn.style.display = "block";
    if (formReg) formReg.style.display = "none";
    setTimeout(() => {
      const el = document.getElementById("signin-student-id");
      if (el) el.focus();
    }, 100);
  } else {
    if (tabReg) tabReg.classList.add("active");
    if (tabIn) tabIn.classList.remove("active");
    if (formReg) formReg.style.display = "block";
    if (formIn) formIn.style.display = "none";
    setTimeout(() => {
      const el = document.getElementById("reg-student-id");
      if (el) el.focus();
    }, 100);
  }
}

function showAuthAlert(message, type = "error") {
  const banner = document.getElementById("auth-alert-banner");
  if (banner) {
    banner.className = `auth-alert-banner ${type}`;
    banner.innerText = message;
    banner.style.display = "block";
  }
}

function hideAuthAlert() {
  const banner = document.getElementById("auth-alert-banner");
  if (banner) banner.style.display = "none";
}

async function handleSignInSubmit(studentId, password, isGate = false) {
  const btn = isGate ? document.getElementById("btn-gate-submit-signin") : document.getElementById("btn-submit-signin");
  if (btn) btn.disabled = true;

  try {
    const resp = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ student_id: studentId, password: password })
    });
    const res = await resp.json();

    if (res.success && res.user) {
      setAuthenticatedUser(res.user, res.draft);
      closeAuthModal();
      showToast(`Welcome back, ${res.user.student_name}!`);
    } else {
      const msg = res.error || "Sign in failed. Check your ID and password.";
      if (isGate) showGateAlert(msg, "error");
      else showAuthAlert(msg, "error");
    }
  } catch (e) {
    const msg = "Network error signing in. Please check connection.";
    if (isGate) showGateAlert(msg, "error");
    else showAuthAlert(msg, "error");
  } finally {
    if (btn) btn.disabled = false;
  }
}

async function handleRegisterSubmit(studentId, studentName, password, isGate = false) {
  const btn = isGate ? document.getElementById("btn-gate-submit-register") : document.getElementById("btn-submit-register");
  if (btn) btn.disabled = true;

  try {
    const resp = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        student_id: studentId,
        student_name: studentName,
        password: password
      })
    });
    const res = await resp.json();

    if (res.success && res.user) {
      projectState.student_id = res.user.student_id;
      projectState.student_name = res.user.student_name;
      setAuthenticatedUser(res.user);
      await saveStudentDraftToServer(false);
      closeAuthModal();
      showToast(`Account created! Welcome, ${res.user.student_name}!`);
    } else {
      const msg = res.error || "Registration failed. Try a different Student ID.";
      if (isGate) showGateAlert(msg, "error");
      else showAuthAlert(msg, "error");
    }
  } catch (e) {
    const msg = "Network error creating account.";
    if (isGate) showGateAlert(msg, "error");
    else showAuthAlert(msg, "error");
  } finally {
    if (btn) btn.disabled = false;
  }
}

async function handleLogout() {
  try {
    await fetch("/api/auth/logout", { method: "POST" });
    setUnauthenticatedUser();
    const menu = document.getElementById("auth-user-menu");
    if (menu) menu.classList.remove("show");
    showToast("Signed out successfully. Please sign in to access your workspace.");
  } catch (e) {
    console.error("Logout error", e);
  }
}

function applyCloudDraftToWorkspace(draft) {
  if (!draft) return;
  Object.assign(projectState, draft);
  saveToStorage();

  // Populate HTML input fields
  const setVal = (id, val) => {
    const el = document.getElementById(id);
    if (el && val !== undefined) el.value = val;
  };

  setVal("student-name-input", projectState.student_name);
  setVal("student-id-input", projectState.student_id);
  setVal("proposal-title-input", projectState.title);
  setVal("abstract-input", projectState.abstract);
  setVal("methodology-input", projectState.methodology);
  setVal("timeplan-input", projectState.time_plan);
  setVal("budget-input", projectState.budget);
  setVal("references-input", projectState.references);

  // Pillars
  setVal("chassis-input", projectState.chassis);
  setVal("tool-input", projectState.tool);
  setVal("target-input", projectState.target);

  // Funnel
  const fn = projectState.funnel || {};
  setVal("funnel-tier1", fn.tier1);
  setVal("funnel-tier2", fn.tier2);
  setVal("funnel-tier3", fn.tier3);
  setVal("funnel-tier4", fn.tier4);

  // Aims
  const aims = projectState.aims || {};
  setVal("aim-overarching", aims.overarching);
  setVal("aim1-input", aims.aim1);
  setVal("aim2-input", aims.aim2);
  setVal("aim3-input", aims.aim3);

  // Matrix
  const mx = projectState.matrix || {};
  setVal("matrix-blue", mx.blue);
  setVal("matrix-green", mx.green);
  setVal("matrix-yellow", mx.yellow);
  setVal("matrix-purple", mx.purple);

  // Impact
  const imp = projectState.impact_data || {};
  setVal("impact-academic", imp.academic);
  setVal("impact-economic", imp.economic);
  setVal("impact-societal", imp.societal);

  // Competitors
  const comp = projectState.competitor_data || {};
  setVal("comp-incumbent", comp.incumbent_name);
  setVal("comp-speed", comp.speed_metric);
  setVal("comp-cost", comp.cost_metric);
  setVal("comp-lod", comp.lod_metric);
  setVal("comp-portability", comp.portability_metric);
  setVal("comp-usp", comp.usp);

  // SWOT
  const swot = projectState.swot || {};
  setVal("swot-s", swot.s);
  setVal("swot-w", swot.w);
  setVal("swot-o", swot.o);
  setVal("swot-t", swot.t);

  // Aims Contingencies (B1)
  const cont = projectState.aims_contingencies || {};
  setVal("aim1-fallback", cont.aim1_fallback);
  setVal("aim2-fallback", cont.aim2_fallback);
  setVal("aim3-fallback", cont.aim3_fallback);

  // Control Triad (B2)
  const triad = projectState.control_triad || {};
  setVal("control-negative", triad.negative);
  setVal("control-positive", triad.positive);
  setVal("control-specificity", triad.specificity);

  // Biotech FMEA Matrix (B3)
  const fmea = projectState.biotech_risk_matrix || {};
  setVal("fmea-off-target", fmea.off_target);
  setVal("fmea-toxicity", fmea.toxicity);
  setVal("fmea-solubility", fmea.solubility);
  setVal("fmea-biosafety", fmea.biosafety);

  // Lock State (Part 3.3)
  if (typeof applyLockStateToUI === "function") {
    applyLockStateToUI(Boolean(projectState.is_locked_for_grading));
  }

  // Instructor Review Banner (Part 3.2 - NO GRADES)
  if (typeof renderInstructorReviewBanner === "function") {
    renderInstructorReviewBanner(projectState.faculty_review);
  }

  updateLiveScore();
  updateLogicChainUI();
}

async function saveStudentDraftToServer(userInitiated = false) {
  const sid = (projectState.student_id || (currentAuthUser ? currentAuthUser.student_id : "") || "ST-2026-01").trim();
  const btn = document.getElementById("btn-sync-server-draft");
  const saveIndicator = document.getElementById("save-status");

  if (btn && userInitiated) {
    btn.disabled = true;
    btn.innerHTML = `<span>⏳</span> <span>Saving...</span>`;
  }

  try {
    const resp = await fetch("/api/student/save_draft", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        student_id: sid,
        student_data: projectState
      })
    });
    const res = await resp.json();
    if (res.success) {
      if (saveIndicator) saveIndicator.innerText = `● Saved to cloud (${res.updated_at || "now"})`;
      if (userInitiated) showToast(`Draft saved to database for ${res.student_id}!`);
    }
  } catch (e) {
    console.error("Cloud save failed", e);
  } finally {
    if (btn && userInitiated) {
      btn.disabled = false;
      btn.innerHTML = `<span>💾</span> <span class="btn-save-text">Save Draft</span>`;
    }
  }
}

// ============================================================================
// PART 1 & 3: GOVERNANCE, PREREQUISITE GATING & PERSISTENT GUIDANCE
// ============================================================================

function initGovernanceAndGuidance() {
  // 1. Wire Proposal Lock Toggle Switch (Part 3.3)
  const btnLock = document.getElementById("btn-toggle-draft-lock");
  if (btnLock) {
    btnLock.addEventListener("click", handleToggleProposalLock);
  }

  // 2. Wire Next Action Jump Button (A3)
  const btnJump = document.getElementById("btn-floating-jump-action");
  if (btnJump) {
    btnJump.addEventListener("click", () => {
      const step = parseInt(btnJump.getAttribute("data-target-step") || "1");
      const fieldId = btnJump.getAttribute("data-target-field");
      // Ensure we switch to studio view before jumping
      setViewMode("studio");
      goToStep(step);
      if (fieldId) {
        setTimeout(() => {
          const el = document.getElementById(fieldId);
          if (el) {
            el.scrollIntoView({ behavior: "smooth", block: "center" });
            el.focus();
            el.style.boxShadow = "0 0 0 3px rgba(79, 70, 229, 0.4)";
            setTimeout(() => el.style.boxShadow = "", 1800);
          }
        }, 300);
      }
    });
  }

  // Dismiss button for floating guidance bar
  const btnDismissBar = document.getElementById("btn-dismiss-floating-bar");
  if (btnDismissBar) {
    btnDismissBar.addEventListener("click", () => {
      const bar = document.getElementById("studio-floating-guidance-bar");
      if (bar) bar.style.display = "none";
      sessionStorage.setItem("biowriter_guidance_dismissed", "true");
      showToast("Milestone guidance bar hidden for this session.");
    });
  }

  // 3. Wire Instructor Evaluation Memo Modal (Part 3.2)
  const btnViewMemo = document.getElementById("btn-view-faculty-memo");
  const modalMemo = document.getElementById("modal-instructor-memo");
  const btnCloseMemo = document.getElementById("btn-close-memo-modal");
  const btnDismissMemo = document.getElementById("btn-dismiss-memo-modal");
  const btnCopyMemo = document.getElementById("btn-copy-memo-modal");

  if (btnViewMemo && modalMemo) {
    btnViewMemo.addEventListener("click", () => {
      modalMemo.style.display = "flex";
    });
  }

  const closeMemoModal = () => {
    if (modalMemo) modalMemo.style.display = "none";
  };

  if (btnCloseMemo) btnCloseMemo.addEventListener("click", closeMemoModal);
  if (btnDismissMemo) btnDismissMemo.addEventListener("click", closeMemoModal);
  if (btnCopyMemo) {
    btnCopyMemo.addEventListener("click", () => {
      const content = document.getElementById("memo-modal-content");
      if (content) {
        navigator.clipboard.writeText(content.innerText).then(() => {
          showToast("Evaluation Memo copied to clipboard!");
        });
      }
    });
  }

  // Initial evaluations
  evaluateStepPrerequisites();
  updateNextActionGuidance();
}

async function handleToggleProposalLock() {
  const currentLock = Boolean(projectState.is_locked_for_grading);
  const nextLock = !currentLock;
  projectState.is_locked_for_grading = nextLock;

  applyLockStateToUI(nextLock);
  saveToStorage();

  try {
    const sid = projectState.student_id || (currentAuthUser ? currentAuthUser.student_id : "");
    await fetch("/api/student/toggle_lock", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        student_id: sid,
        is_locked: nextLock
      })
    });
    showToast(nextLock ? "🔒 Proposal locked for official grading!" : "🔓 Proposal unlocked for revisions.");
  } catch (e) {
    console.error("Error updating lock state", e);
  }
}

function applyLockStateToUI(isLocked) {
  const btnLock = document.getElementById("btn-toggle-draft-lock");
  const lockIcon = document.getElementById("lock-icon");
  const lockLabel = document.getElementById("lock-label");
  const lockSubtext = document.getElementById("lock-subtext");
  const lockedBanner = document.getElementById("draft-locked-banner");
  const canvas = document.getElementById("wizard-steps-pane");

  if (btnLock && lockIcon && lockLabel) {
    if (isLocked) {
      btnLock.classList.add("locked");
      lockIcon.innerText = "🔒";
      lockLabel.innerText = "Locked for Grading";
      if (lockSubtext) lockSubtext.innerText = "Submission Frozen";
    } else {
      btnLock.classList.remove("locked");
      lockIcon.innerText = "🔓";
      lockLabel.innerText = "Lock for Grading";
      if (lockSubtext) lockSubtext.innerText = "Editable draft";
    }
  }

  if (lockedBanner) {
    lockedBanner.style.display = isLocked ? "flex" : "none";
  }

  if (canvas) {
    if (isLocked) canvas.classList.add("proposal-canvas-locked");
    else canvas.classList.remove("proposal-canvas-locked");

    const inputs = canvas.querySelectorAll("input:not(.always-editable), textarea:not(.always-editable), select:not(.always-editable)");
    inputs.forEach(inp => {
      inp.readOnly = isLocked;
      if (inp.tagName === "SELECT") inp.disabled = isLocked;
    });
  }
}

function renderInstructorReviewBanner(review) {
  const banner = document.getElementById("instructor-review-banner");
  if (!banner) return;

  if (!review) {
    banner.style.display = "none";
    return;
  }

  banner.style.display = "block";

  const standingEl = document.getElementById("review-banner-standing");
  if (standingEl) {
    const standing = review.standing || "🌟 Grant-Ready";
    standingEl.innerText = standing;
    if (standing.includes("Grant-Ready") || standing.includes("Excellent")) {
      standingEl.className = "status-pill status-grant-ready";
    } else if (standing.includes("Minor")) {
      standingEl.className = "status-pill status-minor-rev";
    } else {
      standingEl.className = "status-pill status-major-rev";
    }
  }

  const metaEl = document.getElementById("review-banner-meta");
  if (metaEl) {
    metaEl.innerText = `Evaluated on ${review.dispatched_at || "Recently"} • Official Faculty Directive`;
  }

  const listEl = document.getElementById("review-banner-action-list");
  const progressBadge = document.getElementById("revision-progress-badge");
  const progressBarFill = document.getElementById("revision-progress-bar-fill");

  if (!Array.isArray(projectState.completed_feedback_items)) {
    projectState.completed_feedback_items = [];
  }

  let items = [];
  if (Array.isArray(review.action_items) && review.action_items.length > 0) {
    items = review.action_items;
  } else if (review.manual_notes) {
    items = [review.manual_notes];
  }

  if (listEl) {
    if (items.length > 0) {
      listEl.innerHTML = "";
      items.forEach((item, idx) => {
        const isDone = projectState.completed_feedback_items.includes(String(idx));
        const itemRow = document.createElement("div");
        itemRow.className = "checklist-item-row";
        itemRow.style.cssText = `display: flex; align-items: flex-start; gap: 10px; padding: 10px 12px; border-radius: 8px; background: ${isDone ? '#f0fdf4' : '#f8fafc'}; border: 1px solid ${isDone ? '#bbf7d0' : '#e2e8f0'}; transition: all 0.2s ease;`;

        itemRow.innerHTML = `
          <input type="checkbox" id="chk-action-item-${idx}" data-idx="${idx}" ${isDone ? 'checked' : ''} style="margin-top: 3px; width: 17px; height: 17px; cursor: pointer; accent-color: #16a34a; flex-shrink: 0;">
          <label for="chk-action-item-${idx}" style="flex: 1; cursor: pointer; font-size: 0.85rem; line-height: 1.45; color: ${isDone ? '#166534' : '#1e293b'}; text-decoration: ${isDone ? 'line-through' : 'none'}; font-weight: ${isDone ? '500' : '600'};">
            ${escapeHtml(item)}
          </label>
          <span class="status-pill" style="font-size: 0.68rem; padding: 2px 8px; background: ${isDone ? '#dcfce7' : '#fef3c7'}; color: ${isDone ? '#15803d' : '#92400e'}; border: 1px solid ${isDone ? '#86efac' : '#fde68a'}; font-weight: 700; white-space: nowrap; flex-shrink: 0;">
            ${isDone ? '✅ Done' : '⏳ Needs Work'}
          </span>
        `;

        const chk = itemRow.querySelector("input[type='checkbox']");
        chk.addEventListener("change", async () => {
          const checked = chk.checked;
          const idxStr = String(idx);
          if (checked) {
            if (!projectState.completed_feedback_items.includes(idxStr)) {
              projectState.completed_feedback_items.push(idxStr);
            }
          } else {
            projectState.completed_feedback_items = projectState.completed_feedback_items.filter(x => x !== idxStr);
          }
          // Re-render checklist to update item styling and progress bar
          renderFacultyReviewStatus(review);
          // Auto-save to cloud draft
          await saveStudentDraftToServer(false);
        });

        listEl.appendChild(itemRow);
      });

      // Update progress badge and progress bar
      const doneCount = projectState.completed_feedback_items.filter(idxStr => Number(idxStr) < items.length).length;
      const totalCount = items.length;
      const pct = Math.round((doneCount / totalCount) * 100);

      if (progressBadge) {
        progressBadge.innerText = `${doneCount} of ${totalCount} Addressed (${pct}%)`;
        progressBadge.style.background = doneCount === totalCount ? "#dcfce7" : "#e0e7ff";
        progressBadge.style.color = doneCount === totalCount ? "#15803d" : "#4338ca";
        progressBadge.style.borderColor = doneCount === totalCount ? "#86efac" : "#c7d2fe";
      }

      if (progressBarFill) {
        progressBarFill.style.width = `${pct}%`;
        progressBarFill.style.background = doneCount === totalCount ? "#16a34a" : "#4f46e5";
      }
    } else {
      listEl.innerHTML = '<div style="font-size: 0.82rem; color: #64748b;">All proposal milestones reviewed and accepted for oral defense preparation.</div>';
      if (progressBadge) progressBadge.innerText = "Accepted";
      if (progressBarFill) progressBarFill.style.width = "100%";
    }
  }

  // Populate memo modal contents
  const memoModalContent = document.getElementById("memo-modal-content");
  if (memoModalContent) {
    memoModalContent.innerText = review.memo_text || review.manual_notes || "Official BT_301 Evaluation Memo recorded.";
  }

  const memoModalStudent = document.getElementById("memo-modal-student-name");
  if (memoModalStudent) {
    memoModalStudent.innerText = projectState.student_name || "Proposal Evaluation";
  }

  const memoModalDate = document.getElementById("memo-modal-date");
  if (memoModalDate) {
    memoModalDate.innerText = review.dispatched_at || "Recently Reviewed";
  }

  const memoModalBadge = document.getElementById("memo-modal-standing-badge");
  if (memoModalBadge) {
    memoModalBadge.innerText = review.standing || "Evaluated";
  }
}

function isStepUnlocked(s) {
  if (s <= 1) return true;
  if (s === 2) {
    return Boolean(projectState.title && (projectState.chassis || projectState.system) && projectState.tool);
  }
  if (s === 3) {
    return isStepUnlocked(2) && Boolean(projectState.matrix && (projectState.matrix.blue || projectState.matrix.yellow || projectState.matrix.green || projectState.matrix.citation));
  }
  if (s === 4) {
    const fn = projectState.funnel || {};
    return isStepUnlocked(3) && Boolean(fn.tier1 && fn.tier3 && fn.tier4);
  }
  if (s === 5) {
    const aims = projectState.aims || {};
    return isStepUnlocked(4) && Boolean(aims.aim1 && aims.aim2 && projectState.methodology && projectState.methodology.length > 30);
  }
  if (s === 6) {
    return isStepUnlocked(5) && Boolean(projectState.usps && projectState.swot && projectState.swot.strengths);
  }
  return true;
}

function evaluateStepPrerequisites() {
  for (let s = 1; s <= 6; s++) {
    const badge = document.getElementById(`prereq-badge-${s}`);
    const sideItem = document.getElementById(`side-step-${s}`);
    if (!badge || !sideItem) continue;

    const unlocked = isStepUnlocked(s);
    if (s === currentStep) {
      badge.innerText = "● Active";
      badge.className = "prereq-badge unlocked";
      sideItem.classList.remove("prereq-locked");
    } else if (unlocked) {
      badge.innerText = "🔓 Ready";
      badge.className = "prereq-badge unlocked";
      sideItem.classList.remove("prereq-locked");
    } else {
      badge.innerText = `🔒 Step ${s - 1} Req`;
      badge.className = "prereq-badge";
      sideItem.classList.add("prereq-locked");
    }
  }
}

function updateNextActionGuidance(nodes = 0, pct = 0) {
  const bar = document.getElementById("studio-floating-guidance-bar");
  const actionText = document.getElementById("floating-next-action-text");
  const progressPill = document.getElementById("floating-progress-pill");
  const jumpBtn = document.getElementById("btn-floating-jump-action");

  if (!bar || !actionText || !progressPill || !jumpBtn) return;

  // Auto-hide if dismissed, or if breakthroughs view is active, or if outside studio mode
  const isDismissed = sessionStorage.getItem("biowriter_guidance_dismissed") === "true";
  const btView = document.getElementById("view-container-breakthroughs");
  const isBtVisible = btView && btView.style.display !== "none";
  const authModal = document.getElementById("auth-modal-overlay");
  const isAuthOpen = authModal && authModal.style.display !== "none";
  const btnStudio = document.getElementById("btn-view-studio");
  const isStudioActive = btnStudio && btnStudio.classList.contains("active");

  if (isDismissed || isBtVisible || isAuthOpen || !currentAuthUser || !isStudioActive) {
    bar.style.display = "none";
    return;
  }

  bar.style.display = "block";

  progressPill.innerText = `Milestones: ${nodes}/10 (${pct}%)`;

  // Determine immediate next unfulfilled scientific task
  let nextStep = 1;
  let nextField = "pillar-chassis";
  let prompt = "Define your Host Chassis and Molecular Tool in Step 1";

  if (!projectState.chassis || !projectState.tool) {
    nextStep = 1; nextField = "pillar-chassis"; prompt = "Specify Host Chassis & Molecular Tool in Step 1";
  } else if (!projectState.title) {
    nextStep = 1; nextField = "proposal-title-input"; prompt = "Formulate Tripartite Scientific Title in Step 1";
  } else if (!projectState.matrix || (!projectState.matrix.blue && !projectState.matrix.yellow)) {
    nextStep = 2; nextField = "matrix-blue"; prompt = "Record Quantitative Benchmark in Literature Lab (Step 2)";
  } else if (!projectState.funnel || !projectState.funnel.tier1) {
    nextStep = 3; nextField = "funnel-tier1"; prompt = "Draft Global Burden Statement (Tier 1) in Step 3";
  } else if (!projectState.funnel || !projectState.funnel.tier3) {
    nextStep = 3; nextField = "funnel-tier3"; prompt = "Identify Biophysical Knowledge Gap (Tier 3) in Step 3";
  } else if (!projectState.funnel || !projectState.funnel.tier4) {
    nextStep = 3; nextField = "funnel-tier4"; prompt = "Formulate Mechanistic Hypothesis (Tier 4) in Step 3";
  } else if (!projectState.aims || !projectState.aims.aim1 || !projectState.aims.aim2) {
    nextStep = 4; nextField = "aim1-input"; prompt = "Decouple 3 Specific Objectives in Step 4";
  } else if (!projectState.control_triad || !projectState.control_triad.negative) {
    nextStep = 4; nextField = "control-negative"; prompt = "Specify The Control Triad (Negative & Positive) in Step 4";
  } else if (!projectState.aims_contingencies || !projectState.aims_contingencies.aim1_fallback) {
    nextStep = 4; nextField = "aim1-fallback"; prompt = "Formulate Aim 1 Fallback Contingency in Step 4";
  } else if (!projectState.usps) {
    nextStep = 5; nextField = "usps-input"; prompt = "Synthesize Unique Selling Proposition (USP) in Step 5";
  } else if (!projectState.biotech_risk_matrix || !projectState.biotech_risk_matrix.off_target) {
    nextStep = 5; nextField = "fmea-off-target"; prompt = "Complete Biotech FMEA Risk Matrix in Step 5";
  } else if (!projectState.abstract || projectState.abstract.length < 50) {
    nextStep = 6; nextField = "abstract-input"; prompt = "Synthesize 250-word Structured Abstract in Step 6";
  } else {
    nextStep = 6; nextField = "abstract-input"; prompt = "🌟 All 10 Milestones Complete! Lock Proposal for Official Grading.";
  }

  actionText.innerText = prompt;
  jumpBtn.setAttribute("data-target-step", nextStep);
  jumpBtn.setAttribute("data-target-field", nextField);
}

// ==========================================================================
// BIOTECHNOLOGY BREAKTHROUGHS RADAR MODULE
// Designed & Authored by Maya Abdelrazek & Youssef Aboulkheir
// ==========================================================================

let btCatalogState = [];
let btStorageFilter = "all";
let btCategoryFilter = "All";
let btPresentationMode = "edu"; // 'edu' or 'tech'
let btSearchQuery = "";
let btBookmarkedIds = new Set();
let btIsLoading = false;

function initBreakthroughsModule() {
  // 1. Storage Area Pills
  const storagePills = document.querySelectorAll("#storage-pills-bar .btn-storage-pill");
  storagePills.forEach(pill => {
    pill.addEventListener("click", () => {
      storagePills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      btStorageFilter = pill.getAttribute("data-storage") || "all";
      loadBreakthroughsCatalog();
    });
  });

  // 2. Category Discipline Buttons
  const catButtons = document.querySelectorAll("#bt-category-buttons .btn-bt-cat");
  catButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      catButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      btCategoryFilter = btn.getAttribute("data-cat") || "All";
      loadBreakthroughsCatalog();
    });
  });

  // 3. Presentation Mode Toggle
  const btnModeEdu = document.getElementById("btn-mode-edu");
  const btnModeTech = document.getElementById("btn-mode-tech");
  if (btnModeEdu && btnModeTech) {
    btnModeEdu.addEventListener("click", () => {
      btnModeEdu.classList.add("active");
      btnModeTech.classList.remove("active");
      btPresentationMode = "edu";
      renderBreakthroughCards();
    });
    btnModeTech.addEventListener("click", () => {
      btnModeTech.classList.add("active");
      btnModeEdu.classList.remove("active");
      btPresentationMode = "tech";
      renderBreakthroughCards();
    });
  }

  // 4. Search Filter with live debounce
  const searchInput = document.getElementById("bt-search-input");
  const btnClearSearch = document.getElementById("btn-clear-bt-search");
  if (searchInput) {
    let searchDebounce = null;
    searchInput.addEventListener("input", (e) => {
      btSearchQuery = e.target.value.trim();
      if (btnClearSearch) btnClearSearch.style.display = btSearchQuery ? "flex" : "none";
      clearTimeout(searchDebounce);
      searchDebounce = setTimeout(() => {
        loadBreakthroughsCatalog();
      }, 250);
    });
  }
  if (btnClearSearch && searchInput) {
    btnClearSearch.addEventListener("click", () => {
      searchInput.value = "";
      btSearchQuery = "";
      btnClearSearch.style.display = "none";
      loadBreakthroughsCatalog();
    });
  }

  // 5. Live Sync via Europe PMC
  const btnSync = document.getElementById("btn-sync-europepmc");
  const topicInput = document.getElementById("bt-sync-topic-input");
  if (btnSync) {
    btnSync.addEventListener("click", async () => {
      const topic = topicInput ? topicInput.value.trim() : "";
      await syncEuropePmcBreakthroughs(topic);
    });
  }

  // 6. Reset Filters Button
  const btnReset = document.getElementById("btn-reset-bt-filters");
  if (btnReset) {
    btnReset.addEventListener("click", () => {
      btStorageFilter = "all";
      btCategoryFilter = "All";
      btSearchQuery = "";
      if (searchInput) searchInput.value = "";
      if (btnClearSearch) btnClearSearch.style.display = "none";

      const pills = document.querySelectorAll("#storage-pills-bar .btn-storage-pill");
      pills.forEach(p => {
        if (p.getAttribute("data-storage") === "all") p.classList.add("active");
        else p.classList.remove("active");
      });

      const cats = document.querySelectorAll("#bt-category-buttons .btn-bt-cat");
      cats.forEach(c => {
        if (c.getAttribute("data-cat") === "All") c.classList.add("active");
        else c.classList.remove("active");
      });

      loadBreakthroughsCatalog();
    });
  }

  // Pre-load data once in background
  loadBreakthroughsCatalog(false);
}

async function loadBreakthroughsCatalog(showStatus = true) {
  if (btIsLoading) return;
  btIsLoading = true;

  const statusBar = document.getElementById("bt-sync-status-bar");
  const statusText = document.getElementById("bt-sync-status-text");
  if (showStatus && statusBar && statusText) {
    statusText.innerText = "Accessing Biotechnology Breakthroughs Vault...";
    statusBar.style.display = "flex";
  }

  try {
    const params = new URLSearchParams({
      category: btCategoryFilter,
      storage_filter: btStorageFilter,
      q: btSearchQuery
    });
    const resp = await fetch(`/api/breakthroughs?${params.toString()}`);
    const data = await resp.json();

    if (data.status === "success" && data.items) {
      btCatalogState = data.items;
      btBookmarkedIds = new Set(data.bookmarked_ids || []);

      // Update counters
      const counts = data.counts || {};
      const setEl = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.innerText = val !== undefined ? val : 0;
      };
      setEl("stat-total-count", counts.total);
      setEl("stat-foundational-count", counts.foundational);
      setEl("stat-live-count", counts.live);
      setEl("stat-bookmarked-count", counts.bookmarks);

      setEl("count-pill-all", counts.total);
      setEl("count-pill-foundational", counts.foundational);
      setEl("count-pill-live", counts.live);
      setEl("count-pill-bookmarks", counts.bookmarks);

      renderBreakthroughCards();
    }
  } catch (err) {
    console.error("Failed to load breakthroughs catalog:", err);
  } finally {
    btIsLoading = false;
    if (statusBar) statusBar.style.display = "none";
  }
}

async function syncEuropePmcBreakthroughs(topic = "") {
  const btnSync = document.getElementById("btn-sync-europepmc");
  const statusBar = document.getElementById("bt-sync-status-bar");
  const statusText = document.getElementById("bt-sync-status-text");

  if (btnSync) btnSync.disabled = true;
  if (statusBar && statusText) {
    statusText.innerText = topic
      ? `Querying Europe PMC for 2026 breakthroughs on '${topic}' and deconstructing mechanisms...`
      : "Streaming fresh 2026 high-impact biotechnology papers from Europe PMC...";
    statusBar.style.display = "flex";
  }

  try {
    const resp = await fetch("/api/breakthroughs/sync", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic: topic })
    });
    const data = await resp.json();

    if (data.status === "success") {
      const added = data.added_count || 0;
      showToast(`Synchronized! ${added} new verified breakthroughs added to discovery vault.`);
      await loadBreakthroughsCatalog(false);
    } else {
      showToast(data.message || "Could not sync new breakthroughs from Europe PMC.");
    }
  } catch (err) {
    console.error("Sync error:", err);
    showToast("Network error syncing breakthroughs. Europe PMC may be busy.");
  } finally {
    if (btnSync) btnSync.disabled = false;
    if (statusBar) statusBar.style.display = "none";
  }
}

async function toggleBreakthroughBookmark(id) {
  try {
    const resp = await fetch("/api/breakthroughs/bookmark", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: id })
    });
    const data = await resp.json();
    if (data.status === "success") {
      btBookmarkedIds = new Set(data.bookmarked_ids || []);
      const countEl = document.getElementById("stat-bookmarked-count");
      if (countEl) countEl.innerText = btBookmarkedIds.size;
      const countPill = document.getElementById("count-pill-bookmarks");
      if (countPill) countPill.innerText = btBookmarkedIds.size;

      showToast(data.is_bookmarked ? "⭐ Breakthrough bookmarked!" : "Bookmark removed.");
      renderBreakthroughCards();
    }
  } catch (err) {
    console.error("Bookmark error:", err);
  }
}

function renderBreakthroughCards() {
  const container = document.getElementById("breakthroughs-cards-container");
  const emptyState = document.getElementById("breakthroughs-empty-state");
  if (!container) return;

  if (!btCatalogState || btCatalogState.length === 0) {
    container.innerHTML = "";
    if (emptyState) emptyState.style.display = "block";
    return;
  }

  if (emptyState) emptyState.style.display = "none";

  const cardsHtml = btCatalogState.map(item => {
    const isBookmarked = btBookmarkedIds.has(item.id) || item.is_bookmarked;
    const isFoundational = item.storage_source === "foundational";
    const storageBadge = isFoundational
      ? `<span class="bt-badge bt-badge-foundational">🏛️ Foundational</span>`
      : `<span class="bt-badge bt-badge-live">⚡ Live Discovery</span>`;

    const verifiedYear = item.year || "2026";
    const yearBadge = `<span class="bt-badge bt-badge-year" title="Verified Publication Year">${verifiedYear}</span>`;
    const categoryBadge = `<span class="bt-badge bt-badge-category">${escapeHtml(item.category || "Biotechnology")}</span>`;

    // Educational Mode Content
    const edu = item.educational || {};
    const howSteps = edu.how_it_works || {};

    const formatStep = (stepText, fallback) => {
      let raw = (stepText || fallback || "").trim();
      raw = raw.replace(/^Step\s*\d+\s*(?:\([^)]*\))?\s*:\s*/i, "");
      const colonIdx = raw.indexOf(":");
      if (colonIdx > 0 && colonIdx < 35) {
        const header = raw.slice(0, colonIdx).trim();
        const body = raw.slice(colonIdx + 1).trim();
        return `<strong>${escapeHtml(header)}:</strong> ${escapeHtml(body)}`;
      }
      return escapeHtml(raw);
    };

    const eduHtml = `
      <div class="bt-section-block block-what">
        <div class="bt-section-title">📌 What is this?</div>
        <div class="bt-section-content">${escapeHtml(edu.what_is_it || "Groundbreaking molecular or bioengineering milestone.")}</div>
      </div>
      <div class="bt-section-block block-problem">
        <div class="bt-section-title">🛑 Biological Problem Solved</div>
        <div class="bt-section-content">${escapeHtml(edu.problem_solved || "Overcomes baseline rate or delivery limitation.")}</div>
      </div>
      <div class="bt-section-block block-mechanism">
        <div class="bt-section-title">⚙️ 3-Step How It Works</div>
        <ul class="bt-steps-list">
          <li class="bt-step-item">
            <span class="bt-step-num">1</span>
            <span class="bt-step-text">${formatStep(Array.isArray(howSteps) ? howSteps[0] : howSteps.step1, "Molecular recognition and targeted sequence binding.")}</span>
          </li>
          <li class="bt-step-item">
            <span class="bt-step-num">2</span>
            <span class="bt-step-text">${formatStep(Array.isArray(howSteps) ? howSteps[1] : howSteps.step2, "Catalytic conversion or precision biochemical execution.")}</span>
          </li>
          <li class="bt-step-item">
            <span class="bt-step-num">3</span>
            <span class="bt-step-text">${formatStep(Array.isArray(howSteps) ? howSteps[2] : howSteps.step3, "Measurable phenotypic rescue or analytical signal generation.")}</span>
          </li>
        </ul>
      </div>
      <div class="bt-section-block block-significance">
        <div class="bt-section-title">🌍 Why It Matters</div>
        <div class="bt-section-content">${escapeHtml(edu.why_it_matters || "Transforms translational applications across health, synthetic biology, and industry.")}</div>
      </div>
    `;

    // Technical Mode Content
    const tech = item.technical || {};
    const links = item.links || {};
    const sourceLink = item.doi_url || links.europepmc || links.doi || (item.doi ? ('https://doi.org/' + item.doi) : null);
    const techHtml = `
      <div class="bt-section-block block-mechanism">
        <div class="bt-section-title">🧪 Biochemical Mechanism & Molecular Architecture</div>
        <div class="bt-section-content">${escapeHtml(tech.mechanism || "Targeted enzymatic catalysis and engineered molecular cascade.")}</div>
      </div>
      <div class="bt-tech-chips-grid">
        <div class="bt-tech-metric-chip">
          <div class="bt-chip-label">📊 Primary Empirical Benchmark</div>
          <div class="bt-chip-val">${escapeHtml(tech.primary_metric || "Quantified analytical sensitivity or yield baseline.")}</div>
        </div>
        <div class="bt-tech-metric-chip">
          <div class="bt-chip-label">⚖️ Valid Experimental Control</div>
          <div class="bt-chip-val">${escapeHtml(tech.controls || "Wild-type baseline host vs engineered construct.")}</div>
        </div>
      </div>
      <div class="bt-section-block block-significance">
        <div class="bt-section-title">🎯 Proposal Translation Significance</div>
        <div class="bt-section-content">${escapeHtml(tech.significance || "Provides validated baseline calibrating specific aims.")}</div>
      </div>
      <div class="bt-citation-box">
        <strong>Citation:</strong> ${escapeHtml(tech.citation || "Peer-reviewed literature citation")}
        ${sourceLink ? `<a href="${sourceLink}" target="_blank" rel="noopener noreferrer" class="bt-citation-link"><span>📄 Open Primary Paper ↗</span></a>` : ""}
      </div>
    `;

    const bodyContent = btPresentationMode === "edu" ? eduHtml : techHtml;

    return `
      <article class="breakthrough-card ${isBookmarked ? "bookmarked" : ""}" data-id="${escapeHtml(item.id)}">
        <div class="bt-card-header">
          <div class="card-top-badges">
            <div class="badges-left">
              ${storageBadge}
              ${yearBadge}
              ${categoryBadge}
            </div>
            <button type="button" class="btn-bookmark-card ${isBookmarked ? "active" : ""}" data-id="${escapeHtml(item.id)}" title="${isBookmarked ? "Remove Bookmark" : "Bookmark this Breakthrough"}">
              ${isBookmarked ? "⭐" : "☆"}
            </button>
          </div>
          <h3 class="bt-card-title">${escapeHtml(item.title || "Biotechnology Breakthrough")}</h3>
        </div>

        <div class="bt-card-body">
          ${bodyContent}
        </div>

        <div class="bt-card-actions">
          <button type="button" class="btn-bt-transfer" data-id="${escapeHtml(item.id)}" title="Transfer this benchmark and problem into Step 2 Evidence Matrix">
            <span>📥</span> <span>Transfer to Step 2 Matrix</span>
          </button>
          <div class="bt-aux-actions">
            <button type="button" class="btn-bt-aux btn-copy-bt-cite" data-citation="${escapeHtml(tech.citation || item.title || "")}" title="Copy APA reference to clipboard">
              <span>📋</span> <span>Cite</span>
            </button>
            ${sourceLink ? `
              <a href="${sourceLink}" target="_blank" rel="noopener noreferrer" class="btn-bt-aux btn-bt-paper" title="Open source peer-reviewed research paper in new tab">
                <span>📄</span> <span>Read Paper ↗</span>
              </a>
            ` : ""}
          </div>
        </div>
      </article>
    `;
  }).join("");

  container.innerHTML = cardsHtml;

  // Bind dynamic card buttons
  container.querySelectorAll(".btn-bookmark-card").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const id = btn.getAttribute("data-id");
      if (id) toggleBreakthroughBookmark(id);
    });
  });

  container.querySelectorAll(".btn-bt-transfer").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const id = btn.getAttribute("data-id");
      const item = btCatalogState.find(x => x.id === id);
      if (item) transferBreakthroughToMatrix(item);
    });
  });

  container.querySelectorAll(".btn-copy-bt-cite").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const cite = btn.getAttribute("data-citation");
      if (cite) {
        navigator.clipboard.writeText(cite).then(() => {
          showToast("APA citation copied to clipboard!");
        });
      }
    });
  });
}

function transferBreakthroughToMatrix(item) {
  const tech = item.technical || {};
  const edu = item.educational || {};

  // Populate Step 2 inputs
  const blueInput = document.getElementById("matrix-blue");
  const greenInput = document.getElementById("matrix-green");
  const citeInput = document.getElementById("matrix-citation");

  if (blueInput && tech.primary_metric) {
    blueInput.value = tech.primary_metric;
    projectState.matrix.blue = tech.primary_metric;
  }
  if (greenInput && (edu.problem_solved || tech.mechanism)) {
    greenInput.value = edu.problem_solved || tech.mechanism;
    projectState.matrix.green = edu.problem_solved || tech.mechanism;
  }
  if (citeInput && tech.citation) {
    citeInput.value = tech.citation;
    projectState.matrix.citation = tech.citation;
  }

  saveToStorage();
  updateLiveScoreDebounced();

  // Switch to studio view and jump to step 2
  setViewMode("studio");
  goToStep(2);

  const matrixCard = document.getElementById("card-evidence-matrix") || blueInput;
  if (matrixCard) {
    setTimeout(() => {
      matrixCard.scrollIntoView({ behavior: "smooth", block: "center" });
      if (blueInput) {
        blueInput.style.transition = "box-shadow 0.3s ease";
        blueInput.style.boxShadow = "0 0 0 3px #3b82f6";
        setTimeout(() => { blueInput.style.boxShadow = ""; }, 2000);
      }
    }, 200);
  }

  showToast(`Transferred "${item.title}" benchmarks into Step 2 Evidence Matrix!`);
}
