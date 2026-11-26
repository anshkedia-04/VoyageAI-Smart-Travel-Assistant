import os
from typing import Callable, List

from dotenv import load_dotenv
from langchain_core.tools import tool

from logger.logging import get_logger
from utils.place_info_search import GeoapifyPlaceSearchTool, TavilyPlaceSearchTool

logger = get_logger(__name__)


class PlaceSearchTool:
    def __init__(self):
        load_dotenv()
        self.geoapify_api_key = os.environ.get("GEOAPIFY_API_KEY")
        self.geoapify_search = GeoapifyPlaceSearchTool(self.geoapify_api_key)
        self.tavily_search = TavilyPlaceSearchTool()
        self.place_search_tool_list = self._setup_tools()

    def _query_with_fallback(
        self,
        label: str,
        place: str,
        primary_fn: Callable[[str], list[str]],
        fallback_fn: Callable[[str], object],
    ) -> str:
        """Try Geoapify first and fall back cleanly to Tavily without crashing the agent."""
        try:
            primary_res = primary_fn(place)
            if primary_res:
                return f"Following are the {label} of {place} as suggested by Geoapify: {primary_res}"
        except Exception as exc:
            logger.info("Geoapify %s lookup skipped for %s: %s", label, place, exc)

        try:
            fallback_res = fallback_fn(place)
            return f"Following are the {label} of {place}: {fallback_res}"
        except Exception as exc:
            logger.warning("Tavily %s fallback unavailable for %s: %s", label, place, exc)
            return (
                f"Live place search is unavailable for {label} in {place} ({exc}). "
                "Provide well-known curated recommendations based on destination knowledge."
            )

    def _setup_tools(self) -> List:
        """Setup all tools for the place search tool."""

        @tool
        def search_attractions(place: str) -> str:
            """Search attractions of a place."""
            return self._query_with_fallback(
                "attractions",
                place,
                self.geoapify_search.search_attractions,
                self.tavily_search.tavily_search_attractions,
            )

        @tool
        def search_restaurants(place: str) -> str:
            """Search restaurants of a place."""
            return self._query_with_fallback(
                "restaurants",
                place,
                self.geoapify_search.search_restaurants,
                self.tavily_search.tavily_search_restaurants,
            )

        @tool
        def search_activities(place: str) -> str:
            """Search activities of a place."""
            return self._query_with_fallback(
                "activities",
                place,
                self.geoapify_search.search_activities,
                self.tavily_search.tavily_search_activity,
            )

        @tool
        def search_transportation(place: str) -> str:
            """Search transportation of a place."""
            return self._query_with_fallback(
                "modes of transportation",
                place,
                self.geoapify_search.search_transportation,
                self.tavily_search.tavily_search_transportation,
            )

        return [search_attractions, search_restaurants, search_activities, search_transportation]
