from langchain_core.messages import HumanMessage
from agents.state import AgentState, show_agent_reasoning, show_workflow_status
from utils.api import get_financial_metrics, get_financial_statements, get_market_data, get_price_history, get_short_term_data
from utils.logging_config import setup_logger

from datetime import datetime, timedelta
import pandas as pd

import ta

# 设置日志记录
logger = setup_logger('market_data_agent')


def market_data_agent(state: AgentState):
    """Responsible for gathering and preprocessing market data"""
    show_workflow_status("Market Data Agent")
    show_reasoning = state["metadata"]["show_reasoning"]

    messages = state["messages"]
    data = state["data"]

    # Set default dates
    current_date = datetime.now()
    yesterday = current_date - timedelta(days=1)
    end_date = data["end_date"] or yesterday.strftime('%Y-%m-%d')

    # Ensure end_date is not in the future
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    if end_date_obj > yesterday:
        end_date = yesterday.strftime('%Y-%m-%d')
        end_date_obj = yesterday

    if not data["start_date"]:
        # Calculate 1 year before end_date
        start_date = end_date_obj - timedelta(days=365)  # 默认获取一年的数据
        start_date = start_date.strftime('%Y-%m-%d')
    else:
        start_date = data["start_date"]

    # Get all required data
    market = data["market"]
    ticker = data["ticker"]

    # 获取价格数据并验证
    prices_df = get_price_history(ticker, start_date, end_date)
    if prices_df is None or prices_df.empty:
        logger.warning(f"警告：无法获取{ticker}的价格数据，将使用空数据继续")
        prices_df = pd.DataFrame(
            columns=['close', 'open', 'high', 'low', 'volume'])

    # 获取财务指标
    try:
        financial_metrics = get_financial_metrics(ticker)
    except Exception as e:
        logger.error(f"获取财务指标失败: {str(e)}")
        financial_metrics = {}

    # 获取财务报表
    try:
        financial_line_items = get_financial_statements(ticker)
    except Exception as e:
        logger.error(f"获取财务报表失败: {str(e)}")
        financial_line_items = {}

    # 获取市场数据
    try:
        market_data = get_market_data(ticker)
    except Exception as e:
        logger.error(f"获取市场数据失败: {str(e)}")
        market_data = {"market_cap": 0}

    # 确保数据格式正确
    if not isinstance(prices_df, pd.DataFrame):
        prices_df = pd.DataFrame(
            columns=['close', 'open', 'high', 'low', 'volume'])

    # 转换价格数据为字典格式
    prices_dict = prices_df.to_dict('records')

    short_term_data, short_term_summary, short_term_summary_text = get_short_term_data(market, ticker)

    message = HumanMessage(
        content=short_term_summary_text,
        name="short_term_summary",
    )
    messages.append(message)

    res = {
        "messages": [message],
        "data": {
            **data,
            "prices": prices_dict,
            "start_date": start_date,
            "end_date": end_date,
            "financial_metrics": financial_metrics,
            "financial_line_items": financial_line_items,
            "market_cap": market_data.get("market_cap", 0),
            "market_data": market_data,
            "short_term_data": short_term_data,
            "short_term_summary": short_term_summary,
            "short_term_summary_text": short_term_summary_text
        }
    }

    return res


if __name__=="__main__":
    ticker = "002518"
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
    print(market_data_agent(initial_state))