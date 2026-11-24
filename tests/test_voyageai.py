import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

import main as backend_main
from ui.client import check_backend_health, query_travel_backend
from ui.parser import (
    compose_travel_prompt,
    estimate_trip_budget,
    format_inline_markdown_safe,
    parse_travel_plan,
)


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
        # 4 nights * 5000 = 20000 + food 10000 + act 5000 + transport 10000 = 45000
        self.assertEqual(res["Stay & Lodging"], 20000)
        self.assertEqual(res["Total Estimated"], 45000)
        self.assertEqual(res["Per Person"], 22500)

    def test_fastapi_root_health_and_query_mocked(self) -> None:
        client = TestClient(backend_main.app)
        root_resp = client.get("/")
        self.assertEqual(root_resp.status_code, 200)

        health_resp = client.get("/health")
        self.assertEqual(health_resp.status_code, 200)
        self.assertEqual(health_resp.json()["status"], "ok")

        fake_msg = MagicMock()
        fake_msg.content = "Day 1: Arrival\n- Explore downtown"
        fake_graph = MagicMock()
        fake_graph.invoke.return_value = {"messages": [fake_msg]}

        with patch.object(backend_main, "_get_compiled_graph", return_value=fake_graph):
            q_resp = client.post("/query", json={"question": "Plan 2 days in Goa"})
            self.assertEqual(q_resp.status_code, 200)
            self.assertIn("Day 1: Arrival", q_resp.json()["answer"])

    def test_client_handles_timeout_and_success(self) -> None:
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


if __name__ == "__main__":
    unittest.main()
