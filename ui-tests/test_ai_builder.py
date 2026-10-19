
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

BASE = Path(__file__).resolve().parent.parent
AUTH = BASE / ".auth" / "state.json"

WORKFLOW_URL = "https://rhombusai.com/workflow/5346"


def test_ai_builder_transformation():
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
            # 1. Open workflow
            page.goto(
                WORKFLOW_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            expect(
                page.get_by_text("Canvas", exact=True).first
            ).to_be_visible(timeout=30000)

            print("PASS: Workflow loaded")

            # 2. Locate Custom transformation node
            custom_node = page.get_by_text(
                "Custom", exact=True
            ).first

            expect(custom_node).to_be_visible(timeout=15000)

            custom_node.click()

            print("PASS: Custom node opened")

            # 3. Verify AI-generated transformation editor
            expect(
                page.get_by_text(
                    "Edit Prompt", exact=True
                ).first
            ).to_be_visible(timeout=15000)

            print("PASS: Prompt editor available")

            expect(
                page.get_by_text(
                    "Edit Code", exact=True
                ).first
            ).to_be_visible(timeout=10000)

            print("PASS: Code editor available")

            # 4. Verify regeneration option
            # Do not click it: regeneration may change code.
            expect(
                page.get_by_text(
                    "Regenerate Code", exact=True
                ).first
            ).to_be_visible(timeout=10000)

            print("PASS: Code regeneration option visible")

            # 5. Save evidence
            evidence = BASE / "ai_builder_test_passed.png"

            page.screenshot(
                path=str(evidence),
                full_page=False
            )

            print("Screenshot saved:", evidence)

        finally:
            context.close()
            browser.close()
