import requests

from exception.exceptionhandling import ConfigurationError, ExternalServiceError


class CurrencyConverter:
    def __init__(self, api_key: str | None, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout
        self.base_url = (
            f"https://v6.exchangerate-api.com/v6/{api_key}/latest" if api_key else ""
        )

    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Convert an amount between ISO currency codes."""
        if not self.api_key:
            raise ConfigurationError("EXCHANGE_RATE_API_KEY is not configured.")

        src = from_currency.strip().upper()
        dst = to_currency.strip().upper()
        url = f"{self.base_url}/{src}"

        try:
            response = requests.get(url, timeout=self.timeout)
        except requests.RequestException as exc:
            raise ExternalServiceError(f"Exchange rate request failed: {exc}") from exc

        if response.status_code != 200:
            raise ExternalServiceError(
                f"Exchange rate API returned HTTP {response.status_code}: {response.text[:200]}"
            )

        rates = response.json().get("conversion_rates", {})
        if dst not in rates:
            raise ValueError(f"{dst} not found in exchange rates.")
        return round(float(amount) * float(rates[dst]), 2)
