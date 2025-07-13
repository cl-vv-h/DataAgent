from model import app
from langchain.schema import HumanMessage

def run_hedge_fund(ticker: str, start_date: str="2024-03-10", end_date: str="2025-03-10", num_of_news: int = 10):
    final_state = app.invoke(
        {
            "messages": [
                HumanMessage(
                    content="Make a trading decision based on the provided data.",
                )
            ],
            "data": {
                "ticker": ticker,
                "start_date": start_date,
                "end_date": end_date,
                "num_of_news": num_of_news,
            },
            "metadata": {
                "show_reasoning": False
            }
        },
    )
    return final_state["messages"][-1].content