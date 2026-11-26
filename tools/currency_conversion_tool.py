import os
from typing import List

from dotenv import load_dotenv
from langchain_core.tools import tool

from logger.logging import get_logger
from utils.currency_converter import CurrencyConverter

logger = get_logger(__name__)


class CurrencyConverterTool:
    def __init__(self):
        load_dotenv()
        self.api_key = os.environ.get("EXCHANGE_RATE_API_KEY")
        self.currency_service = CurrencyConverter(self.api_key)
        self.currency_converter_tool_list = self._setup_tools()

    def _setup_tools(self) -> List:
        """Setup all tools for the currency converter tool."""

        @tool
        def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
            """Convert amount from one currency to another."""
            try:
                converted = self.currency_service.convert(amount, from_currency, to_currency)
                return f"{amount} {from_currency.upper()} = {converted} {to_currency.upper()}"
            except Exception as exc:
                logger.warning("Currency conversion failed: %s", exc)
                return (
                    f"Live exchange rate unavailable ({exc}). "
                    f"Provide an approximate conversion between {from_currency} and {to_currency}."
                )

        return [convert_currency]
