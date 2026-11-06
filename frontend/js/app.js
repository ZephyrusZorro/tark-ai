/**
 * TarkAI (तर्क) — Client-Side Application Controller
 * Manages editor state, AST visualizer, test runner execution, and Socratic mentoring.
 */

document.addEventListener("DOMContentLoaded", () => {
  // State
  let currentChallengeId = "two_sum_sorted";
  let challenges = [];
  let currentHintLevel = 1;
  let lastFailedTest = null;

  // DOM Elements
  const codeEditor = document.getElementById("code-editor");
  const lineNumbers = document.getElementById("line-numbers");
  const consoleStatus = document.getElementById("console-status");
  const consolePerf = document.getElementById("console-perf");
  const challengeList = document.getElementById("challenge-list");
  const curriculumCount = document.getElementById("curriculum-count");

  // Spec Elements
  const probTitle = document.getElementById("prob-title");
  const probSummary = document.getElementById("prob-summary");
  const probDescription = document.getElementById("prob-description");
  const probConstraints = document.getElementById("prob-constraints");

  // Buttons
  const btnRun = document.getElementById("btn-run");
  const btnAnalyze = document.getElementById("btn-analyze");
  const btnHint = document.getElementById("btn-hint");
  const btnReset = document.getElementById("btn-reset");

  // Tabs
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  // Test Results Elements
  const testSummaryBox = document.getElementById("test-summary-box");
  const testSummaryText = document.getElementById("test-summary-text");
  const testSummaryTime = document.getElementById("test-summary-time");
  const testCardsContainer = document.getElementById("test-cards-container");

  // AST Elements
  const astComplexity = document.getElementById("ast-complexity");
  const astNesting = document.getElementById("ast-nesting");
  const antiPatternsContainer = document.getElementById("anti-patterns-container");
  const astTreePre = document.getElementById("ast-tree-pre");

  // Socratic Elements
  const socTier = document.getElementById("soc-tier");
  const socTitle = document.getElementById("soc-title");
  const socGuidance = document.getElementById("soc-guidance");
  const socQuestion = document.getElementById("soc-question");
  const chatForm = document.getElementById("chat-form");
  const chatQuery = document.getElementById("chat-query");

  // --------------------------------------------------------------------------
  // Tab Navigation
  // --------------------------------------------------------------------------
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");
      tabButtons.forEach(b => b.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));

      btn.classList.add("active");
      document.getElementById(targetTab)?.classList.add("active");
    });
  });

  // --------------------------------------------------------------------------
  // Editor Line Numbers & Keyboard Handlers
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

    // Ctrl+Enter / Cmd+Enter runs tests
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

      challengeList.innerHTML = challenges.map(c => `
        <div class="challenge-item ${c.id === currentChallengeId ? 'active' : ''}" data-id="${c.id}">
          <div>
            <div class="challenge-title">${c.solved ? '✓ ' : ''}${c.title}</div>
            <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">${c.track.split(':')[0]}</div>
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
    } catch (err) {
      console.error("Failed to load curriculum", err);
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

      probTitle.textContent = data.title;
      probSummary.textContent = data.summary;
      probDescription.innerHTML = data.description
        .replace(/### (.*?)\n/g, '<h3>$1</h3>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n\n/g, '<br><br>');

      probConstraints.innerHTML = data.constraints.map(c => `<li>${c}</li>`).join("");

      codeEditor.value = data.starter_code;
      updateLineNumbers();

      // Trigger automatic initial AST inspection
      analyzeAST();
    } catch (err) {
      console.error("Failed to load challenge details", err);
    }
  }

  // --------------------------------------------------------------------------
  // AST Analysis (/api/analyze)
  // --------------------------------------------------------------------------
  async function analyzeAST() {
    consoleStatus.textContent = "Parsing AST & calculating complexity...";
    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: codeEditor.value })
      });
      const data = await res.json();

      if (!data.syntax_valid) {
        astComplexity.textContent = "Syntax Error";
        astComplexity.style.color = "var(--rose)";
        astNesting.textContent = `Line ${data.syntax_line || '?'}`;
        antiPatternsContainer.innerHTML = `
          <div class="anti-pattern-alert" style="border-color: var(--rose); background: var(--rose-bg);">
            <h4 style="color: var(--rose);">Syntax Error Detected</h4>
            <p>${data.syntax_error}</p>
          </div>
        `;
        astTreePre.textContent = JSON.stringify({ error: data.syntax_error }, null, 2);
        consoleStatus.textContent = `Syntax Error on line ${data.syntax_line}.`;
        return;
      }

      // Valid AST
      astComplexity.textContent = data.complexity.estimated_time;
      astComplexity.style.color = "var(--cyan)";
      astNesting.textContent = `${data.complexity.max_loop_nesting} Level${data.complexity.max_loop_nesting === 1 ? '' : 's'}`;

      if (data.anti_patterns && data.anti_patterns.length > 0) {
        antiPatternsContainer.innerHTML = data.anti_patterns.map(p => `
          <div class="anti-pattern-alert">
            <h4>[${p.severity.toUpperCase()}] ${p.message}</h4>
            <p><strong>Suggestion:</strong> ${p.suggestion}</p>
          </div>
        `).join("");
      } else {
        antiPatternsContainer.innerHTML = `
          <div style="background: var(--emerald-bg); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 6px; padding: 10px; margin-bottom: 10px;">
            <p style="font-size: 11px; color: var(--emerald);">✓ Zero anti-patterns detected. Clean idiomatic Python structure.</p>
          </div>
        `;
      }

      astTreePre.textContent = JSON.stringify(data.tree_hierarchy, null, 2);
      consoleStatus.textContent = `AST Parsed: ${data.complexity.estimated_time} (${data.complexity.reason})`;
    } catch (err) {
      console.error("AST error", err);
      consoleStatus.textContent = "AST parsing network error.";
    }
  }

  // --------------------------------------------------------------------------
  // Sandboxed Test Execution (/api/run)
  // --------------------------------------------------------------------------
  async function runTests() {
    consoleStatus.textContent = "Executing sandboxed test runner...";
    btnRun.disabled = true;

    // Switch to test results tab
    document.querySelector('.tab-btn[data-tab="tab-tests"]').click();

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
        consoleStatus.textContent = "All test cases passed successfully!";
        lastFailedTest = null;
        loadCurriculum(); // Refresh solved indicators
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
              <div style="font-size: 10px; color: var(--text-muted); margin-top: 4px;">Latency: ${t.execution_time_ms}ms</div>
            </div>
          </div>
        `).join("");
      } else if (data.stderr) {
        testCardsContainer.innerHTML = `
          <div class="anti-pattern-alert" style="border-color: var(--rose); background: var(--rose-bg);">
            <h4 style="color: var(--rose);">Execution Error</h4>
            <p style="white-space: pre-wrap; font-family: var(--font-mono); font-size: 11px;">${data.stderr}</p>
          </div>
        `;
      }

      // Also refresh AST analysis
      analyzeAST();
    } catch (err) {
      console.error("Test execution failed", err);
      consoleStatus.textContent = "Execution request failed.";
    } finally {
      btnRun.disabled = false;
    }
  }

  // --------------------------------------------------------------------------
  // Socratic Guidance (/api/socratic-hint)
  // --------------------------------------------------------------------------
  async function fetchSocraticHint(userQuestion = null) {
    consoleStatus.textContent = "Consulting Socratic Coach...";
    try {
      const res = await fetch("/api/socratic-hint", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          challenge_id: currentChallengeId,
          code: codeEditor.value,
          hint_level: currentHintLevel,
          student_question: userQuestion,
          failed_test: lastFailedTest
        })
      });
      const data = await res.json();

      // Switch to Socratic tab
      document.querySelector('.tab-btn[data-tab="tab-socratic"]').click();

      socTier.textContent = data.level_name;
      socTitle.textContent = data.title;
      socGuidance.textContent = data.guidance;
      socQuestion.textContent = data.question_to_ponder;

      consoleStatus.textContent = `Socratic Hint (${data.level_name}) ready.`;

      // Cycle to next level for subsequent clicks
      currentHintLevel = currentHintLevel >= 3 ? 1 : currentHintLevel + 1;
    } catch (err) {
      console.error("Socratic hint error", err);
    }
  }

  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const query = chatQuery.value.trim();
    if (!query) return;
    fetchSocraticHint(query);
    chatQuery.value = "";
  });

  // --------------------------------------------------------------------------
  // Event Bindings
  // --------------------------------------------------------------------------
  btnRun.addEventListener("click", runTests);
  btnAnalyze.addEventListener("click", analyzeAST);
  btnHint.addEventListener("click", () => fetchSocraticHint());
  btnReset.addEventListener("click", () => {
    const chal = challenges.find(c => c.id === currentChallengeId);
    if (chal && confirm("Reset your editor to starter template?")) {
      codeEditor.value = chal.starter_code;
      updateLineNumbers();
      analyzeAST();
    }
  });

  // Initial Boot
  loadCurriculum();
});
