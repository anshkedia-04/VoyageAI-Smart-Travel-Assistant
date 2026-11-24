from __future__ import annotations

import requests

DEFAULT_CLOUD_URL = "https://voyageai-smart-travel-assistant-1.onrender.com"
DEFAULT_LOCAL_URL = "http://localhost:8000"


def check_backend_health(base_url: str, timeout: int = 10) -> tuple[bool, str]:
    """Ping FastAPI backend root or /health endpoint without hanging."""
    clean_url = base_url.rstrip("/")
    for path in ("/health", "/"):
        try:
            resp = requests.get(f"{clean_url}{path}", timeout=timeout)
            if resp.status_code == 200:
                return True, f"Connected ({clean_url})"
        except requests.RequestException as exc:
            last_error = str(exc)
            continue
    return False, f"Unavailable or sleeping ({locals().get('last_error', 'non-200 response')})"


def query_travel_backend(
    base_url: str,
    question: str,
    model_provider: str = "groq",
    timeout: int = 120,
) -> tuple[bool, str]:
    """Send a trip planning query to the VoyageAI FastAPI backend."""
    clean_url = base_url.rstrip("/")
    payload = {"question": question, "model_provider": model_provider}
    try:
        resp = requests.post(
            f"{clean_url}/query",
            json=payload,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )
    except requests.Timeout:
        return (
            False,
            "Request timed out. If using Render free tier, click 'Wake / Check Backend' first "
            "or switch to a local FastAPI instance.",
        )
    except requests.ConnectionError:
        return (
            False,
            f"Could not connect to {clean_url}. Verify the backend server is running.",
        )
    except requests.RequestException as exc:
        return False, f"Network error: {exc}"

    if resp.status_code != 200:
        return False, f"Backend returned HTTP {resp.status_code}: {resp.text[:350]}"

    try:
        data = resp.json()
    except ValueError:
        return False, "Backend returned invalid JSON."

    answer = data.get("answer", "")
    if not answer or not str(answer).strip():
        return False, "Backend returned an empty itinerary."
    return True, str(answer)
