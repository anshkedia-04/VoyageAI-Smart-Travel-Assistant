from typing import Any

import requests

from exception.exceptionhandling import ExternalServiceError
from logger.logging import get_logger

logger = get_logger(__name__)


class WeatherForecastTool:
    def __init__(self, api_key: str | None, timeout: int = 10):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.timeout = timeout

    def get_current_weather(self, place: str) -> dict[str, Any]:
        """Get current metric weather conditions for a city."""
        if not self.api_key:
            return {}
        try:
            response = requests.get(
                f"{self.base_url}/weather",
                params={"q": place, "appid": self.api_key, "units": "metric"},
                timeout=self.timeout,
            )
            if response.status_code == 200:
                return response.json()
            logger.warning("OpenWeather current status=%s for %s", response.status_code, place)
            return {}
        except requests.RequestException as exc:
            raise ExternalServiceError(f"Weather API error for {place}: {exc}") from exc

    def get_forecast_weather(self, place: str) -> dict[str, Any]:
        """Get short-range metric weather forecast for a city."""
        if not self.api_key:
            return {}
        try:
            response = requests.get(
                f"{self.base_url}/forecast",
                params={"q": place, "appid": self.api_key, "cnt": 10, "units": "metric"},
                timeout=self.timeout,
            )
            if response.status_code == 200:
                return response.json()
            logger.warning("OpenWeather forecast status=%s for %s", response.status_code, place)
            return {}
        except requests.RequestException as exc:
            raise ExternalServiceError(f"Forecast API error for {place}: {exc}") from exc
