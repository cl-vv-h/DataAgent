from workflow import app
from datetime import datetime, timedelta
import argparse
from langchain_core.messages import HumanMessage
from langchain.prompts import PromptTemplate

from model import doubao_llm
from workflow import app


market = "sh"
ticker = "600310"
initial_state = {
    # "messages": [
    #     HumanMessage(content=f"请为以下股票提供详细分析，该股票代码为： {market + ticker}")
    # ],
    "data": {
        "market": market,
        "ticker": ticker,
        "start_date": "2024-03-01",  # Will be set later
        "end_date": "2025-08-08",    # Will be set later
    },
    "metadata": {
        "show_reasoning": True
    }
}

print(f"Starting analysis for ticker: {ticker}")
result = app.invoke(initial_state)

i = 0
for msg in result["messages"]:
    print(msg.content)
    with open(f"res{i}.json", 'w', encoding='utf-8') as f:
        import json
        data = json.dumps(msg.content)
        f.write(data)
        f.close()
    i += 1
