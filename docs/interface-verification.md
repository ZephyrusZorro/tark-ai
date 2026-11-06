# Tark interface verification — 2026-11-07

## Current interface
Ink-blue glass with violet/blue accents, stronger panel hierarchy, safe Python syntax coloring, searchable challenges, larger source text, and visible draft status. Mobile layouts, keyboard navigation and reduced motion remain in place.

## Correctness improvements
- Drafts persist across reloads, including empty drafts. Blocked storage falls back to the current tab.
- Different challenges in separate tabs preserve their saved drafts.
- Source changes mark old test/fuzz results outdated until those checks run again.
- Success after failure correctly marks a challenge solved. Attempts count, best successful times are retained, and old incorrect aggregates are repaired from submission history on startup.
- Streaks reflect consecutive UTC practice dates instead of a fixed one-day value.
- Previous selection, HTML-rendering, JSON-fixture and duplicate-shortcut fixes remain covered.

## Verification
- Backend suite: 33 tests.
- Browser regressions: 7 original plus 6 product cases.
- Walkthrough: numeric/boolean runs, fuzzing, CFG/AST, complexity, recall, coaching, syntax feedback and reset.
- All 5 workspaces at 1440, 1024, 768 and 390 pixels: no page overflow.
- JavaScript syntax checks and desktop/mobile screenshots reviewed.
- Independent review checked long-line/multiline editor scroll and found a cross-tab overwrite; a failing regression passed after correction.
- Browser review uses a disposable database.

## Boundaries
Drafts are local browser data, not collaborative editing or synchronization. Clearing site data removes them. Simultaneous edits to the same challenge use the latest saved version. Syntax coloring is presentation, not a full language server. Optional Ollama behavior was not tested. Existing FastAPI/Starlette warnings remain. No database is committed.
