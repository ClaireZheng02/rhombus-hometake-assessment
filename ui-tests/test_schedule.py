
from pathlib import Path
import re

from playwright.sync_api import sync_playwright, expect

BASE = Path(__file__).resolve().parent.parent
AUTH = BASE / ".auth" / "state.json"

WORKFLOW_URL = "https://rhombusai.com/workflow/5346"


def test_schedule_configuration():

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
            # Step 1: Open Workflow
            page.goto(
                WORKFLOW_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            expect(
                page.get_by_text("Canvas", exact=True).first
            ).to_be_visible(timeout=30000)

            print("PASS: Workflow loaded")

            # Step 2: Open Schedule
            schedule_tab = page.get_by_text(
                "Schedule", exact=True
            ).first

            expect(schedule_tab).to_be_visible()
            schedule_tab.click()

            expect(
                page.get_by_text(
                    "Manage schedules within this project"
                )
            ).to_be_visible(timeout=15000)

            print("PASS: Schedule panel opened")

            # Step 3: Verify schedule exists
            expect(
                page.get_by_text(
                    "Schedule for Home", exact=False
                ).first
            ).to_be_visible(timeout=15000)

            print("PASS: Existing schedule found")

            # Step 4: Verify frequency
            cron_pattern = re.compile(
                r"\*/3\s+\*\s+\*\s+\*\s+\*"
            )

            expect(
                page.get_by_text(cron_pattern).first
            ).to_be_visible(timeout=10000)

            print("PASS: Custom cron frequency verified")

            # Step 5: Verify exact status
            inactive = page.get_by_text(
                "Inactive", exact=True
            ).first

            expect(inactive).to_be_visible(timeout=10000)

            print("PASS: Schedule is Inactive")

            # Step 6: Save evidence
            evidence = BASE / "schedule_test_passed.png"

            page.screenshot(
                path=str(evidence),
                full_page=False
            )

            print("Screenshot saved:", evidence)

        finally:
            context.close()
            browser.close()
