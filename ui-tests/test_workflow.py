
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

WORKFLOW_URL = "https://rhombusai.com/workflow/5346"

AUTH_FILE = (
    Path(__file__).resolve().parent.parent
    / ".auth"
    / "state.json"
)


def test_workflow_access():
    assert AUTH_FILE.exists(), "Authentication state not found"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="msedge",
            headless=False
        )

        context = browser.new_context(
            storage_state=str(AUTH_FILE),
            viewport={"width": 1440, "height": 900}
        )

        page = context.new_page()

        try:
            page.goto(
                WORKFLOW_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            # Verify the authenticated workflow loaded
            expect(
                page.get_by_text("Canvas", exact=True).first
            ).to_be_visible(timeout=30000)

            expect(
                page.get_by_text("Workspace", exact=True).first
            ).to_be_visible()

            expect(
                page.get_by_text("Logs", exact=True).first
            ).to_be_visible()

            assert "/workflow/5346" in page.url

            print("PASS: Workflow 5346 loaded successfully")
            print("PASS: Canvas is visible")
            print("PASS: Workspace is visible")
            print("PASS: Logs is visible")

        finally:
            context.close()
            browser.close()
