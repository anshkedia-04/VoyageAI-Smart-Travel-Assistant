from __future__ import annotations

import os

import requests

DEFAULT_CLOUD_URL = "https://voyageai-smart-travel-assistant-1.onrender.com"
DEFAULT_LOCAL_URL = "http://localhost:8000"

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"

DIRECT_SYSTEM_PROMPT = (
    "You are VoyageAI, an expert AI travel agent and expense planner. "
    "Provide a complete, practical travel plan with both classic highlights and off-beat gems. "
    "Format clearly with Day 1:, Day 2:, ... headings, followed by sections for "
    "Hotels:, Restaurants:, Activities:, Transportation:, Cost Breakdown:, Per Day Expense Budget:, and Weather:."
)


def get_default_backend_url() -> str:
    """Resolve backend URL from VOYAGEAI_BACKEND_URL env var or default cloud endpoint."""
    env_url = os.getenv("VOYAGEAI_BACKEND_URL", "").strip()
    return env_url.rstrip("/") if env_url else DEFAULT_CLOUD_URL


def _validate_http_url(url: str) -> str | None:
    clean = url.strip().rstrip("/")
    if not clean.startswith(("http://", "https://")):
        return None
    return clean


def check_backend_health(base_url: str, timeout: int = 10) -> tuple[bool, str]:
    """Ping FastAPI backend /health or root endpoint without hanging."""
    clean_url = _validate_http_url(base_url)
    if not clean_url:
        return False, "Invalid backend URL (must start with http:// or https://)."

    last_error = "non-200 response"
    for path in ("/health", "/"):
        try:
            resp = requests.get(f"{clean_url}{path}", timeout=timeout)
            if resp.status_code == 200:
                return True, f"Connected ({clean_url})"
        except requests.RequestException as exc:
            last_error = str(exc)
            continue
    return False, f"Unavailable or sleeping ({last_error})"


def query_travel_backend(
    base_url: str,
    question: str,
    model_provider: str = "groq",
    timeout: int = 120,
) -> tuple[bool, str]:
    """Send a trip planning query to the VoyageAI FastAPI backend."""
    clean_url = _validate_http_url(base_url)
    if not clean_url:
        return False, "Invalid backend URL (must start with http:// or https://)."

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
            "Request timed out. If using Render free tier, click 'Check / Wake Backend' first "
            "or switch to Direct API mode with your Groq/OpenAI key.",
        )
    except requests.ConnectionError:
        return (
            False,
            f"Could not connect to {clean_url}. Verify the backend server is running or use Direct API mode.",
        )
    except requests.RequestException as exc:
        return False, f"Network error: {exc}"

    if resp.status_code != 200:
        detail = resp.text[:350]
        if "model_not_found" in detail or "llama-3.3-70b-versatile" in detail:
            return (
                False,
                "The remote Render backend is still running an outdated deprecated Groq model "
                "(`llama-3.3-70b-versatile`). Redeploy Render from the latest `main` branch, or "
                "switch Execution Mode to 'Direct API (Groq / OpenAI)' below.",
            )
        return False, f"Backend returned HTTP {resp.status_code}: {detail}"

    try:
        data = resp.json()
    except ValueError:
        return False, "Backend returned invalid JSON."

    answer = data.get("answer", "")
    if not answer or not str(answer).strip():
        return False, "Backend returned an empty itinerary."
    return True, str(answer)


def query_direct_llm(
    provider: str,
    api_key: str,
    question: str,
    model_name: str | None = None,
    timeout: int = 60,
) -> tuple[bool, str]:
    """Call Groq or OpenAI Chat Completions directly when running standalone without Render."""
    clean_key = api_key.strip()
    if not clean_key:
        return False, f"Please enter a valid {provider.upper()} API key (or set it in Streamlit secrets)."

    if provider == "groq":
        url = GROQ_CHAT_URL
        model = model_name or "openai/gpt-oss-120b"
    elif provider == "openai":
        url = OPENAI_CHAT_URL
        model = model_name or "gpt-4o-mini"
    else:
        return False, f"Unsupported provider: {provider}"

    try:
        resp = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {clean_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": DIRECT_SYSTEM_PROMPT},
                    {"role": "user", "content": question},
                ],
                "temperature": 0.6,
            },
            timeout=timeout,
        )
    except requests.RequestException as exc:
        return False, f"Direct {provider.upper()} request failed: {exc}"

    if resp.status_code != 200:
        return False, f"{provider.upper()} returned HTTP {resp.status_code}: {resp.text[:350]}"

    try:
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return True, str(content)
    except (ValueError, KeyError, IndexError, TypeError):
        return False, f"Unexpected response format from {provider.upper()}."
