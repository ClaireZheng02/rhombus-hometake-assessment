
from pathlib import Path
import re

from playwright.sync_api import (
    sync_playwright,
    expect,
)

BASE = Path(__file__).resolve().parent.parent
AUTH = BASE / ".auth" / "state.json"

WORKFLOW_URL = "https://rhombusai.com/workflow/5346"


def test_execution_history():
    assert AUTH.exists(), "Authentication state missing"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="msedge",
            headless=False
        )

        context = browser.new_context(
            storage_state=str(AUTH),
            viewport={"width": 1600, "height": 1000}
        )

        page = context.new_page()

        try:
            page.goto(
                WORKFLOW_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            expect(
                page.get_by_text("Canvas", exact=True).first
            ).to_be_visible(timeout=30000)

            print("PASS: Workflow loaded")

            # Open Schedule panel
            page.get_by_text(
                "Schedule", exact=True
            ).first.click()

            expect(
                page.get_by_text(
                    "Schedule for Home-take Exercise",
                    exact=True
                ).first
            ).to_be_visible(timeout=20000)

            print("PASS: Schedule found")

            # Locate the history button
            selectors = [
                "button[aria-label*='history' i]",
                "button[title*='history' i]",
                "button[aria-label*='execution' i]",
                "button[title*='execution' i]",
                "button:has(svg.lucide-history)",
                "svg.lucide-history",
            ]

            history_clicked = False

            for selector in selectors:
                locator = page.locator(selector).first

                if locator.count() > 0 and locator.is_visible():
                    locator.click()
                    history_clicked = True
                    print("PASS: History opened")
                    break

            if not history_clicked:
                page.screenshot(
                    path=str(BASE / "history_debug.png")
                )
                raise AssertionError(
                    "History button not found. "
                    "Inspect history_debug.png."
                )

            # Verify the known successful execution
            execution = page.get_by_text(
                re.compile(r"Execution\s*#18420")
            ).first

            expect(execution).to_be_visible(timeout=20000)

            print("PASS: Execution #18420 found")

            expect(
                page.get_by_text("Success", exact=True).first
            ).to_be_visible(timeout=10000)

            print("PASS: Success status visible")

            # Save evidence
            evidence = BASE / "execution_history_passed.png"

            page.screenshot(
                path=str(evidence),
                full_page=False
            )

            print("Screenshot saved:", evidence)

        finally:
            context.close()
            browser.close()
