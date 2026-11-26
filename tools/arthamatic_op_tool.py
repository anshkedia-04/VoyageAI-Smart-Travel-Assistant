import os

from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


@tool
def currency_converter(from_curr: str, to_curr: str, value: float) -> float:
    """Convert currency via AlphaVantage when ALPHAVANTAGE_API_KEY is configured."""
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    if not api_key:
        raise ValueError("ALPHAVANTAGE_API_KEY is not configured.")

    from langchain_community.utilities.alpha_vantage import AlphaVantageAPIWrapper

    os.environ["ALPHAVANTAGE_API_KEY"] = api_key
    alpha_vantage = AlphaVantageAPIWrapper()
    response = alpha_vantage._get_exchange_rate(from_curr, to_curr)
    exchange_rate = response["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
    return value * float(exchange_rate)
