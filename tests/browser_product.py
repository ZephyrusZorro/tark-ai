"""Product improvements: safe highlighting, filtering, and resilient drafts."""
import sys
from playwright.sync_api import sync_playwright, expect


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    failures = []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge")

        def load():
            page.goto(url)
            page.wait_for_function("!document.getElementById('code-editor').disabled && document.getElementById('code-editor').value.length > 0")

        def highlighting_preserves_literal_source():
            load()
            code = 'def answer():\n    # a comment\n    return "<img src=x onerror=window.bad=1>"'
            page.locator("#code-editor").fill(code)
            expect(page.locator("#code-highlight .token-keyword").first).to_have_text("def")
            assert page.locator("#code-highlight").text_content() == code + "\n"
            assert page.locator("#code-highlight img").count() == 0
            assert not page.evaluate("Boolean(window.bad)")

        def drafts_survive_reload_including_empty_draft():
            load()
            code = "# keep my work after reload\ndef answer():\n    return 42"
            page.locator("#code-editor").fill(code)
            page.reload()
            expect(page.locator("#code-editor")).to_have_value(code)
            page.locator("#code-editor").fill("")
            page.reload()
            expect(page.locator("#code-editor")).to_have_value("")
            page.wait_for_function("!document.getElementById('code-editor').disabled")
            assert page.locator("#code-editor").input_value() == ""

        def challenge_search_has_results_and_empty_state():
            load()
            page.locator("#challenge-search").fill("sliding")
            expect(page.locator(".challenge-item:visible")).to_have_count(2)
            page.locator("#challenge-search").fill("nothing-matches-this")
            expect(page.locator("#challenge-search-empty")).to_be_visible()
            page.locator("#challenge-search").fill("")
            expect(page.locator(".challenge-item:visible")).to_have_count(10)

        def blocked_storage_keeps_app_and_tab_drafts_working():
            page.add_init_script("Storage.prototype.setItem = function(){throw new DOMException('Blocked','SecurityError')}; Storage.prototype.getItem = function(){throw new DOMException('Blocked','SecurityError')};")
            load()
            page.locator("#code-editor").fill("# retained in this tab")
            page.locator('.challenge-item[data-id="longest_unique_substring"]').click()
            page.wait_for_function("document.getElementById('editor-filename').textContent.includes('longest_unique_substring')")
            page.locator('.challenge-item[data-id="two_sum_sorted"]').click()
            expect(page.locator("#code-editor")).to_have_value("# retained in this tab")

        def edited_code_marks_old_test_results_outdated():
            load()
            page.locator("#btn-run").click()
            expect(page.locator("#test-summary-box")).to_be_visible()
            expect(page.locator("#test-summary-text")).to_contain_text("100%")
            code = page.locator("#code-editor").input_value()
            page.locator("#code-editor").fill(code + "\n# changed since the last run")
            expect(page.locator("#test-freshness")).to_be_visible()
            page.locator("#btn-run").click()
            expect(page.locator("#test-freshness")).not_to_be_visible()

        def different_tabs_do_not_overwrite_each_others_drafts():
            load()
            second = page.context.new_page()
            second.goto(url)
            second.wait_for_function("!document.getElementById('code-editor').disabled")
            second.locator('.challenge-item[data-id="longest_unique_substring"]').click()
            second.wait_for_function("document.getElementById('editor-filename').textContent.includes('longest_unique_substring')")
            first_draft = "# important work in tab A"
            second_draft = "# independent work in tab B"
            page.locator("#code-editor").fill(first_draft)
            second.locator("#code-editor").fill(second_draft)
            page.reload()
            expect(page.locator("#code-editor")).to_have_value(first_draft)
            page.locator('.challenge-item[data-id="longest_unique_substring"]').click()
            expect(page.locator("#code-editor")).to_have_value(second_draft)
            second.close()

        for test in [highlighting_preserves_literal_source, drafts_survive_reload_including_empty_draft, challenge_search_has_results_and_empty_state, blocked_storage_keeps_app_and_tab_drafts_working, edited_code_marks_old_test_results_outdated, different_tabs_do_not_overwrite_each_others_drafts]:
            context = browser.new_context(viewport={"width": 1440, "height": 1000})
            page = context.new_page()
            page.set_default_timeout(2500)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            try:
                test()
                assert not errors, errors
                print("PASS", test.__name__)
            except Exception as exc:
                failures.append(test.__name__)
                print("FAIL", test.__name__, str(exc)[:170])
            context.close()
        browser.close()
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
