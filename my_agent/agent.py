# pyrefly: ignore [missing-import]
from google.adk.agents.llm_agent import Agent

# pyrefly: ignore [missing-import]
from google.adk.tools import tool

def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}

def get_currency_converter(amount: float, from_currency: str, to_currency: str) -> dict:
    """Returns the currency converted amount from one currency to another."""
    return {"status": "success", "amount": amount, "from_currency": from_currency, "to_currency": to_currency, "converted_amount": amount * 1.1}

currency_agent = Agent(
    model="gemini-2.0-flash",
    name='currency_agent',
    description='A helpful assistant for helping convert currency from one to another',
    instruction='Answer user questions about currency conversion to the best of your knowledge',
)

time_agent = Agent(
    model="gemini-2.0-flash",
    name='time_agent',
    description='A helpful assistant for helping with time of a particular location',
    instruction='Answer user questions about time of a particular location to the best of your knowledge',
)