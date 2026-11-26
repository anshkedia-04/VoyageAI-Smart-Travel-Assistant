import os
import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from exception.exceptionhandling import ConfigurationError
import main as backend_main
from tools.place_search_tool import PlaceSearchTool
from ui.client import (
    DEFAULT_CLOUD_URL,
    check_backend_health,
    get_default_backend_url,
    query_direct_llm,
    query_travel_backend,
)
from ui.parser import (
    compose_travel_prompt,
    estimate_trip_budget,
    format_inline_markdown_safe,
    parse_travel_plan,
)
from utils.config_loader import load_config
from utils.currency_converter import CurrencyConverter
from utils.weather_info import WeatherForecastTool


class VoyageAITests(unittest.TestCase):
    def test_parse_travel_plan_flexible_markdown(self) -> None:
        sample = """Welcome to your Kyoto itinerary!

### Day 1: Temples & Gion
- Visit Kiyomizu-dera at sunrise
- Walk Hanamikoji Street

**Day 2 - Arashiyama Bamboo Grove**
1. Early boat ride and **Tenryu-ji** visit

Hotels:
- Hotel Kanra Kyoto: $220 / night

Weather:
- Mild 19°C with clear skies
"""
        parsed = parse_travel_plan(sample)
        self.assertEqual(len(parsed.intro_lines), 1)
        self.assertEqual(len(parsed.days), 2)
        self.assertEqual(parsed.days[0].day_number, "01")
        self.assertEqual(parsed.days[0].title, "Temples & Gion")
        self.assertEqual(len(parsed.days[0].items), 2)
        self.assertEqual(parsed.days[1].title, "Arashiyama Bamboo Grove")
        self.assertEqual(len(parsed.sections), 2)
        self.assertEqual(parsed.sections[0].heading, "Hotels")

    def test_html_escaping_prevents_injection(self) -> None:
        rendered = format_inline_markdown_safe("<script>alert(1)</script> **Safe**")
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertIn("<strong>Safe</strong>", rendered)

    def test_compose_travel_prompt(self) -> None:
        prompt = compose_travel_prompt(
            destination="Goa",
            days=4,
            travelers=2,
            budget_tier="Mid-Range Comfort",
            currency="INR",
            interests=["Beaches & Relaxation", "Food & Local Cafés"],
            include_offbeat=True,
            custom_notes="Prefer South Goa",
        )
        self.assertIn("4-day trip to Goa", prompt)
        self.assertIn("2 travelers", prompt)
        self.assertIn("off-beat", prompt.lower())
        self.assertIn("Prefer South Goa", prompt)

    def test_estimate_trip_budget(self) -> None:
        res = estimate_trip_budget(
            days=5,
            travelers=2,
            stay_per_night=5000,
            food_per_person_day=1000,
            activities_per_person_day=500,
            transport_total=10000,
        )
        self.assertEqual(res["Stay & Lodging"], 20000)
        self.assertEqual(res["Total Estimated"], 45000)
        self.assertEqual(res["Per Person"], 22500)

    def test_config_loader_and_missing_file(self) -> None:
        cfg = load_config("config/config.yaml")
        self.assertIn("llm", cfg)
        self.assertIn("groq", cfg["llm"])
        with self.assertRaises(ConfigurationError):
            load_config("config/does_not_exist.yaml")

    def test_weather_tool_uses_metric_and_guards_missing_key(self) -> None:
        self.assertEqual(WeatherForecastTool(None).get_current_weather("Goa"), {})

        with patch("utils.weather_info.requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: {"main": {"temp": 29.5}, "weather": [{"description": "clear sky"}]},
            )
            data = WeatherForecastTool("fake-key").get_current_weather("Goa")
            self.assertEqual(data["main"]["temp"], 29.5)
            _, kwargs = mock_get.call_args
            self.assertEqual(kwargs["params"]["units"], "metric")
            self.assertEqual(kwargs["timeout"], 10)

    def test_currency_converter_url_and_missing_key(self) -> None:
        with self.assertRaises(ConfigurationError):
            CurrencyConverter(None).convert(100, "USD", "INR")

        with patch("utils.currency_converter.requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: {"conversion_rates": {"INR": 84.5}},
            )
            converted = CurrencyConverter("fx-key").convert(10, "usd", "inr")
            self.assertEqual(converted, 845.0)
            called_url = mock_get.call_args[0][0]
            self.assertTrue(called_url.endswith("/latest/USD"))

    def test_place_search_tool_fallback_and_graceful_degradation(self) -> None:
        tool_bundle = PlaceSearchTool()
        search_attractions = tool_bundle.place_search_tool_list[0]

        with (
            patch.object(tool_bundle.geoapify_search, "search_attractions", return_value=[]),
            patch.object(tool_bundle.tavily_search, "tavily_search_attractions", return_value="Fort Aguada"),
        ):
            res = search_attractions.invoke({"place": "Goa"})
            self.assertIn("Fort Aguada", res)

        with (
            patch.object(tool_bundle.geoapify_search, "search_attractions", side_effect=ConfigurationError("no key")),
            patch.object(tool_bundle.tavily_search, "tavily_search_attractions", side_effect=ConfigurationError("no key")),
        ):
            res = search_attractions.invoke({"place": "Goa"})
            self.assertIn("Live place search is unavailable", res)

    def test_fastapi_root_health_and_query_states(self) -> None:
        client = TestClient(backend_main.app)
        root_resp = client.get("/")
        self.assertEqual(root_resp.status_code, 200)
        self.assertIn("X-Request-ID", root_resp.headers)

        health_resp = client.get("/health")
        self.assertEqual(health_resp.status_code, 200)
        body = health_resp.json()
        self.assertEqual(body["status"], "ok")
        self.assertIn("tools_configured", body)

        fake_msg = MagicMock()
        fake_msg.content = "Day 1: Arrival\n- Explore downtown"
        fake_graph = MagicMock()
        fake_graph.invoke.return_value = {"messages": [fake_msg]}

        with patch.object(backend_main, "_get_compiled_graph", return_value=fake_graph):
            q_resp = client.post("/query", json={"question": "Plan 2 days in Goa"})
            self.assertEqual(q_resp.status_code, 200)
            self.assertIn("Day 1: Arrival", q_resp.json()["answer"])

        with patch.object(backend_main, "_get_compiled_graph", side_effect=ConfigurationError("GROQ_API_KEY missing")):
            err_resp = client.post("/query", json={"question": "Plan 2 days in Goa"})
            self.assertEqual(err_resp.status_code, 503)
            self.assertIn("GROQ_API_KEY missing", err_resp.json()["error"])

    def test_client_helpers_and_env_override(self) -> None:
        with patch.dict(os.environ, {"VOYAGEAI_BACKEND_URL": "http://backend:8000/"}):
            self.assertEqual(get_default_backend_url(), "http://backend:8000")
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_default_backend_url(), DEFAULT_CLOUD_URL)

        ok, msg = check_backend_health("ftp://invalid")
        self.assertFalse(ok)
        self.assertIn("Invalid backend URL", msg)

        with patch("ui.client.requests.get") as mock_get:
            mock_get.return_value = MagicMock(status_code=200)
            ok, _ = check_backend_health("http://localhost:8000", timeout=2)
            self.assertTrue(ok)

        with patch("ui.client.requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: {"answer": "Day 1: Beach Walk\n- Sunset point"},
            )
            ok, ans = query_travel_backend("http://localhost:8000", "Goa 2 days")
            self.assertTrue(ok)
            self.assertIn("Beach Walk", ans)

        with patch("ui.client.requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=500,
                text="model_not_found llama-3.3-70b-versatile",
            )
            ok, msg = query_travel_backend("http://localhost:8000", "Goa 2 days")
            self.assertFalse(ok)
            self.assertIn("Direct API", msg)

    def test_direct_llm_mode_validation_and_success(self) -> None:
        ok, msg = query_direct_llm("groq", "", "Plan Goa")
        self.assertFalse(ok)
        self.assertIn("API key", msg)

        with patch("ui.client.requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: {"choices": [{"message": {"content": "Day 1: Old Goa"}}]},
            )
            ok, ans = query_direct_llm("groq", "test-key", "Plan Goa")
            self.assertTrue(ok)
            self.assertIn("Old Goa", ans)


if __name__ == "__main__":
    unittest.main()
