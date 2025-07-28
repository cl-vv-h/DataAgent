from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from model import get_chat_completion
import json

from agents.state import AgentState, show_agent_reasoning, show_workflow_status

def long_term_agent(state: AgentState):
    show_workflow_status("Short Term Analysis")
    show_reasoning = state["metadata"]["show_reasoning"]

    data = AgentState["data"]
    messages = AgentState["messages"]
    # Create the system message
    system_message = {
        "role": "system",
        "content": """你是一个专业的量化交易分析智能体，请根据下方提供的股票技术指标摘要，结合短线交易原则，从以下几个方面进行分析：

            1. 当前市场的短线走势是上涨、震荡还是下跌？
            2. 是否存在超买或超卖信号？是否存在回调或反弹的可能？
            3. 当前价格在布林带中的位置是否存在突破、回调风险？
            4. 成交量变化是否支持价格的当前趋势？
            5. 综合判断：是否适合在当前时点买入、卖出或观望？

            请以专业、简洁、明确的语言输出分析结论，提供以下输出:
            - "action": "看涨" | "看跌" | "中立",
            - "confidence": <0-1之间的置信度>
            - "reasoning": <给出该结论的详细解释>
            """
    }

    # Create the user message
    user_message = {
        "role": "user",
        "content": f"""以下是技术指标摘要：
        {data["long_term_summary_text"]}
        """
    }

    # Get the completion from OpenRouter
    result = get_chat_completion([system_message, user_message])

    # 如果API调用失败，使用默认的保守决策
    if result is None:
        result = json.dumps({
            "action": "hold",
            "confidence": 0.5,
            "reasoning": "短线分析失败，无法提供相应建议，因此保持现状"
        })

    # Create the portfolio management message
    message = HumanMessage(
        content=result,
        name="long_term_analysis",
    )

    # Print the decision if the flag is set
    if show_reasoning:
        show_agent_reasoning(message.content, "Short Term Agent")

    show_workflow_status("Short Term Agent", "completed")
    return {
        "messages": state["messages"] + [message],
        "data": state["data"],
    }
