from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from model import get_chat_completion
import json

from agents.state import AgentState, show_agent_reasoning, show_workflow_status

def long_term_agent(state: AgentState):
    show_workflow_status("Long Term Analysis")
    show_reasoning = state["metadata"]["show_reasoning"]

    data = state["data"]
    messages = state["messages"]
    # Create the system message
    system_message = {
        "role": "system",
        "content": """你是一个经验丰富的长线股票分析师，擅长结合财务、估值、技术趋势以及公司战略进行整体判断。

            ## 提供给你的信息包括：
            - 近三年经营现金流（Operating Cash Flow）
            - 近三年每季度净利润增长率（以百分比表示）
            - 近三年企业价值(EV)
            - 近三年营业利润（Income）
            - ma50、ma200（长期趋势均线）
            - 本周成交额，以及成交额相较于历史均值的“放量”或“缩量”情况
            - 公司战略概要（由提取工具提供的战略方向或关键战略要点）

            ### 指导分析逻辑建议如下：
            1. 如果经营现金流持续稳健并增长，视为基本面强劲；
            2. 若净利润增长率呈现稳定上升趋势，支持长期成长；
            3. EV/营业利润若处于行业较低区间，意味着估值有吸引力；
            4. 股价长期站稳 ma50 与 ma200 上方，并伴随成交额放大，趋势更可信；
            5. 如果公司战略清晰、对行业未来定位坚定，应增强投资信心；
            6. 若多项指标存在矛盾（如现金流弱但战略强），应降低置信度。

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
        {data["long_term_data"]}
        """
    }

    # Get the completion from OpenRouter
    result = get_chat_completion([system_message, user_message])

    # 如果API调用失败，使用默认的保守决策
    if result is None:
        result = json.dumps({
            "action": "中立",
            "confidence": 0.5,
            "reasoning": "长分析失败，无法提供相应建议，因此保持现状"
        }, ensure_ascii=False)

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
