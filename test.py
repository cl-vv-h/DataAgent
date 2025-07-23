from workflow import app
from datetime import datetime, timedelta
import argparse
from langchain_core.messages import HumanMessage
from langchain.prompts import PromptTemplate

from model import doubao_llm
from workflow import app

ticker = "sh600310"
initial_state = {
    "messages": [
        HumanMessage(content=f"Please analyze stock with ticker {ticker}")
    ],
    "data": {
        "ticker": ticker,
        "start_date": "2024-03-01",  # Will be set later
        "end_date": "2025-07-20",    # Will be set later
    },
    "metadata": {
        "show_reasoning": True
    }
}

print(f"Starting analysis for ticker: {ticker}")
# result = app.invoke(initial_state)

from agents.market_data import market_data_agent
res = market_data_agent(initial_state)
