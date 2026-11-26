import os
from typing import Any

import requests

from exception.exceptionhandling import ConfigurationError, ExternalServiceError


class GeoapifyPlaceSearchTool:
    def __init__(self, api_key: str | None, timeout: int = 10):
        self.api_key = api_key
        self.base_url = "https://api.geoapify.com/v2/places"
        self.timeout = timeout

    def _search(self, place: str, categories: str, limit: int = 10) -> list[str]:
        """Query Geoapify Places API with timeout and structured error handling."""
        if not self.api_key:
            raise ConfigurationError("GEOAPIFY_API_KEY is not configured.")
        try:
            response = requests.get(
                self.base_url,
                params={
                    "categories": categories,
                    "filter": f"city:{place}",
                    "limit": limit,
                    "apiKey": self.api_key,
                },
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise ExternalServiceError(f"Geoapify request failed: {exc}") from exc

        if response.status_code != 200:
            raise ExternalServiceError(
                f"Geoapify API error {response.status_code}: {response.text[:200]}"
            )

        features = response.json().get("features", [])
        return [
            f["properties"]["name"]
            for f in features
            if isinstance(f, dict) and f.get("properties", {}).get("name")
        ]

    def search_attractions(self, place: str) -> list[str]:
        return self._search(place, categories="tourism.attractions")

    def search_restaurants(self, place: str) -> list[str]:
        return self._search(place, categories="catering.restaurant")

    def search_activities(self, place: str) -> list[str]:
        return self._search(place, categories="entertainment")

    def search_transportation(self, place: str) -> list[str]:
        return self._search(place, categories="transport")


class TavilyPlaceSearchTool:
    def _run_search(self, query: str) -> Any:
        if not os.environ.get("TAVILY_API_KEY"):
            raise ConfigurationError("TAVILY_API_KEY is not configured.")
        from langchain_tavily import TavilySearch

        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": query})
        if isinstance(result, dict) and result.get("answer"):
            return result["answer"]
        return result

    def tavily_search_attractions(self, place: str) -> Any:
        return self._run_search(f"top attractive places in and around {place}")

    def tavily_search_restaurants(self, place: str) -> Any:
        return self._run_search(f"what are the top 10 restaurants and eateries in and around {place}")

    def tavily_search_activity(self, place: str) -> Any:
        return self._run_search(f"activities in and around {place}")

    def tavily_search_transportation(self, place: str) -> Any:
        return self._run_search(f"What are the different modes of transportations available in {place}")
