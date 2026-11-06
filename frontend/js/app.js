/**
 * TarkAI (तर्क) — Master Client-Side Application Studio Controller
 * Inspired by Rao Muhammad Hamza's terminal / window-manager design system.
 * Manages workspaces, AST visualization, Halstead metrics, Leitner recall, and Socratic mentoring.
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

  // Initialize Mermaid.js
  if (window.mermaid) {
    try {
      mermaid.initialize({
        startOnLoad: false,
        theme: "dark",
        securityLevel: "loose",
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
      console.warn("Mermaid init error:", e);
    }
  }

  // --------------------------------------------------------------------------
  // DOM References
  // --------------------------------------------------------------------------
  // Workspaces & Tabs
  const workspaceButtons = document.querySelectorAll(".ws-btn");
  const workspacePanes = document.querySelectorAll(".workspace-pane");
  const panelTabButtons = document.querySelectorAll(".panel-tab-btn");
  const subtabPanes = document.querySelectorAll(".subtab-pane");

  // Header & Status
  const utcClock = document.getElementById("utc-clock");
  const btnScanlines = document.getElementById("btn-scanlines");
  const scanlinesLayer = document.getElementById("scanlines-layer");
  const topChalTitle = document.getElementById("top-chal-title");
  const topTrackCode = document.getElementById("top-track-code");
  const topChalDiff = document.getElementById("top-chal-diff");

  // Stats
  const statSolved = document.getElementById("stat-solved");
  const statStreak = document.getElementById("stat-streak");
  const statLoc = document.getElementById("stat-loc");
  const leitnerDueCount = document.getElementById("leitner-due-count");

  // Editor Elements
  const codeEditor = document.getElementById("code-editor");
  const lineNumbers = document.getElementById("line-numbers");
  const consoleStatus = document.getElementById("console-status");
  const consolePerf = document.getElementById("console-perf");
  const editorFilename = document.getElementById("editor-filename");

  // Curriculum & Specs
  const challengeList = document.getElementById("challenge-list");
  const curriculumCount = document.getElementById("curriculum-count");
  const probTitle = document.getElementById("prob-title");
  const probSummary = document.getElementById("prob-summary");
  const probDescription = document.getElementById("prob-description");
  const probConstraints = document.getElementById("prob-constraints");

  // Action Buttons
  const btnRun = document.getElementById("btn-run");
  const btnAnalyze = document.getElementById("btn-analyze");
  const btnHint = document.getElementById("btn-hint");
  const btnReset = document.getElementById("btn-reset");
  const btnRefreshFlowchart = document.getElementById("btn-refresh-flowchart");
  const btnZoomReset = document.getElementById("btn-zoom-reset");

  // Test Runner Elements
  const testSummaryBox = document.getElementById("test-summary-box");
  const testSummaryText = document.getElementById("test-summary-text");
  const testSummaryTime = document.getElementById("test-summary-time");
  const testCardsContainer = document.getElementById("test-cards-container");

  // AST Elements (Quick & Full)
  const astQuickComplexity = document.getElementById("ast-quick-complexity");
  const astQuickNesting = document.getElementById("ast-quick-nesting");
  const astQuickCog = document.getElementById("ast-quick-cog");
  const astQuickCyc = document.getElementById("ast-quick-cyc");
  const quickAntiPatterns = document.getElementById("quick-anti-patterns");
  const astQuickTree = document.getElementById("ast-quick-tree");
  const mermaidGraphTarget = document.getElementById("mermaid-graph-target");
  const fullAstTree = document.getElementById("full-ast-tree");

  // Halstead Elements
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

  // Socratic Elements
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
  // Live UTC Clock & CRT Scanlines
  // --------------------------------------------------------------------------
  function updateClock() {
    const now = new Date();
    const h = String(now.getUTCHours()).padStart(2, "0");
    const m = String(now.getUTCMinutes()).padStart(2, "0");
    const s = String(now.getUTCSeconds()).padStart(2, "0");
    utcClock.textContent = `${h}:${m}:${s} UTC`;
  }
  setInterval(updateClock, 1000);
  updateClock();

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

  // --------------------------------------------------------------------------
  // Workspace Navigation (1 through 5)
  // --------------------------------------------------------------------------
  function switchWorkspace(targetId) {
    workspaceButtons.forEach(b => {
      b.classList.toggle("active", b.getAttribute("data-workspace") === targetId);
    });
    workspacePanes.forEach(p => {
      p.classList.toggle("active", p.id === targetId);
    });

    if (targetId === "ws-ast" && currentAstData && currentAstData.mermaid_flowchart) {
      renderMermaidDiagram(currentAstData.mermaid_flowchart);
    }
    if (targetId === "ws-leitner") {
      loadLeitnerCards();
    }
  }

  workspaceButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const ws = btn.getAttribute("data-workspace");
      switchWorkspace(ws);
    });
  });

  // Hotkeys: Alt+1 to Alt+5
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
      switchWorkspace(wsMap[e.key]);
    }
  });

  // Right Panel Subtabs
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
  function updateLineNumbers() {
    const lines = codeEditor.value.split("\n").length;
    lineNumbers.innerHTML = Array.from({ length: lines }, (_, i) => i + 1).join("<br>");
  }

  codeEditor.addEventListener("input", updateLineNumbers);
  codeEditor.addEventListener("scroll", () => {
    lineNumbers.scrollTop = codeEditor.scrollTop;
  });

  codeEditor.addEventListener("keydown", (e) => {
    // Tab key inserts 4 spaces
    if (e.key === "Tab") {
      e.preventDefault();
      const start = codeEditor.selectionStart;
      const end = codeEditor.selectionEnd;
      codeEditor.value = codeEditor.value.substring(0, start) + "    " + codeEditor.value.substring(end);
      codeEditor.selectionStart = codeEditor.selectionEnd = start + 4;
      updateLineNumbers();
    }

    // Ctrl+Enter or Cmd+Enter runs tests
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      runTests();
    }

    // Ctrl+Shift+A analyzes AST
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === "A" || e.key === "a")) {
      e.preventDefault();
      analyzeAST();
    }
  });

  // --------------------------------------------------------------------------
  // Curriculum & Challenge Loading
  // --------------------------------------------------------------------------
  async function loadCurriculum() {
    try {
      const res = await fetch("/api/curriculum");
      challenges = await res.json();

      const solvedCount = challenges.filter(c => c.solved).length;
      curriculumCount.textContent = `${solvedCount} / ${challenges.length} Solved`;
      statSolved.textContent = `${solvedCount}/${challenges.length}`;

      challengeList.innerHTML = challenges.map(c => `
        <div class="challenge-item ${c.id === currentChallengeId ? 'active' : ''}" data-id="${c.id}">
          <div>
            <div class="challenge-title">${c.solved ? '✓ ' : ''}${c.title}</div>
            <div style="font-size: 10px; color: var(--text-muted); font-family: var(--font-mono); margin-top: 2px;">
              ${c.track_code || c.track.split(':')[0]}
            </div>
          </div>
          <span class="badge badge-${c.difficulty.toLowerCase()}">${c.difficulty}</span>
        </div>
      `).join("");

      document.querySelectorAll(".challenge-item").forEach(item => {
        item.addEventListener("click", () => {
          const id = item.getAttribute("data-id");
          selectChallenge(id);
        });
      });

      if (challenges.length > 0) {
        selectChallenge(currentChallengeId || challenges[0].id);
      }

      loadStats();
      loadLeitnerCards();
    } catch (err) {
      console.error("Failed to load curriculum:", err);
    }
  }

  async function selectChallenge(id) {
    currentChallengeId = id;
    currentHintLevel = 1;
    lastFailedTest = null;

    document.querySelectorAll(".challenge-item").forEach(el => {
      el.classList.toggle("active", el.getAttribute("data-id") === id);
    });

    try {
      const res = await fetch(`/api/challenge/${id}`);
      const data = await res.json();

      topChalTitle.textContent = data.title;
      topTrackCode.textContent = data.track_code || data.track.split(":")[0];
      topChalDiff.textContent = data.difficulty.toUpperCase();
      topChalDiff.className = `badge badge-${data.difficulty.toLowerCase()}`;

      probTitle.textContent = data.title;
      probSummary.textContent = data.summary;
      probDescription.innerHTML = data.description
        .replace(/### (.*?)\n/g, '<h4 style="color:#fff; margin:10px 0 4px;">$1</h4>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n\n/g, '<br><br>');

      probConstraints.innerHTML = data.constraints.map(c => `<li>${c}</li>`).join("");

      editorFilename.textContent = `02_${id.toUpperCase()}.PY`;
      codeEditor.value = data.starter_code;
      updateLineNumbers();

      // Reset tests container
      testSummaryBox.style.display = "none";
      testCardsContainer.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">⚙</div>
          <p>Click <strong>"Run Tests"</strong> (Ctrl+Enter) to evaluate your algorithm against sandboxed test cases.</p>
        </div>
      `;

      analyzeAST();
    } catch (err) {
      console.error("Failed to load challenge details:", err);
    }
  }

  // --------------------------------------------------------------------------
  // AST Semantic Analysis & Flowchart Rendering
  // --------------------------------------------------------------------------
  async function analyzeAST() {
    consoleStatus.textContent = "Parsing Abstract Syntax Tree & computing Halstead bounds...";
    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: codeEditor.value, challenge_id: currentChallengeId })
      });
      const data = await res.json();
      currentAstData = data;

      if (!data.syntax_valid) {
        astQuickComplexity.textContent = "SYNTAX ERR";
        astQuickComplexity.style.color = "var(--rose)";
        astQuickNesting.textContent = `L${data.syntax_line || '?'}`;
        quickAntiPatterns.innerHTML = `
          <div class="anti-pattern-alert" style="border-color: var(--rose);">
            <h4 style="color: var(--rose);">Syntax Error Detected</h4>
            <p>${data.syntax_error} (line ${data.syntax_line})</p>
          </div>
        `;
        astQuickTree.textContent = JSON.stringify({ error: data.syntax_error }, null, 2);
        consoleStatus.textContent = `Syntax Error on line ${data.syntax_line}: ${data.syntax_error}`;
        return;
      }

      // Valid AST
      const comp = data.complexity;
      astQuickComplexity.textContent = comp.estimated_time;
      astQuickComplexity.style.color = "var(--cyan)";
      astQuickNesting.textContent = comp.max_loop_nesting;
      astQuickCog.textContent = comp.cognitive_complexity;
      astQuickCyc.textContent = comp.cyclomatic_complexity;

      // Full Halstead & Big-O View
      fullBigO.textContent = comp.estimated_time;
      fullBigOReason.textContent = comp.reason;
      fullCogVal.textContent = comp.cognitive_complexity;
      fullCycVal.textContent = comp.cyclomatic_complexity;

      if (comp.halstead) {
        const h = comp.halstead;
        hN1.textContent = h.distinct_operators;
        hN2.textContent = h.distinct_operands;
        hN1Tot.textContent = h.total_operators;
        hN2Tot.textContent = h.total_operands;
        hVocab.textContent = h.vocabulary;
        hLength.textContent = h.program_length;
        hVol.textContent = h.volume.toFixed(1);
        hDiff.textContent = h.difficulty.toFixed(2);
        hEffort.textContent = h.effort.toFixed(1);
      }

      // Anti-Patterns
      if (data.anti_patterns && data.anti_patterns.length > 0) {
        const badgesHtml = data.anti_patterns.map(p => `
          <div class="anti-pattern-alert">
            <h4>[LINE ${p.line}] ${p.message}</h4>
            <p><strong>Fix:</strong> ${p.suggestion}</p>
          </div>
        `).join("");
        quickAntiPatterns.innerHTML = badgesHtml;
        fullAntiPatternsList.innerHTML = badgesHtml;
      } else {
        const cleanMsg = `
          <div style="background: var(--emerald-bg); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 4px; padding: 8px 10px;">
            <p style="font-size: 11px; color: var(--emerald); font-family: var(--font-mono);">
              ✓ Zero anti-patterns detected. Clean idiomatic Python structure.
            </p>
          </div>
        `;
        quickAntiPatterns.innerHTML = cleanMsg;
        fullAntiPatternsList.innerHTML = cleanMsg;
      }

      // Symbol Table
      if (data.symbol_table) {
        const sym = data.symbol_table;
        symbolTableContainer.innerHTML = `
          <div style="font-family: var(--font-mono); font-size: 11px; color: var(--text-dim); display:flex; flex-direction:column; gap:6px;">
            <div>Functions: <span style="color:var(--cyan);">${sym.functions.map(f => f.name + '()').join(', ') || 'None'}</span></div>
            <div>Classes: <span style="color:var(--amber);">${sym.classes.map(c => c.name).join(', ') || 'None'}</span></div>
            <div>Imports: <span style="color:var(--purple);">${sym.imports.join(', ') || 'None'}</span></div>
          </div>
        `;
      }

      astQuickTree.textContent = JSON.stringify(data.tree_hierarchy, null, 2);
      fullAstTree.textContent = JSON.stringify(data.tree_hierarchy, null, 2);

      // Render Mermaid flowchart
      if (data.mermaid_flowchart) {
        renderMermaidDiagram(data.mermaid_flowchart);
      }

      consoleStatus.textContent = `AST Ready: ${comp.estimated_time} Complexity (${comp.reason})`;
    } catch (err) {
      console.error("AST parsing error:", err);
      consoleStatus.textContent = "AST parsing network error.";
    }
  }

  async function renderMermaidDiagram(chartDefinition) {
    if (!window.mermaid) return;
    try {
      const id = "mermaid-svg-" + Date.now();
      const { svg } = await mermaid.render(id, chartDefinition);
      mermaidGraphTarget.innerHTML = svg;
    } catch (err) {
      console.warn("Mermaid render error:", err);
      mermaidGraphTarget.innerHTML = `
        <div class="empty-state">
          <p style="color: var(--amber); font-family: var(--font-mono); font-size: 11px;">
            Flowchart render notice: Diagram syntax refreshed.
          </p>
        </div>
      `;
    }
  }

  btnRefreshFlowchart?.addEventListener("click", () => {
    if (currentAstData && currentAstData.mermaid_flowchart) {
      renderMermaidDiagram(currentAstData.mermaid_flowchart);
    } else {
      analyzeAST();
    }
  });

  btnZoomReset?.addEventListener("click", () => {
    const svg = mermaidGraphTarget.querySelector("svg");
    if (svg) {
      svg.style.transform = "none";
    }
  });

  // --------------------------------------------------------------------------
  // Sandboxed Test Execution
  // --------------------------------------------------------------------------
  async function runTests() {
    consoleStatus.textContent = "Executing sandboxed test runner...";
    btnRun.disabled = true;

    // Switch to Workspace 1, Tests tab
    switchWorkspace("ws-code");
    document.querySelector('.panel-tab-btn[data-tab="tab-tests"]')?.click();

    try {
      const res = await fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          challenge_id: currentChallengeId,
          code: codeEditor.value
        })
      });
      const data = await res.json();

      consolePerf.textContent = `${data.execution_time_ms}ms · ${data.memory_kb}KB`;

      testSummaryBox.style.display = "flex";
      if (data.overall_passed) {
        testSummaryBox.className = "test-summary pass";
        testSummaryText.textContent = `✓ ${data.passed_count} / ${data.total_count} Tests Passed (100%)`;
        testSummaryTime.textContent = `${data.execution_time_ms}ms`;
        consoleStatus.textContent = "All test assertions passed successfully!";
        lastFailedTest = null;
        loadCurriculum();
      } else {
        testSummaryBox.className = "test-summary fail";
        testSummaryText.textContent = `✕ ${data.passed_count} / ${data.total_count} Tests Passed`;
        testSummaryTime.textContent = `${data.execution_time_ms}ms`;
        consoleStatus.textContent = "Some test assertions failed. Inspect failures below.";
        lastFailedTest = data.test_results?.find(t => !t.passed) || null;
      }

      if (data.test_results && data.test_results.length > 0) {
        testCardsContainer.innerHTML = data.test_results.map(t => `
          <div class="test-card" style="border-left: 3px solid ${t.passed ? 'var(--emerald)' : 'var(--rose)'};">
            <div class="test-card-head">
              <span class="test-card-desc">${t.description}</span>
              <span class="badge ${t.passed ? 'badge-easy' : 'badge-hard'}">${t.passed ? 'PASSED' : 'FAILED'}</span>
            </div>
            <div class="test-details">
              <div>Call: <span class="call">${t.call}</span></div>
              <div>Expected: <span class="exp">${t.expected_repr}</span></div>
              <div>Actual: <span class="${t.passed ? 'act-pass' : 'act-fail'}">${t.actual_repr}</span></div>
              ${t.error_message ? `<div style="color: var(--rose); margin-top: 4px;">${t.error_message}</div>` : ''}
              <div style="font-size: 10px; color: var(--text-muted); margin-top: 2px;">Latency: ${t.execution_time_ms}ms</div>
            </div>
          </div>
        `).join("");
      } else if (data.stderr) {
        testCardsContainer.innerHTML = `
          <div class="anti-pattern-alert" style="border-color: var(--rose);">
            <h4 style="color: var(--rose);">Execution Error</h4>
            <pre style="white-space: pre-wrap; font-family: var(--font-mono); font-size: 11px; color: var(--rose);">${data.stderr}</pre>
          </div>
        `;
      }

      // Also trigger AST update
      analyzeAST();
      loadLeitnerCards();
      loadStats();
    } catch (err) {
      console.error("Test execution failed:", err);
      consoleStatus.textContent = "Execution request failed.";
    } finally {
      btnRun.disabled = false;
    }
  }

  // --------------------------------------------------------------------------
  // Leitner Spaced Repetition Station
  // --------------------------------------------------------------------------
  async function loadLeitnerCards() {
    try {
      const res = await fetch("/api/leitner");
      const cards = await res.json();

      // Clear boxes
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

      // Update box counts
      for (let i = 1; i <= 5; i++) {
        const countEl = document.getElementById(`lbox-${i}-count`);
        const cardsEl = document.getElementById(`lbox-${i}-cards`);
        if (countEl && cardsEl) {
          countEl.textContent = cardsEl.children.length;
        }
      }

      if (dueCount > 0) {
        leitnerDueCount.style.display = "inline-block";
        leitnerDueCount.textContent = dueCount;
        dueList.innerHTML = dueHtml;
      } else {
        leitnerDueCount.style.display = "none";
        dueList.innerHTML = `<p style="color: var(--text-dim); font-size: 12px; font-family: var(--font-mono);">No challenges due for recall review at this moment. You are caught up!</p>`;
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
    consoleStatus.textContent = "Consulting Socratic Pedagogical Coach...";
    try {
      const payload = {
        challenge_id: currentChallengeId,
        code: codeEditor.value,
        hint_level: currentHintLevel,
        student_question: studentPrompt,
        chat_history: chatHistory,
        failed_test: lastFailedTest
      };

      const res = await fetch("/api/socratic-hint", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      // Update Dock
      dockSocTier.textContent = data.level_name;
      dockSocTitle.textContent = data.title;
      dockSocGuidance.textContent = data.guidance;
      dockSocQuestion.textContent = data.question_to_ponder;

      // Update Terminal
      terminalTierPill.textContent = data.level_name.toUpperCase();

      if (studentPrompt) {
        appendTerminalMsg("student", studentPrompt);
        chatHistory.push({ role: "student", content: studentPrompt });
      }

      const tutorResponse = `${data.guidance}\n\n→ Invariant Question: ${data.question_to_ponder}`;
      appendTerminalMsg("tutor", tutorResponse);
      chatHistory.push({ role: "tutor", content: tutorResponse });

      consoleStatus.textContent = `Socratic Advice (${data.level_name}) ready.`;

      // Cycle hint levels (1 -> 2 -> 3 -> 1)
      currentHintLevel = currentHintLevel >= 3 ? 1 : currentHintLevel + 1;
    } catch (err) {
      console.error("Socratic consultation error:", err);
    }
  }

  function appendTerminalMsg(role, text) {
    const msgEl = document.createElement("div");
    msgEl.className = `terminal-msg ${role}`;
    const promptLabel = role === "student" ? "faris@student:~$" : "tark@socrates:~$";
    msgEl.innerHTML = `
      <span class="t-prompt">${promptLabel}</span>
      <div style="white-space: pre-wrap;">${text}</div>
    `;
    terminalChatLog.appendChild(msgEl);
    terminalChatLog.scrollTop = terminalChatLog.scrollHeight;
  }

  // Quick Chips
  document.querySelectorAll(".s-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const q = chip.getAttribute("data-query");
      consultSocrates(q);
    });
  });

  dockChatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const q = dockChatInput.value.trim();
    if (!q) return;
    consultSocrates(q);
    dockChatInput.value = "";
  });

  terminalInputForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const q = terminalInputField.value.trim();
    if (!q) return;
    consultSocrates(q);
    terminalInputField.value = "";
  });

  // --------------------------------------------------------------------------
  // User Telemetry & Stats Loading
  // --------------------------------------------------------------------------
  async function loadStats() {
    try {
      const res = await fetch("/api/stats");
      const data = await res.json();
      statStreak.textContent = `${data.streak_days}d`;
      statLoc.textContent = data.total_loc_analyzed;
    } catch (err) {
      console.error("Failed to load user stats:", err);
    }
  }

  // --------------------------------------------------------------------------
  // Top Level Action Bindings
  // --------------------------------------------------------------------------
  btnRun.addEventListener("click", runTests);
  btnAnalyze.addEventListener("click", analyzeAST);
  btnHint.addEventListener("click", () => consultSocrates());
  btnReset.addEventListener("click", () => {
    const chal = challenges.find(c => c.id === currentChallengeId);
    if (chal && confirm("Reset your editor to starter template?")) {
      codeEditor.value = chal.starter_code;
      updateLineNumbers();
      analyzeAST();
    }
  });

  // Boot
  loadCurriculum();
});
