"""Run against a local Tark server: python tests/browser_regressions.py URL."""
import sys
from playwright.sync_api import sync_playwright, expect


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    failures = []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge")
        page = browser.new_page(viewport={"width": 1440, "height": 1000})

        def load():
            page.goto(url)
            page.wait_for_function("document.getElementById('code-editor').value.length > 10")

        def successful_run_preserves_solution():
            load()
            code = "def two_sum_sorted(numbers, target):\n    # preserve this solution\n    for i in range(len(numbers)):\n        for j in range(i + 1, len(numbers)):\n            if numbers[i] + numbers[j] == target:\n                return [i + 1, j + 1]\n    return []"
            page.locator("#code-editor").fill(code)
            page.locator("#btn-run").click()
            expect(page.locator("#test-summary-text")).to_contain_text("100%")
            page.wait_for_timeout(500)
            assert page.locator("#code-editor").input_value() == code

        def switching_challenges_preserves_drafts():
            load()
            code = "# unfinished draft\ndef two_sum_sorted(numbers, target):\n    return []"
            page.locator("#code-editor").fill(code)
            page.locator('.challenge-item[data-id="longest_unique_substring"]').click()
            page.wait_for_timeout(400)
            page.locator('.challenge-item[data-id="two_sum_sorted"]').click()
            page.wait_for_timeout(400)
            assert page.locator("#code-editor").input_value() == code

        def result_html_is_text():
            load()
            page.locator("#code-editor").fill('def two_sum_sorted(numbers, target):\n    return "<img src=x onerror=window.__injected=1>"')
            page.locator("#btn-run").click()
            expect(page.locator("#test-summary-text")).to_contain_text("Tests Passed")
            expect(page.locator("#test-cards-container")).to_contain_text("<img")
            assert page.evaluate("window.__injected !== 1")

        def fuzz_output_is_text():
            load()
            page.locator("#code-editor").fill('def two_sum_sorted(numbers, target):\n    return "<img src=x onerror=window.__injected=1>"')
            page.locator("#btn-fuzz").click()
            expect(page.locator("#fuzz-summary-text")).to_contain_text("Invariants")
            expect(page.locator("#fuzz-cards-container")).to_contain_text("<img")
            assert page.evaluate("window.__injected !== 1")

        def rapid_selection_does_not_copy_another_draft():
            load()
            page.locator("#code-editor").fill("# draft for two sum only")
            pending = []
            page.route("**/api/challenge/longest_unique_substring", lambda route: pending.append(route))
            page.locator('.challenge-item[data-id="longest_unique_substring"]').click()
            page.wait_for_timeout(100)
            assert page.locator("#btn-run").is_disabled()
            page.locator('.challenge-item[data-id="search_rotated_array"]').click()
            page.wait_for_function("document.getElementById('editor-filename').textContent.includes('search_rotated_array')")
            for route in pending:
                route.abort()
            page.unroute("**/api/challenge/longest_unique_substring")
            page.locator('.challenge-item[data-id="longest_unique_substring"]').click()
            page.wait_for_function("document.getElementById('editor-filename').textContent.includes('longest_unique_substring')")
            assert "# draft for two sum only" not in page.locator("#code-editor").input_value()

        def failed_selection_preserves_current_challenge():
            load()
            page.locator("#code-editor").fill("# keep this draft")
            page.route("**/api/challenge/longest_unique_substring", lambda route: route.fulfill(status=503, json={"detail": "Unavailable"}))
            page.locator('.challenge-item[data-id="longest_unique_substring"]').click()
            expect(page.locator("#console-status")).to_contain_text("draft is preserved")
            assert page.locator('.challenge-item[data-id="two_sum_sorted"]').evaluate("node => node.classList.contains('active')")
            assert page.locator("#code-editor").input_value() == "# keep this draft"
            assert page.locator("#btn-run").is_enabled()
            page.unroute("**/api/challenge/longest_unique_substring")

        def repeated_run_shortcut_submits_once():
            load()
            pending = []
            page.route("**/api/run", lambda route: pending.append(route))
            page.locator("#code-editor").press("Control+Enter")
            page.locator("#code-editor").press("Control+Enter")
            page.wait_for_timeout(100)
            count = len(pending)
            for route in pending:
                route.abort()
            page.unroute("**/api/run")
            assert count == 1, f"One shortcut burst sent {count} submissions"

        for test in [successful_run_preserves_solution, switching_challenges_preserves_drafts, result_html_is_text, fuzz_output_is_text, rapid_selection_does_not_copy_another_draft, failed_selection_preserves_current_challenge, repeated_run_shortcut_submits_once]:
            try:
                test()
                print("PASS", test.__name__)
            except Exception as exc:
                failures.append(test.__name__)
                print("FAIL", test.__name__, str(exc)[:200])
        browser.close()
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
