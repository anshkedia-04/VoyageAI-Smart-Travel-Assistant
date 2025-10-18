import os
import requests
from langchain_tavily import TavilySearch

class GeoapifyPlaceSearchTool:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.geoapify.com/v2/places"

    def _search(self, place: str, categories: str, limit: int = 10) -> dict:
        """Generic Geoapify place search helper"""
        params = {
            "categories": categories,
            "filter": f"city:{place}",
            "limit": limit,
            "apiKey": self.api_key
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            features = data.get("features", [])
            # Return names of the places
            return [f["properties"]["name"] for f in features]
        else:
            raise Exception(f"Geoapify API error: {response.status_code} - {response.text}")

    def search_attractions(self, place: str) -> dict:
        return self._search(place, categories="tourism.attractions")

    def search_restaurants(self, place: str) -> dict:
        return self._search(place, categories="catering.restaurant")

    def search_activities(self, place: str) -> dict:
        return self._search(place, categories="entertainment")

    def search_transportation(self, place: str) -> dict:
        return self._search(place, categories="transport")

class TavilyPlaceSearchTool:
    def __init__(self):
        pass

    def tavily_search_attractions(self, place: str) -> dict:
        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": f"top attractive places in and around {place}"})
        return result.get("answer") if isinstance(result, dict) and result.get("answer") else result

    def tavily_search_restaurants(self, place: str) -> dict:
        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": f"what are the top 10 restaurants and eateries in and around {place}"})
        return result.get("answer") if isinstance(result, dict) and result.get("answer") else result

    def tavily_search_activity(self, place: str) -> dict:
        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": f"activities in and around {place}"})
        return result.get("answer") if isinstance(result, dict) and result.get("answer") else result

    def tavily_search_transportation(self, place: str) -> dict:
        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": f"What are the different modes of transportations available in {place}"})
        return result.get("answer") if isinstance(result, dict) and result.get("answer") else result
