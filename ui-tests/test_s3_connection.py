
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

BASE = Path(__file__).resolve().parent.parent
AUTH = BASE / ".auth" / "state.json"

WORKFLOW_URL = "https://rhombusai.com/workflow/5346"
S3_PATH = "s3://rhombus-ai-etl-test-20261016-01/input/"


def test_s3_connection():

    assert AUTH.exists(), "Authentication state is missing"

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
            # Open workflow
            page.goto(
                WORKFLOW_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            expect(
                page.get_by_text("Canvas", exact=True).first
            ).to_be_visible(timeout=30000)

            # Open Data Input settings
            page.get_by_text(
                "Data Input", exact=True
            ).first.click()

            # Open third-party sources
            page.get_by_text(
                "Third Party Sources", exact=True
            ).first.click()

            # Verify the S3 source has loaded
            expect(
                page.get_by_text(
                    "Orders Test Source", exact=True
                )
            ).to_be_visible(timeout=30000)

            print("PASS: Orders Test Source exists")

            # Verify the storage provider
            expect(
                page.get_by_text(
                    "Amazon S3", exact=True
                ).first
            ).to_be_visible()

            print("PASS: Amazon S3 provider identified")

            # Verify the expected bucket and prefix
            expect(
                page.get_by_text(
                    S3_PATH, exact=False
                ).first
            ).to_be_visible(timeout=15000)

            print("PASS: S3 bucket and prefix match")

            # Save test evidence
            evidence = BASE / "s3_test_passed.png"

            page.screenshot(
                path=str(evidence),
                full_page=False
            )

            print("PASS: S3 UI assertions completed")
            print("Evidence saved:", evidence)

        finally:
            context.close()
            browser.close()
