"""Real-browser workflow and responsive checks. Requires Playwright and Edge."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright, expect


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge")
        page = browser.new_page(viewport={"width": 1440, "height": 1000}, reduced_motion="reduce")
        page.on("dialog", lambda dialog: dialog.accept())
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(url)
        expect(page.locator(".challenge-item")).to_have_count(10)
        page.wait_for_function("document.getElementById('code-editor').value.length > 10")
        page.locator("#btn-run").click()
        expect(page.locator("#test-summary-text")).to_contain_text("100%")
        page.locator("#btn-fuzz").click()
        expect(page.locator("#fuzz-summary-text")).to_contain_text("100%")
        # A boolean-returning challenge exercises the repaired subprocess fixture path.
        page.locator('.challenge-item[data-id="valid_parentheses_stack"]').click()
        page.wait_for_function("document.getElementById('editor-filename').textContent.includes('valid_parentheses_stack')")
        page.locator("#btn-run").click()
        expect(page.locator("#test-summary-text")).to_contain_text("100%")
        page.locator("#btn-analyze").click()
        page.locator('[data-workspace="ws-ast"]').click()
        expect(page.locator("#mermaid-graph-target svg")).to_be_visible(timeout=15000)
        page.locator("#btn-view-ast").click()
        expect(page.locator("#mermaid-graph-target svg")).to_be_visible(timeout=15000)
        page.locator('[data-workspace="ws-complexity"]').click()
        expect(page.locator("#full-big-o")).to_contain_text("O(")
        page.locator('[data-workspace="ws-leitner"]').click()
        expect(page.locator(".card-pill").first).to_be_visible()
        page.locator('[data-workspace="ws-socrates"]').click()
        page.locator("#terminal-input-field").fill("What invariant should I maintain?")
        page.locator("#terminal-input-form button").click()
        expect(page.locator(".terminal-msg.tutor")).to_be_visible()
        page.locator('[data-workspace="ws-code"]').click()
        page.locator("#code-editor").fill("def invalid(:")
        page.locator("#btn-analyze").click()
        expect(page.locator("#console-status")).to_contain_text("Syntax Error")
        page.locator("#btn-reset").click()
        assert "def invalid(:" not in page.locator("#code-editor").input_value()
        for width in [1440, 768, 390]:
            page.set_viewport_size({"width": width, "height": 1000 if width == 1440 else 844})
            for index in range(5):
                page.locator(".ws-btn").nth(index).click()
                assert not page.evaluate("document.documentElement.scrollWidth > innerWidth"), (width, index)
        assert not errors, errors
        if output:
            output.mkdir(parents=True, exist_ok=True)
            page.goto(url)
            page.wait_for_function("document.getElementById('code-editor').value.length > 10")
            page.set_viewport_size({"width": 1440, "height": 1000})
            page.screenshot(path=str(output / "tark-desktop.png"), full_page=True)
            page.set_viewport_size({"width": 390, "height": 844})
            page.screenshot(path=str(output / "tark-mobile.png"), full_page=True)
        browser.close()
    print("PASS: test runner (numeric and boolean); fuzz; CFG/AST; complexity; recall; coach; syntax error/reset; 15 responsive workspace checks; no runtime errors")


if __name__ == "__main__":
    main()
