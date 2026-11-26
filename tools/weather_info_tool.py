import os
from typing import List

from dotenv import load_dotenv
from langchain_core.tools import tool

from logger.logging import get_logger
from utils.weather_info import WeatherForecastTool

logger = get_logger(__name__)


class WeatherInfoTool:
    def __init__(self):
        load_dotenv()
        self.api_key = os.environ.get("OPENWEATHERMAP_API_KEY")
        self.weather_service = WeatherForecastTool(self.api_key)
        self.weather_tool_list = self._setup_tools()

    def _setup_tools(self) -> List:
        """Setup all tools for the weather forecast tool."""

        @tool
        def get_current_weather(city: str) -> str:
            """Get current weather for a city."""
            try:
                weather_data = self.weather_service.get_current_weather(city)
                if weather_data:
                    temp = weather_data.get("main", {}).get("temp", "N/A")
                    desc = weather_data.get("weather", [{}])[0].get("description", "N/A")
                    return f"Current weather in {city}: {temp}°C, {desc}"
            except Exception as exc:
                logger.warning("Weather lookup failed for %s: %s", city, exc)
            return f"Live weather unavailable for {city}; share typical seasonal climate guidance."

        @tool
        def get_weather_forecast(city: str) -> str:
            """Get weather forecast for a city."""
            try:
                forecast_data = self.weather_service.get_forecast_weather(city)
                if forecast_data and "list" in forecast_data:
                    forecast_summary = []
                    for item in forecast_data["list"]:
                        date = item["dt_txt"].split(" ")[0]
                        temp = item["main"]["temp"]
                        desc = item["weather"][0]["description"]
                        forecast_summary.append(f"{date}: {temp}°C, {desc}")
                    return f"Weather forecast for {city}:\n" + "\n".join(forecast_summary)
            except Exception as exc:
                logger.warning("Forecast lookup failed for %s: %s", city, exc)
            return f"Live forecast unavailable for {city}; share typical seasonal climate guidance."

        return [get_current_weather, get_weather_forecast]
