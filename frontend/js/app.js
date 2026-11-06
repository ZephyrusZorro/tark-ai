/**
 * TarkAI (तर्क) — Master Client-Side Application Studio Controller (v2.1)
 * Client-side orchestration for:
 * - Control Flow Graph (CFG) basic block visualization
 * - Spectrum-Based Fault Localization (Tarantula & Ochiai)
 * - Dynamic Property-Based Fuzzing & Invariant Stress Testing
 * - Halstead Software Engineering Metrics & Cognitive Complexity
 * - FSRS Spaced Repetition Retrievability Engine
 * - Multi-turn Socratic Pedagogical Mentoring
 */

document.addEventListener("DOMContentLoaded", () => {
  // --------------------------------------------------------------------------
  // Application State
  // --------------------------------------------------------------------------
  let currentChallengeId = "two_sum_sorted";
  let challenges = [];
  let currentHintLevel = 1;
  let lastFailedTest = null;
  let chatHistory = [];
  let currentAstData = null;
  const drafts = window.TarkDrafts;
  let challengeLoaded = false;
  let editorChallengeId = null;
  let challengeLoading = false;
  let runPending = false;
  let fuzzPending = false;
  let lastRunCode = null;
  let lastFuzzCode = null;
  let selectionVersion = 0;
  let analysisVersion = 0;
  let graphVersion = 0;
  function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  }
  async function apiFetch(url, options) {
    const response = await window.fetch(url, options);
    if (!response.ok) {
      const message = `Request failed (${response.status}). Please try again.`;
      if (consoleStatus) consoleStatus.textContent = message;
      throw new Error(message);
    }
    return response;
  }
  let currentFlowchartMode = "cfg"; // "cfg" or "ast"

  // Initialize Mermaid.js engine
  if (window.mermaid) {
    try {
      mermaid.initialize({
        startOnLoad: false,
        theme: "dark",
        securityLevel: "strict",
        themeVariables: {
          darkMode: true,
          background: "#08090f",
          primaryColor: "#1d2236",
          primaryTextColor: "#f1f3f9",
          primaryBorderColor: "#3b82f6",
          lineColor: "#64748b",
          secondaryColor: "#161a29",
          tertiaryColor: "#10131d",
          fontFamily: "'Space Mono', monospace",
          fontSize: "12px"
        }
      });
    } catch (e) {
      console.warn("Mermaid init notice:", e);
    }
  }

  // --------------------------------------------------------------------------
  // DOM References
  // --------------------------------------------------------------------------
  const workspaceButtons = document.querySelectorAll(".ws-btn");
  const workspacePanes = document.querySelectorAll(".workspace-pane");
  const panelTabButtons = document.querySelectorAll(".panel-tab-btn");
  const subtabPanes = document.querySelectorAll(".subtab-pane");

  const utcClock = document.getElementById("utc-clock");
  const btnScanlines = document.getElementById("btn-scanlines");
  const topChalTitle = document.getElementById("top-chal-title");
  const topTrackCode = document.getElementById("top-track-code");
  const topChalDiff = document.getElementById("top-chal-diff");

  const statSolved = document.getElementById("stat-solved");
  const statStreak = document.getElementById("stat-streak");
  const statLoc = document.getElementById("stat-loc");
  const leitnerDueCount = document.getElementById("leitner-due-count");

  const codeEditor = document.getElementById("code-editor");
  const lineNumbers = document.getElementById("line-numbers");
  const consoleStatus = document.getElementById("console-status");
  const consolePerf = document.getElementById("console-perf");
  const editorFilename = document.getElementById("editor-filename");

  const challengeList = document.getElementById("challenge-list");
  const curriculumCount = document.getElementById("curriculum-count");
  const probTitle = document.getElementById("prob-title");
  const probSummary = document.getElementById("prob-summary");
  const probDescription = document.getElementById("prob-description");
  const probConstraints = document.getElementById("prob-constraints");

  const btnRun = document.getElementById("btn-run");
  const btnFuzz = document.getElementById("btn-fuzz");
  const btnRunFuzzInner = document.getElementById("btn-run-fuzz-inner");
  const btnAnalyze = document.getElementById("btn-analyze");
  const btnHint = document.getElementById("btn-hint");
  const btnReset = document.getElementById("btn-reset");
  const btnRefreshFlowchart = document.getElementById("btn-refresh-flowchart");
  const btnZoomReset = document.getElementById("btn-zoom-reset");
  const btnViewCfg = document.getElementById("btn-view-cfg");
  const btnViewAst = document.getElementById("btn-view-ast");

  const testSummaryBox = document.getElementById("test-summary-box");
  const testSummaryText = document.getElementById("test-summary-text");
  const testSummaryTime = document.getElementById("test-summary-time");
  const testCardsContainer = document.getElementById("test-cards-container");

  const sbflSummaryBox = document.getElementById("sbfl-summary-box");
  const sbflHeadline = document.getElementById("sbfl-headline");
  const sbflDesc = document.getElementById("sbfl-desc");
  const sbflTableContainer = document.getElementById("sbfl-table-container");

  const fuzzSummaryBox = document.getElementById("fuzz-summary-box");
  const fuzzSummaryText = document.getElementById("fuzz-summary-text");
  const fuzzSummaryMeta = document.getElementById("fuzz-summary-meta");
  const fuzzCardsContainer = document.getElementById("fuzz-cards-container");

  const astQuickComplexity = document.getElementById("ast-quick-complexity");
  const astQuickNesting = document.getElementById("ast-quick-nesting");
  const astQuickCog = document.getElementById("ast-quick-cog");
  const astQuickCyc = document.getElementById("ast-quick-cyc");
  const quickAntiPatterns = document.getElementById("quick-anti-patterns");
  const astQuickTree = document.getElementById("ast-quick-tree");
  const mermaidGraphTarget = document.getElementById("mermaid-graph-target");
  const fullAstTree = document.getElementById("full-ast-tree");

  const fullBigO = document.getElementById("full-big-o");
  const fullBigOReason = document.getElementById("full-big-o-reason");
  const fullCogVal = document.getElementById("full-cog-val");
  const fullCycVal = document.getElementById("full-cyc-val");
  const fullAntiPatternsList = document.getElementById("full-anti-patterns-list");
  const symbolTableContainer = document.getElementById("symbol-table-container");
  const hN1 = document.getElementById("h-n1");
  const hN2 = document.getElementById("h-n2");
  const hN1Tot = document.getElementById("h-N1");
  const hN2Tot = document.getElementById("h-N2");
  const hVocab = document.getElementById("h-vocab");
  const hLength = document.getElementById("h-length");
  const hVol = document.getElementById("h-vol");
  const hDiff = document.getElementById("h-diff");
  const hEffort = document.getElementById("h-effort");

  const dockSocTier = document.getElementById("dock-soc-tier");
  const dockSocTitle = document.getElementById("dock-soc-title");
  const dockSocGuidance = document.getElementById("dock-soc-guidance");
  const dockSocQuestion = document.getElementById("dock-soc-question");
  const dockChatForm = document.getElementById("dock-chat-form");
  const dockChatInput = document.getElementById("dock-chat-input");
  const terminalTierPill = document.getElementById("terminal-tier-pill");
  const terminalChatLog = document.getElementById("terminal-chat-log");
  const terminalInputForm = document.getElementById("terminal-input-form");
  const terminalInputField = document.getElementById("terminal-input-field");

  // --------------------------------------------------------------------------
  // UTC Clock Ticker & CRT Scanline Toggle
  // --------------------------------------------------------------------------
  function updateClock() {
    const now = new Date();
    const h = String(now.getUTCHours()).padStart(2, "0");
    const m = String(now.getUTCMinutes()).padStart(2, "0");
    const s = String(now.getUTCSeconds()).padStart(2, "0");
    if (utcClock) utcClock.textContent = `${h}:${m}:${s} UTC`;
  }
  setInterval(updateClock, 1000);
  updateClock();

  if (btnScanlines) {
    btnScanlines.addEventListener("click", () => {
      document.body.classList.toggle("scanlines-active");
      const isActive = document.body.classList.contains("scanlines-active");
      btnScanlines.textContent = isActive ? "CRT: ON" : "CRT: OFF";
      localStorage.setItem("tark_scanlines", isActive ? "true" : "false");
    });

    if (localStorage.getItem("tark_scanlines") === "false") {
      document.body.classList.remove("scanlines-active");
      btnScanlines.textContent = "CRT: OFF";
    }
  }

  // --------------------------------------------------------------------------
  // Workspace Navigation (Workspaces 1 through 5)
  // --------------------------------------------------------------------------
  function switchWorkspace(targetId) {
    workspaceButtons.forEach(b => {
      const active = b.getAttribute("data-workspace") === targetId;
      b.classList.toggle("active", active);
      b.setAttribute("aria-pressed", String(active));
    });
    workspacePanes.forEach(p => {
      p.classList.toggle("active", p.id === targetId);
    });

    if (targetId === "ws-ast") {
      updateFlowchartRender();
    } else if (targetId === "ws-leitner") {
      loadLeitnerCards();
    }
  }

  workspaceButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const ws = btn.getAttribute("data-workspace");
      if (ws) switchWorkspace(ws);
    });
  });

  window.addEventListener("keydown", (e) => {
    if (e.altKey && e.key >= "1" && e.key <= "5") {
      e.preventDefault();
      const wsMap = {
        "1": "ws-code",
        "2": "ws-ast",
        "3": "ws-complexity",
        "4": "ws-leitner",
        "5": "ws-socrates"
      };
      if (wsMap[e.key]) switchWorkspace(wsMap[e.key]);
    }
  });

  panelTabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");
      panelTabButtons.forEach(b => b.classList.remove("active"));
      subtabPanes.forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(targetTab)?.classList.add("active");
    });
  });

  // --------------------------------------------------------------------------
  // Editor Controller
  // --------------------------------------------------------------------------
  function updateResultFreshness() {
    const test = document.getElementById("test-freshness");
    const fuzz = document.getElementById("fuzz-freshness");
    if (test) test.hidden = lastRunCode === null || lastRunCode === codeEditor.value;
    if (fuzz) fuzz.hidden = lastFuzzCode === null || lastFuzzCode === codeEditor.value;
  }
  function updateLineNumbers() {
    if (!codeEditor || !lineNumbers) return;
    const lines = codeEditor.value.split("\n").length;
    lineNumbers.innerHTML = Array.from({ length: lines }, (_, i) => i + 1).join("<br>");
    window.TarkEditor.render(codeEditor);
    updateResultFreshness();
    if (editorChallengeId && !challengeLoading) drafts.set(editorChallengeId, codeEditor.value);
  }

  if (codeEditor) {
    codeEditor.addEventListener("input", updateLineNumbers);
    codeEditor.addEventListener("scroll", () => {
      if (lineNumbers) lineNumbers.scrollTop = codeEditor.scrollTop;
    });

    codeEditor.addEventListener("keydown", (e) => {
      if (e.key === "Tab") {
        e.preventDefault();
        const start = codeEditor.selectionStart;
        const end = codeEditor.selectionEnd;
        codeEditor.value = codeEditor.value.substring(0, start) + "    " + codeEditor.value.substring(end);
        codeEditor.selectionStart = codeEditor.selectionEnd = start + 4;
        updateLineNumbers();
      }

      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        runTests();
      }

      if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === "A" || e.key === "a")) {
        e.preventDefault();
        analyzeAST();
      }
    });
  }

  // --------------------------------------------------------------------------
  // Curriculum & Challenge Loading
  // --------------------------------------------------------------------------
  async function loadCurriculum() {
    try {
      const res = await apiFetch("/api/curriculum");
      challenges = await res.json();

      const solvedCount = challenges.filter(c => c.solved).length;
      if (curriculumCount) curriculumCount.textContent = `${solvedCount} / ${challenges.length} Solved`;
      if (statSolved) statSolved.textContent = `${solvedCount}/${challenges.length}`;

      if (challengeList) {
        challengeList.innerHTML = challenges.map(c => `
          <button type="button" class="challenge-item ${c.id === currentChallengeId ? 'active' : ''}" data-id="${c.id}">
            <div>
              <div class="challenge-title">${c.solved ? '✓ ' : ''}${c.title}</div>
              <div style="font-size: 10px; color: var(--text-muted); font-family: var(--font-mono); margin-top: 2px;">
                ${c.track_code || c.track.split(':')[0]}
              </div>
            </div>
            <span class="badge badge-${c.difficulty.toLowerCase()}">${c.difficulty}</span>
          </button>
        `).join("");

        document.querySelectorAll(".challenge-item").forEach(item => {
          item.addEventListener("click", () => {
            const id = item.getAttribute("data-id");
            if (id) selectChallenge(id);
          });
        });
      }

      window.filterChallenges?.();
      if (challenges.length > 0 && !challengeLoaded) {
        await selectChallenge(currentChallengeId || challenges[0].id);
      }

      loadStats();
      loadLeitnerCards();
    } catch (err) {
      console.error("Failed to load curriculum:", err);
    }
  }

  async function selectChallenge(id, { reset = false } = {}) {
    if (editorChallengeId && !reset) drafts.set(editorChallengeId, codeEditor.value);
    if (reset) drafts.delete(id);
    const version = ++selectionVersion;
    challengeLoading = true;
    codeEditor.disabled = true;
    [btnRun, btnAnalyze, btnHint, btnFuzz, btnRunFuzzInner, btnReset].forEach(button => { if (button) button.disabled = true; });
    if (consoleStatus) consoleStatus.textContent = "Loading challenge…";
    currentHintLevel = 1;
    lastFailedTest = null;

    document.querySelectorAll(".challenge-item").forEach(el => {
      el.classList.toggle("active", el.getAttribute("data-id") === id);
    });

    try {
      const res = await apiFetch(`/api/challenge/${id}`);
      const data = await res.json();
      if (version !== selectionVersion) return;
      currentChallengeId = id;
      editorChallengeId = id;
      challengeLoaded = true;
      challengeLoading = false;
      chatHistory = [];
      currentAstData = null;
      lastRunCode = null;
      lastFuzzCode = null;
      if (terminalChatLog) terminalChatLog.textContent = "Ask about this challenge, your approach, or a failing test.";
      if (dockSocGuidance) dockSocGuidance.textContent = "Request a hint to explore this challenge.";
      if (dockSocTitle) dockSocTitle.textContent = "A little guidance, when you need it.";
      if (dockSocQuestion) dockSocQuestion.textContent = "";
      if (sbflSummaryBox) sbflSummaryBox.style.display = "none";
      if (sbflTableContainer) sbflTableContainer.replaceChildren();
      if (fuzzSummaryBox) fuzzSummaryBox.style.display = "none";
      if (fuzzCardsContainer) fuzzCardsContainer.replaceChildren();

      if (topChalTitle) topChalTitle.textContent = data.title;
      if (topTrackCode) topTrackCode.textContent = data.track_code || data.track.split(":")[0];
      if (topChalDiff) {
        topChalDiff.textContent = data.difficulty.toUpperCase();
        topChalDiff.className = `badge badge-${data.difficulty.toLowerCase()}`;
      }

      if (probTitle) probTitle.textContent = data.title;
      if (probSummary) probSummary.textContent = data.summary;
      if (probDescription) {
        probDescription.innerHTML = data.description
          .replace(/### (.*?)\n/g, '<h4 style="color:#fff; margin:10px 0 4px;">$1</h4>')
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/`(.*?)`/g, '<code>$1</code>')
          .replace(/\n\n/g, '<br><br>');
      }

      if (probConstraints) {
        probConstraints.innerHTML = data.constraints.map(c => `<li>${c}</li>`).join("");
      }

      if (editorFilename) editorFilename.textContent = `${id}.py`;
      if (codeEditor) {
        codeEditor.value = drafts.get(id) ?? data.starter_code;
        updateLineNumbers();
      }

      // Reset tests container
      if (testSummaryBox) testSummaryBox.style.display = "none";
      if (testCardsContainer) {
        testCardsContainer.innerHTML = `
          <div class="empty-state">
            <div class="empty-icon">⚙</div>
            <p>Click <strong>"Run Tests"</strong> (Ctrl+Enter) to evaluate your algorithm against sandboxed test cases.</p>
          </div>
        `;
      }

      analyzeAST();
    } catch (err) {
      console.error("Failed to load challenge details:", err);
      if (version === selectionVersion) {
        document.querySelectorAll(".challenge-item").forEach(item => item.classList.toggle("active", item.dataset.id === currentChallengeId));
        if (consoleStatus) consoleStatus.textContent = "Could not load that challenge. Your current draft is preserved.";
      }
    } finally {
      if (version === selectionVersion) {
        challengeLoading = false;
        codeEditor.disabled = !editorChallengeId;
        [btnRun, btnAnalyze, btnHint, btnFuzz, btnRunFuzzInner, btnReset].forEach(button => { if (button) button.disabled = !editorChallengeId; });
        if (btnRun) btnRun.disabled ||= runPending;
        [btnFuzz, btnRunFuzzInner].forEach(button => { if (button) button.disabled ||= fuzzPending; });
      }
    }
  }

  // --------------------------------------------------------------------------
  // AST Semantic Analysis & CFG Visualization
  // --------------------------------------------------------------------------
  async function analyzeAST() {
    if (challengeLoading || !editorChallengeId) return;
    const version = ++analysisVersion;
    const challenge = currentChallengeId;
    const code = codeEditor.value;
    if (consoleStatus) consoleStatus.textContent = "Parsing AST, computing CFG & calculating Halstead bounds...";
    try {
      const res = await apiFetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: codeEditor.value, challenge_id: currentChallengeId })
      });
      const data = await res.json();
      if (version !== analysisVersion || challenge !== currentChallengeId || code !== codeEditor.value) return;
      currentAstData = data;

      if (!data.syntax_valid) {
        if (astQuickComplexity) {
          astQuickComplexity.textContent = "SYNTAX ERR";
          astQuickComplexity.style.color = "var(--rose)";
        }
        if (astQuickNesting) astQuickNesting.textContent = `L${data.syntax_line || '?'}`;
        if (quickAntiPatterns) {
          quickAntiPatterns.innerHTML = `
            <div class="anti-pattern-alert" style="border-color: var(--rose);">
              <h4 style="color: var(--rose);">Syntax Error Detected</h4>
              <p>${escapeHTML(data.syntax_error)} (line ${data.syntax_line})</p>
            </div>
          `;
        }
        if (astQuickTree) astQuickTree.textContent = JSON.stringify({ error: data.syntax_error }, null, 2);
        if (consoleStatus) consoleStatus.textContent = `Syntax Error on line ${data.syntax_line}: ${data.syntax_error}`;
        return;
      }

      const comp = data.complexity;
      if (astQuickComplexity) {
        astQuickComplexity.textContent = comp.estimated_time;
        astQuickComplexity.style.color = "var(--cyan)";
      }
      if (astQuickNesting) astQuickNesting.textContent = comp.max_loop_nesting;
      if (astQuickCog) astQuickCog.textContent = comp.cognitive_complexity;
      if (astQuickCyc) astQuickCyc.textContent = comp.cyclomatic_complexity;

      if (fullBigO) fullBigO.textContent = comp.estimated_time;
      if (fullBigOReason) fullBigOReason.textContent = comp.reason;
      if (fullCogVal) fullCogVal.textContent = comp.cognitive_complexity;
      if (fullCycVal) fullCycVal.textContent = comp.cyclomatic_complexity;

      if (comp.halstead) {
        const h = comp.halstead;
        if (hN1) hN1.textContent = h.distinct_operators;
        if (hN2) hN2.textContent = h.distinct_operands;
        if (hN1Tot) hN1Tot.textContent = h.total_operators;
        if (hN2Tot) hN2Tot.textContent = h.total_operands;
        if (hVocab) hVocab.textContent = h.vocabulary;
        if (hLength) hLength.textContent = h.program_length;
        if (hVol) hVol.textContent = h.volume.toFixed(1);
        if (hDiff) hDiff.textContent = h.difficulty.toFixed(2);
        if (hEffort) hEffort.textContent = h.effort.toFixed(1);
      }

      if (data.anti_patterns && data.anti_patterns.length > 0) {
        const badgesHtml = data.anti_patterns.map(p => `
          <div class="anti-pattern-alert" style="cursor:pointer;" onclick="jumpToEditorLine(${p.line})">
            <h4>[LINE ${p.line}] ${escapeHTML(p.message)}</h4>
            <p><strong>Fix:</strong> ${escapeHTML(p.suggestion)}</p>
          </div>
        `).join("");
        if (quickAntiPatterns) quickAntiPatterns.innerHTML = badgesHtml;
        if (fullAntiPatternsList) fullAntiPatternsList.innerHTML = badgesHtml;
      } else {
        const cleanMsg = `
          <div style="background: var(--emerald-bg); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 4px; padding: 8px 10px;">
            <p style="font-size: 11px; color: var(--emerald); font-family: var(--font-mono);">
              ✓ Zero anti-patterns detected. Clean idiomatic Python structure.
            </p>
          </div>
        `;
        if (quickAntiPatterns) quickAntiPatterns.innerHTML = cleanMsg;
        if (fullAntiPatternsList) fullAntiPatternsList.innerHTML = cleanMsg;
      }

      if (data.symbol_table && symbolTableContainer) {
        const sym = data.symbol_table;
        symbolTableContainer.innerHTML = `
          <div style="font-family: var(--font-mono); font-size: 11px; color: var(--text-dim); display:flex; flex-direction:column; gap:6px;">
            <div>Functions: <span style="color:var(--cyan);">${sym.functions.map(f => f.name + '()').join(', ') || 'None'}</span></div>
            <div>Classes: <span style="color:var(--amber);">${sym.classes.map(c => c.name).join(', ') || 'None'}</span></div>
            <div>Imports: <span style="color:var(--purple);">${escapeHTML(sym.imports.join(', ') || 'None')}</span></div>
          </div>
        `;
      }

      if (astQuickTree) astQuickTree.textContent = JSON.stringify(data.tree_hierarchy, null, 2);
      if (fullAstTree) fullAstTree.textContent = JSON.stringify(data.tree_hierarchy, null, 2);

      updateFlowchartRender();
      if (consoleStatus) consoleStatus.textContent = `AST Ready: ${comp.estimated_time} (${comp.reason}) · CFG Blocks: ${data.cfg_analysis?.total_blocks || 0}`;
    } catch (err) {
      console.error("AST parsing error:", err);
      if (consoleStatus) consoleStatus.textContent = "AST parsing network error.";
    }
  }

  function updateFlowchartRender() {
    if (!currentAstData) {
      analyzeAST();
      return;
    }
    if (currentFlowchartMode === "cfg" && currentAstData.cfg_analysis && currentAstData.cfg_analysis.mermaid_cfg) {
      renderMermaidDiagram(currentAstData.cfg_analysis.mermaid_cfg);
    } else if (currentAstData.mermaid_flowchart) {
      renderMermaidDiagram(currentAstData.mermaid_flowchart);
    }
  }

  btnViewCfg?.addEventListener("click", () => {
    currentFlowchartMode = "cfg";
    btnViewCfg.classList.add("active");
    btnViewAst?.classList.remove("active");
    updateFlowchartRender();
  });

  btnViewAst?.addEventListener("click", () => {
    currentFlowchartMode = "ast";
    btnViewAst.classList.add("active");
    btnViewCfg?.classList.remove("active");
    updateFlowchartRender();
  });

  async function renderMermaidDiagram(chartDefinition) {
    const version = ++graphVersion;
    if (!window.mermaid || !mermaidGraphTarget) return;
    if (!chartDefinition || !chartDefinition.trim()) {
      mermaidGraphTarget.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">◈</div>
          <p>No graph definition available. Click "Inspect AST" to parse.</p>
        </div>
      `;
      return;
    }

    try {
      const renderId = "mermaid_svg_" + Math.random().toString(36).substring(2, 9);
      const { svg } = await mermaid.render(renderId, chartDefinition);
      if (version !== graphVersion) return;
      mermaidGraphTarget.innerHTML = svg;
    } catch (err) {
      console.warn("Mermaid render notice:", err);
      mermaidGraphTarget.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">◈</div>
          <p style="color: var(--amber); font-family: var(--font-mono); font-size: 11px;">
            Diagram refreshed. Select CFG or AST mode to reload view.
          </p>
        </div>
      `;
    }
  }

  btnRefreshFlowchart?.addEventListener("click", () => {
    analyzeAST();
  });

  btnZoomReset?.addEventListener("click", () => {
    const svg = mermaidGraphTarget?.querySelector("svg");
    if (svg) svg.style.transform = "none";
  });

  // --------------------------------------------------------------------------
  // Sandboxed Test Execution & Fault Localization
  // --------------------------------------------------------------------------
  async function runTests() {
    if (challengeLoading || !editorChallengeId || runPending) return;
    runPending = true;
    const requestChallenge = currentChallengeId;
    const requestCode = codeEditor.value;
    if (consoleStatus) consoleStatus.textContent = "Executing sandboxed test runner with failure tracing...";
    if (btnRun) btnRun.disabled = true;

    switchWorkspace("ws-code");
    document.querySelector('.panel-tab-btn[data-tab="tab-tests"]')?.click();

    try {
      const res = await apiFetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          challenge_id: currentChallengeId,
          code: codeEditor.value
        })
      });
      const data = await res.json();
      if (requestChallenge !== currentChallengeId || requestCode !== codeEditor.value) return;
      lastRunCode = requestCode;
      updateResultFreshness();

      if (consolePerf) consolePerf.textContent = `${data.execution_time_ms}ms · ${data.memory_kb}KB`;

      if (testSummaryBox) testSummaryBox.style.display = "flex";
      if (data.overall_passed) {
        if (testSummaryBox) testSummaryBox.className = "test-summary pass";
        if (testSummaryText) testSummaryText.textContent = `✓ ${data.passed_count} / ${data.total_count} Tests Passed (100%)`;
        if (testSummaryTime) testSummaryTime.textContent = `${data.execution_time_ms}ms`;
        if (consoleStatus) consoleStatus.textContent = "All test assertions passed successfully!";
        lastFailedTest = null;
        loadCurriculum();
      } else {
        if (testSummaryBox) testSummaryBox.className = "test-summary fail";
        if (testSummaryText) testSummaryText.textContent = `✕ ${data.passed_count} / ${data.total_count} Tests Passed`;
        if (testSummaryTime) testSummaryTime.textContent = `${data.execution_time_ms}ms`;
        if (consoleStatus) consoleStatus.textContent = "Some test assertions failed. Click FAULT LOC (SBFL) tab to view root-cause analysis.";
        lastFailedTest = data.test_results?.find(t => !t.passed) || null;
      }

      if (data.test_results && data.test_results.length > 0 && testCardsContainer) {
        testCardsContainer.innerHTML = data.test_results.map(t => `
          <div class="test-card" style="border-left: 3px solid ${t.passed ? 'var(--emerald)' : 'var(--rose)'};">
            <div class="test-card-head">
              <span class="test-card-desc">${escapeHTML(t.description)}</span>
              <span class="badge ${t.passed ? 'badge-easy' : 'badge-hard'}">${t.passed ? 'PASSED' : 'FAILED'}</span>
            </div>
            <div class="test-details">
              <div>Call: <span class="call">${escapeHTML(t.call)}</span></div>
              <div>Expected: <span class="exp">${escapeHTML(t.expected_repr)}</span></div>
              <div>Actual: <span class="${t.passed ? 'act-pass' : 'act-fail'}">${escapeHTML(t.actual_repr)}</span></div>
              ${t.error_message ? `<div style="color: var(--rose); margin-top: 4px;">${escapeHTML(t.error_message)}</div>` : ''}
              <div style="font-size: 10px; color: var(--text-muted); margin-top: 2px;">Latency: ${t.execution_time_ms}ms</div>
            </div>
          </div>
        `).join("");
      } else if (data.stderr && testCardsContainer) {
        testCardsContainer.innerHTML = `
          <div class="anti-pattern-alert" style="border-color: var(--rose);">
            <h4 style="color: var(--rose);">Execution Error</h4>
            <pre style="white-space: pre-wrap; font-family: var(--font-mono); font-size: 11px; color: var(--rose);">${escapeHTML(data.stderr)}</pre>
          </div>
        `;
      }

      if (data.fault_localization) {
        renderFaultLocalization(data.fault_localization);
      }

      analyzeAST();
      loadLeitnerCards();
      loadStats();
    } catch (err) {
      console.error("Test execution failed:", err);
      if (consoleStatus) consoleStatus.textContent = "Execution request failed.";
    } finally {
      runPending = false;
      if (btnRun) btnRun.disabled = challengeLoading || !editorChallengeId;
    }
  }

  function renderFaultLocalization(report) {
    if (!sbflSummaryBox || !sbflTableContainer) return;

    if (!report.has_failures) {
      sbflSummaryBox.style.display = "block";
      sbflSummaryBox.style.borderColor = "var(--emerald)";
      if (sbflHeadline) {
        sbflHeadline.textContent = "✓ Clean Spectrum Execution";
        sbflHeadline.style.color = "var(--emerald)";
      }
      if (sbflDesc) sbflDesc.textContent = "All test assertions passed. Line suspiciousness is 0.00 across all execution traces.";
      sbflTableContainer.innerHTML = `
        <div style="background: var(--emerald-bg); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 4px; padding: 10px;">
          <p style="font-size: 11px; color: var(--emerald); font-family: var(--font-mono);">
            Zero fault anomalies detected. Mathematical execution paths fully consistent.
          </p>
        </div>
      `;
      return;
    }

    sbflSummaryBox.style.display = "block";
    sbflSummaryBox.style.borderColor = "var(--rose)";
    if (sbflHeadline) {
      sbflHeadline.textContent = `Suspect Line ${report.most_suspicious_line || '?'}`;
      sbflHeadline.style.color = "var(--rose)";
    }
    if (sbflDesc) sbflDesc.textContent = report.pedagogical_diagnosis;

    if (report.line_scores && report.line_scores.length > 0) {
      sbflTableContainer.innerHTML = `
        <table class="halstead-table" style="font-size: 10px;">
          <thead>
            <tr>
              <th>LINE</th>
              <th>SNIPPET</th>
              <th>OCHIAI</th>
              <th>TARANTULA</th>
              <th>VERDICT</th>
            </tr>
          </thead>
          <tbody>
            ${report.line_scores.map(s => `
              <tr style="cursor:pointer;" onclick="jumpToEditorLine(${s.line})" title="Click to jump to line ${s.line} in editor">
                <td style="color:var(--cyan); font-weight:700;">L${s.line}</td>
                <td style="font-family:var(--font-mono); color:var(--text-main);">${escapeHTML(s.source_snippet)}</td>
                <td class="t-val ${s.ochiai_score >= 0.7 ? 'rose' : 'amber'}">${(s.ochiai_score * 100).toFixed(0)}%</td>
                <td class="t-val">${(s.tarantula_score * 100).toFixed(0)}%</td>
                <td>
                  <span class="badge ${s.verdict === 'CRITICAL' ? 'badge-hard' : s.verdict === 'SUSPICIOUS' ? 'badge-medium' : 'badge-easy'}">
                    ${s.verdict}
                  </span>
                </td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      `;
    }
  }

  window.jumpToEditorLine = (line) => {
    switchWorkspace("ws-code");
    if (!codeEditor) return;
    const lines = codeEditor.value.split("\n");
    let pos = 0;
    for (let i = 0; i < line - 1 && i < lines.length; i++) {
      pos += lines[i].length + 1;
    }
    codeEditor.focus();
    codeEditor.setSelectionRange(pos, pos + (lines[line - 1]?.length || 0));
    const lineHeight = 20;
    codeEditor.scrollTop = Math.max(0, (line - 4) * lineHeight);
    if (lineNumbers) lineNumbers.scrollTop = codeEditor.scrollTop;
  };

  // --------------------------------------------------------------------------
  // Dynamic Property Fuzz Testing
  // --------------------------------------------------------------------------
  async function runPropertyFuzzing() {
    if (challengeLoading || !editorChallengeId || fuzzPending) return;
    fuzzPending = true;
    const requestChallenge = currentChallengeId;
    const requestCode = codeEditor.value;
    if (consoleStatus) consoleStatus.textContent = "Running property-based fuzz stress testing...";
    [btnFuzz, btnRunFuzzInner].forEach(button => { if (button) button.disabled = true; });

    switchWorkspace("ws-code");
    document.querySelector('.panel-tab-btn[data-tab="tab-fuzz"]')?.click();

    try {
      const res = await apiFetch("/api/fuzz", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          challenge_id: currentChallengeId,
          code: codeEditor.value
        })
      });
      const data = await res.json();
      if (requestChallenge !== currentChallengeId || requestCode !== codeEditor.value) return;
      lastFuzzCode = requestCode;
      updateResultFreshness();

      if (fuzzSummaryBox) fuzzSummaryBox.style.display = "flex";
      if (data.all_invariants_held) {
        if (fuzzSummaryBox) fuzzSummaryBox.className = "test-summary pass";
        if (fuzzSummaryText) fuzzSummaryText.textContent = `✓ ${data.passed_fuzz_tests} / ${data.total_fuzz_tests} Invariants Held (100%)`;
        if (fuzzSummaryMeta) fuzzSummaryMeta.textContent = "Stress Passed";
        if (consoleStatus) consoleStatus.textContent = "All algebraic invariants held under property fuzzing!";
      } else {
        if (fuzzSummaryBox) fuzzSummaryBox.className = "test-summary fail";
        if (fuzzSummaryText) fuzzSummaryText.textContent = `✕ ${data.passed_fuzz_tests} / ${data.total_fuzz_tests} Invariants Held`;
        if (fuzzSummaryMeta) fuzzSummaryMeta.textContent = "Violations";
        if (consoleStatus) consoleStatus.textContent = "Property fuzzing detected invariant violations under extreme boundaries.";
      }

      if (fuzzCardsContainer) {
        fuzzCardsContainer.innerHTML = data.fuzz_results.map(f => `
          <div class="test-card" style="border-left: 3px solid ${f.invariant_held ? 'var(--emerald)' : 'var(--rose)'};">
            <div class="test-card-head">
              <span class="test-card-desc">Fuzz #${f.fuzz_index}: ${escapeHTML(f.property_name)}</span>
              <span class="badge ${f.invariant_held ? 'badge-easy' : 'badge-hard'}">${f.invariant_held ? 'HELD' : 'VIOLATED'}</span>
            </div>
            <div class="test-details">
              <div>Vector: <span class="call">${escapeHTML(f.input_repr)}</span></div>
              <div>Result: <span class="${f.invariant_held ? 'act-pass' : 'act-fail'}">${escapeHTML(f.output_repr)}</span></div>
              ${f.error_message ? `<div style="color:var(--rose);">${escapeHTML(f.error_message)}</div>` : ''}
              <div style="font-size:10px; color:var(--text-muted); margin-top:2px;">Stress Latency: ${f.latency_ms}ms</div>
            </div>
          </div>
        `).join("");
      }
    } catch (err) {
      console.error("Fuzz testing error:", err);
      if (consoleStatus) consoleStatus.textContent = "Property fuzzing network error.";
    } finally {
      fuzzPending = false;
      [btnFuzz, btnRunFuzzInner].forEach(button => { if (button) button.disabled = challengeLoading || !editorChallengeId; });
    }
  }

  btnFuzz?.addEventListener("click", runPropertyFuzzing);
  btnRunFuzzInner?.addEventListener("click", runPropertyFuzzing);

  // --------------------------------------------------------------------------
  // Leitner Spaced Repetition Station
  // --------------------------------------------------------------------------
  async function loadLeitnerCards() {
    try {
      const res = await apiFetch("/api/leitner");
      const cards = await res.json();

      for (let i = 1; i <= 5; i++) {
        const countEl = document.getElementById(`lbox-${i}-count`);
        const cardsEl = document.getElementById(`lbox-${i}-cards`);
        if (countEl) countEl.textContent = "0";
        if (cardsEl) cardsEl.innerHTML = "";
      }

      const dueList = document.getElementById("leitner-due-list");
      let dueCount = 0;
      let dueHtml = "";

      cards.forEach(c => {
        const boxCardsEl = document.getElementById(`lbox-${c.box}-cards`);
        const chal = challenges.find(ch => ch.id === c.challenge_id);
        const title = chal ? chal.title : c.challenge_id;

        if (boxCardsEl) {
          const pill = document.createElement("div");
          pill.className = "card-pill";
          pill.textContent = `${c.is_due ? '⚡ ' : ''}${title}`;
          pill.title = `Interval: ${c.interval_days}d · Next due: ${new Date(c.next_due).toLocaleDateString()}`;
          pill.addEventListener("click", () => {
            selectChallenge(c.challenge_id);
            switchWorkspace("ws-code");
          });
          boxCardsEl.appendChild(pill);
        }

        if (c.is_due) {
          dueCount++;
          dueHtml += `
            <div class="due-item">
              <div>
                <div class="due-title">${title}</div>
                <div class="due-meta">Box ${c.box} (${c.interval_days}d interval) · Due for recall today</div>
              </div>
              <button type="button" class="btn btn-secondary btn-sm" onclick="selectAndLaunch('${c.challenge_id}')">Launch Drill</button>
            </div>
          `;
        }
      });

      for (let i = 1; i <= 5; i++) {
        const countEl = document.getElementById(`lbox-${i}-count`);
        const cardsEl = document.getElementById(`lbox-${i}-cards`);
        if (countEl && cardsEl) {
          countEl.textContent = cardsEl.children.length;
        }
      }

      if (dueCount > 0) {
        if (leitnerDueCount) {
          leitnerDueCount.style.display = "inline-block";
          leitnerDueCount.textContent = dueCount;
        }
        if (dueList) dueList.innerHTML = dueHtml;
      } else {
        if (leitnerDueCount) leitnerDueCount.style.display = "none";
        if (dueList) {
          dueList.innerHTML = `<p style="color: var(--text-dim); font-size: 12px; font-family: var(--font-mono);">No challenges due for recall review at this moment. You are caught up!</p>`;
        }
      }
    } catch (err) {
      console.error("Failed to load Leitner cards:", err);
    }
  }

  window.selectAndLaunch = (id) => {
    selectChallenge(id);
    switchWorkspace("ws-code");
  };

  // --------------------------------------------------------------------------
  // Socratic Mentoring Controller (Dock & Terminal)
  // --------------------------------------------------------------------------
  async function consultSocrates(studentPrompt = null) {
    if (challengeLoading || !editorChallengeId) return;
    const requestChallenge = currentChallengeId;
    const requestCode = codeEditor.value;
    if (consoleStatus) consoleStatus.textContent = "Consulting Socratic Pedagogical Coach...";
    try {
      const payload = {
        challenge_id: currentChallengeId,
        code: codeEditor.value,
        hint_level: currentHintLevel,
        student_question: studentPrompt,
        chat_history: chatHistory,
        failed_test: lastFailedTest
      };

      const res = await apiFetch("/api/socratic-hint", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (requestChallenge !== currentChallengeId || requestCode !== codeEditor.value) return;

      if (dockSocTier) dockSocTier.textContent = data.level_name;
      if (dockSocTitle) dockSocTitle.textContent = data.title;
      if (dockSocGuidance) dockSocGuidance.textContent = data.guidance;
      if (dockSocQuestion) dockSocQuestion.textContent = data.question_to_ponder;

      if (terminalTierPill) terminalTierPill.textContent = data.level_name.toUpperCase();

      if (studentPrompt) {
        appendTerminalMsg("student", studentPrompt);
        chatHistory.push({ role: "student", content: studentPrompt });
      }

      const tutorResponse = `${data.guidance}\n\n→ Invariant Question: ${data.question_to_ponder}`;
      appendTerminalMsg("tutor", tutorResponse);
      chatHistory.push({ role: "tutor", content: tutorResponse });

      if (consoleStatus) consoleStatus.textContent = `Socratic Advice (${data.level_name}) ready.`;
      currentHintLevel = currentHintLevel >= 3 ? 1 : currentHintLevel + 1;
    } catch (err) {
      console.error("Socratic consultation error:", err);
    }
  }

  function appendTerminalMsg(role, text) {
    if (!terminalChatLog) return;
    const msgEl = document.createElement("div");
    msgEl.className = `terminal-msg ${role}`;
    const promptLabel = role === "student" ? "You" : "Tark · Coach";
    msgEl.innerHTML = `
      <span class="t-prompt">${promptLabel}</span>
      <div style="white-space: pre-wrap;">${escapeHTML(text)}</div>
    `;
    terminalChatLog.appendChild(msgEl);
    terminalChatLog.scrollTop = terminalChatLog.scrollHeight;
  }

  document.querySelectorAll(".s-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const q = chip.getAttribute("data-query");
      if (q) consultSocrates(q);
    });
  });

  if (dockChatForm) {
    dockChatForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const q = dockChatInput?.value.trim();
      if (!q) return;
      consultSocrates(q);
      if (dockChatInput) dockChatInput.value = "";
    });
  }

  if (terminalInputForm) {
    terminalInputForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const q = terminalInputField?.value.trim();
      if (!q) return;
      consultSocrates(q);
      if (terminalInputField) terminalInputField.value = "";
    });
  }

  // --------------------------------------------------------------------------
  // User Telemetry & Stats Loading
  // --------------------------------------------------------------------------
  async function loadStats() {
    try {
      const res = await apiFetch("/api/stats");
      const data = await res.json();
      if (statStreak) statStreak.textContent = `${data.streak_days}d`;
      if (statLoc) statLoc.textContent = data.total_loc_analyzed;
    } catch (err) {
      console.error("Failed to load user stats:", err);
    }
  }

  // --------------------------------------------------------------------------
  // Top Level Action Bindings
  // --------------------------------------------------------------------------
  btnRun?.addEventListener("click", runTests);
  btnAnalyze?.addEventListener("click", analyzeAST);
  btnHint?.addEventListener("click", () => consultSocrates());
  btnReset?.addEventListener("click", () => {
    const chal = challenges.find(c => c.id === currentChallengeId);
    if (chal && confirm("Reset your editor to starter template?")) {
      codeEditor.value = chal.starter_code;
      updateLineNumbers();
      analyzeAST();
    }
  });

  // Boot Studio
  loadCurriculum();
});
