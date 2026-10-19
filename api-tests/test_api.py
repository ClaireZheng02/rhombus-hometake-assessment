
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path(__file__).resolve().parent.parent
AUTH = BASE / ".auth" / "state.json"

WORKFLOW_URL = "https://rhombusai.com/workflow/5346"
API_URL = "https://api.rhombusai.com/api/accounts/users/credits"


def test_api_positive_authenticated():
    """Positive: authenticated user can retrieve credits."""

    assert AUTH.exists(), "Authentication state missing"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="msedge",
            headless=False
        )

        context = browser.new_context(
            storage_state=str(AUTH)
        )

        try:
            page = context.new_page()

            # Capture the real API response triggered by the app
            with page.expect_response(
                lambda r: (
                    r.url.split("?")[0] == API_URL
                    and r.request.method == "GET"
                ),
                timeout=30000
            ) as response_info:

                page.goto(
                    WORKFLOW_URL,
                    wait_until="domcontentloaded",
                    timeout=60000
                )

            response = response_info.value

            print("API status:", response.status)

            assert response.status == 200, (
                f"Expected 200, got {response.status}"
            )

            data = response.json()

            assert isinstance(data, (dict, list)), (
                "Expected JSON object or array"
            )

            assert len(data) > 0, "API returned empty data"

            print("PASS: Authenticated API returned valid data")
            print("JSON type:", type(data).__name__)

            if isinstance(data, dict):
                print("Response fields:", list(data.keys()))

        finally:
            context.close()
            browser.close()


def test_api_negative_unauthenticated():
    """Negative: request without login credentials."""

    with sync_playwright() as p:
        # Isolated API client with no authentication state
        api = p.request.new_context(
            extra_http_headers={"Accept": "application/json"}
        )

        try:
            response = api.get(
                API_URL,
                timeout=30000,
                fail_on_status_code=False
            )

            print("Unauthenticated API status:", response.status)

            assert response.status in (401, 403), (
                "Expected authentication rejection (401/403), "
                f"but received {response.status}"
            )

            print("PASS: Unauthenticated request was rejected")

        finally:
            api.dispose()
