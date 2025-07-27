from langchain_core.messages import HumanMessage

from agents.state import AgentState, show_agent_reasoning, show_workflow_status

import json


def fundamentals_agent(state: AgentState):
    show_workflow_status("Fundamentals Analyst")
    show_reasoning = state["metadata"]["show_reasoning"]
    data = state["data"]
    metrics = data["financial_metrics"][0]

    # Initialize signals list for different fundamental aspects
    signals = []
    reasoning = {}

    # 1. Profitability Analysis
    return_on_equity = metrics.get("return_on_equity", 0)
    net_margin = metrics.get("net_margin", 0)
    operating_margin = metrics.get("operating_margin", 0)

    thresholds = [
        (return_on_equity, 0.15),  # Strong ROE above 15%
        (net_margin, 0.20),  # Healthy profit margins
        (operating_margin, 0.15)  # Strong operating efficiency
    ]
    profitability_score = sum(
        metric is not None and metric > threshold
        for metric, threshold in thresholds
    )

    signals.append('看涨' if profitability_score >=
                   2 else '看跌' if profitability_score == 0 else '中立')
    reasoning["利润层面信号"] = {
        "结论": signals[0],
        "论据": (
            f"股本回报率: {metrics.get('return_on_equity', 0):.2%}，股本回报率以15%作为参考阈值" if metrics.get(
                "return_on_equity") is not None else "股本回报率: N/A"
        ) + ", " + (
            f"税后利润率: {metrics.get('net_margin', 0):.2%}，税后利润率以20%作为参考阈值" if metrics.get(
                "net_margin") is not None else "税后利润率: N/A"
        ) + ", " + (
            f"营业利润率: {metrics.get('operating_margin', 0):.2%}，营业利润率以15%作为参考阈值" if metrics.get(
                "operating_margin") is not None else "营业利润率: N/A"
        )
    }

    # 2. Growth Analysis
    revenue_growth = metrics.get("revenue_growth", 0)
    earnings_growth = metrics.get("earnings_growth", 0)
    book_value_growth = metrics.get("book_value_growth", 0)

    thresholds = [
        (revenue_growth, 0.10),  # 10% revenue growth
        (earnings_growth, 0.10),  # 10% earnings growth
        (book_value_growth, 0.10)  # 10% book value growth
    ]
    growth_score = sum(
        metric is not None and metric > threshold
        for metric, threshold in thresholds
    )

    signals.append('看涨' if growth_score >=
                   2 else '看跌' if growth_score == 0 else '中立')
    reasoning["增长层面信号"] = {
        "结论": signals[1],
        "论据": (
            f"收入增长: {metrics.get('revenue_growth', 0):.2%}，收入增长以10%作为参考阈值" if metrics.get(
                "revenue_growth") is not None else "收入增长: N/A"
        ) + ", " + (
            f"盈利增长: {metrics.get('earnings_growth', 0):.2%}，收入增长以10%作为参考阈值" if metrics.get(
                "earnings_growth") is not None else "营收增长: N/A"
        )
    }

    # 3. Financial Health
    current_ratio = metrics.get("current_ratio", 0)
    debt_to_equity = metrics.get("debt_to_equity", 0)
    free_cash_flow_per_share = metrics.get("free_cash_flow_per_share", 0)
    earnings_per_share = metrics.get("earnings_per_share", 0)

    health_score = 0
    if current_ratio and current_ratio > 1.5:  # Strong liquidity
        health_score += 1
    if debt_to_equity and debt_to_equity < 0.5:  # Conservative debt levels
        health_score += 1
    if (free_cash_flow_per_share and earnings_per_share and
            free_cash_flow_per_share > earnings_per_share * 0.8):  # Strong FCF conversion
        health_score += 1

    signals.append('看涨' if health_score >=
                   2 else '看跌' if health_score == 0 else '中立')
    reasoning["财政层面信号"] = {
        "结论": signals[2],
        "论据": (
            f"流动比率: {metrics.get('current_ratio', 0):.2f}，以1.5为参考阈值" if metrics.get(
                "current_ratio") is not None else "流动比率: N/A"
        ) + ", " + (
            f"债务股本比: {metrics.get('debt_to_equity', 0):.2f}，以0.5为参考阈值" if metrics.get(
                "debt_to_equity") is not None else "债务股本比: N/A"
        )
    }

    # 4. Price to X ratios
    pe_ratio = metrics.get("pe_ratio", 0)
    price_to_book = metrics.get("price_to_book", 0)
    price_to_sales = metrics.get("price_to_sales", 0)

    thresholds = [
        (pe_ratio, 25),  # Reasonable P/E ratio
        (price_to_book, 3),  # Reasonable P/B ratio
        (price_to_sales, 5)  # Reasonable P/S ratio
    ]
    price_ratio_score = sum(
        metric is not None and metric < threshold
        for metric, threshold in thresholds
    )

    signals.append('看涨' if price_ratio_score >=
                   2 else '看跌' if price_ratio_score == 0 else '中立')
    reasoning["price_ratios_signal"] = {
        "结论": signals[3],
        "论据": (
            f"P/E: {pe_ratio:.2f}，市盈率以25%为参考阈值" if pe_ratio else "P/E: N/A"
        ) + ", " + (
            f"P/B: {price_to_book:.2f}，市净率以3%为参考阈值" if price_to_book else "P/B: N/A"
        ) + ", " + (
            f"P/S: {price_to_sales:.2f}，市销率以5%为参考阈值" if price_to_sales else "P/S: N/A"
        )
    }

    # Determine overall signal
    bullish_signals = signals.count('看涨')
    bearish_signals = signals.count('看跌')

    if bullish_signals > bearish_signals:
        overall_signal = '看涨'
    elif bearish_signals > bullish_signals:
        overall_signal = '看跌'
    else:
        overall_signal = '中立'

    # Calculate confidence level
    total_signals = len(signals)
    confidence = max(bullish_signals, bearish_signals) / total_signals

    message_content = {
        "观点": overall_signal,
        "置信度": f"{round(confidence * 100)}%",
        "论据": reasoning
    }

    # Create the fundamental analysis message
    message = HumanMessage(
        content=json.dumps(message_content),
        name="fundamentals_agent",
    )

    # Print the reasoning if the flag is set
    if show_reasoning:
        show_agent_reasoning(message_content, "Fundamental Analysis Agent")

    show_workflow_status("Fundamentals Analyst", "completed")
    return {
        "messages": [message],
        "data": {
            **data,
            "fundamental_analysis": message_content
        }
    }
