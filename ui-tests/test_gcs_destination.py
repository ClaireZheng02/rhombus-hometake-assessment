
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

BASE = Path(__file__).resolve().parent.parent
AUTH = BASE / ".auth" / "state.json"

WORKFLOW_URL = "https://rhombusai.com/workflow/5346"
GCS_BUCKET = "rhombus-etl-output-20261016-01"


def test_gcs_destination():

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
            # 1. Open existing workflow
            page.goto(
                WORKFLOW_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            expect(
                page.get_by_text("Canvas", exact=True).first
            ).to_be_visible(timeout=30000)

            print("PASS: Workflow loaded")

            # 2. Open Data Output node
            output_node = page.get_by_text(
                "Data Output", exact=True
            ).first

            expect(output_node).to_be_visible(
                timeout=15000
            )

            output_node.click()

            print("PASS: Data Output clicked")

            # 3. Verify destination settings panel
            expect(
                page.get_by_text(
                    "Select Destination", exact=True
                ).first
            ).to_be_visible(timeout=15000)

            print("PASS: Destination panel opened")

            # 4. Verify expected GCS bucket is displayed
            expect(
                page.get_by_text(
                    GCS_BUCKET, exact=False
                ).first
            ).to_be_visible(timeout=20000)

            print("PASS: Expected GCS bucket found")

            # 5. Save evidence
            evidence = BASE / "gcs_test_passed.png"

            page.screenshot(
                path=str(evidence),
                full_page=False
            )

            print("Screenshot saved:", evidence)

        finally:
            context.close()
            browser.close()
