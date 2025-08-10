from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from model import get_chat_completion
import json

from agents.state import AgentState, show_agent_reasoning, show_workflow_status


##### Portfolio Management Agent #####
def portfolio_management_agent(state: AgentState):
    """Responsible for portfolio management"""
    show_workflow_status("Portfolio Manager")
    show_reasoning = state["metadata"]["show_reasoning"]

    # Get the technical analyst, fundamentals agent, and risk management agent messages
    short_term_message = next(
        msg for msg in state["messages"] if msg.name == "short_term_analysis")
    long_term_message = next(
        msg for msg in state["messages"] if msg.name == "long_term_analysis")
    technical_message = next(
        msg for msg in state["messages"] if msg.name == "technical_analyst_agent")
    fundamentals_message = next(
        msg for msg in state["messages"] if msg.name == "fundamentals_agent")
    sentiment_message = next(
        msg for msg in state["messages"] if msg.name == "sentiment_agent")
    valuation_message = next(
        msg for msg in state["messages"] if msg.name == "valuation_agent")
    risk_message = next(
        msg for msg in state["messages"] if msg.name == "risk_management_agent") if False else "N/A"

    # Create the system message
    system_message = {
        "role": "system",
        "content": """你是一名投资组合经理，负责做出最终的交易决策。
        你的工作是基于团队的分析做出短线及长线的交易决策

        

        在权衡不同方向和时机的信号时：
        1. 估值分析（权重 35%）
           - 公允价值评估的主要驱动因素
           - 判断当前价格是否是良好的买入/卖出时机
       
        2. 基本面分析（权重 30%）
           - 评估业务质量和增长潜力
           - 决定对长期潜力的信心
       
        3. 技术分析（权重 25%）
           - 次要确认信号
           - 帮助确定买入/卖出的时机
       
        4. 市场情绪分析（权重 10%）
           - 最终参考因素
           - 可在风险范围内影响仓位规模
       
        决策流程应为：
        1. 首先检查风险管理约束
        2. 然后评估估值信号
        3. 接着评估基本面信号
        4. 使用技术分析确定时机
        5. 最后考虑市场情绪做最终调整
       
        输出中需包含以下内容：
        - "action": "看涨" | "看跌" | "中立"
        - "confidence": <0 到 1 之间的小数>
        - "agent_signals": <代理信号列表，包含代理名称、信号（看涨 | 看跌 | 中立）及其置信度>
        - "reasoning": <简洁说明你的决策及信号权重的理由>

        """
    }

    # Create the user message
    user_message = {
        "role": "user",
    "content": f"""基于以下团队分析，做出你的交易决策。
        短线分析交易信号：{short_term_message.content}
        长线分析交易信号：{long_term_message.content}
        技术分析交易信号: {technical_message.content}
        基本面分析交易信号: {fundamentals_message.content}
        市场情绪分析交易信号: {sentiment_message.content}
        估值分析交易信号: {valuation_message.content}
        风险管理交易信号: {risk_message}

        输出中仅包含 action、reasoning、confidence、agent_signals，并以 JSON 格式输出。不要包含任何 JSON 代码块标记。

        记住，action 必须是 看涨、看跌 或 中立。
        """
    }

    # Get the completion from OpenRouter
    result = get_chat_completion([system_message, user_message])

    # 如果API调用失败，使用默认的保守决策
    if result is None:
        result = json.dumps({
            "action": "中立",
            "quantity": 0,
            "confidence": 0.7,
            "agent_signals": [
                {
                    "agent_name": "technical_analysis",
                    "signal": "中立",
                    "confidence": 0.0
                },
                {
                    "agent_name": "fundamental_analysis",
                    "signal": "中立",
                    "confidence": 1.0
                },
                {
                    "agent_name": "sentiment_analysis",
                    "signal": "中立",
                    "confidence": 0.6
                },
                {
                    "agent_name": "valuation_analysis",
                    "signal": "中立",
                    "confidence": 0.67
                }
            ],
            "reasoning": "API error occurred. Following risk management signal to hold. This is a conservative decision based on the mixed signals: bullish fundamentals and sentiment vs bearish valuation, with neutral technicals."
        }, ensure_ascii=False)

    # Create the portfolio management message
    message = HumanMessage(
        content=result,
        name="portfolio_management",
    )

    # Print the decision if the flag is set
    if show_reasoning:
        show_agent_reasoning(message.content, "Portfolio Management Agent")

    show_workflow_status("Portfolio Manager", "completed")
    return {
        "messages": state["messages"] + [message],
        "data": state["data"],
    }


def format_decision(action: str, quantity: int, confidence: float, agent_signals: list, reasoning: str) -> dict:
    """Format the trading decision into a standardized output format.
    Think in English but output analysis in Chinese."""

    # 获取各个agent的信号
    fundamental_signal = next(
        (signal for signal in agent_signals if signal["agent_name"] == "fundamental_analysis"), None)
    valuation_signal = next(
        (signal for signal in agent_signals if signal["agent_name"] == "valuation_analysis"), None)
    technical_signal = next(
        (signal for signal in agent_signals if signal["agent_name"] == "technical_analysis"), None)
    sentiment_signal = next(
        (signal for signal in agent_signals if signal["agent_name"] == "sentiment_analysis"), None)
    risk_signal = next(
        (signal for signal in agent_signals if signal["agent_name"] == "risk_management"), None)

    # 转换信号为中文
    def signal_to_chinese(signal):
        if not signal:
            return "无数据"
        if signal["signal"] == "bullish":
            return "看多"
        elif signal["signal"] == "bearish":
            return "看空"
        return "中性"

    # 创建详细分析报告
    detailed_analysis = f"""
====================================
          投资分析报告
====================================

一、策略分析

1. 基本面分析 (权重30%):
   信号: {signal_to_chinese(fundamental_signal)}
   置信度: {fundamental_signal['confidence']*100:.0f}%
   要点: 
   - 盈利能力: {fundamental_signal.get('reasoning', {}).get('profitability_signal', {}).get('details', '无数据')}
   - 增长情况: {fundamental_signal.get('reasoning', {}).get('growth_signal', {}).get('details', '无数据')}
   - 财务健康: {fundamental_signal.get('reasoning', {}).get('financial_health_signal', {}).get('details', '无数据')}
   - 估值水平: {fundamental_signal.get('reasoning', {}).get('price_ratios_signal', {}).get('details', '无数据')}

2. 估值分析 (权重35%):
   信号: {signal_to_chinese(valuation_signal)}
   置信度: {valuation_signal['confidence']*100:.0f}%
   要点:
   - DCF估值: {valuation_signal.get('reasoning', {}).get('dcf_analysis', {}).get('details', '无数据')}
   - 所有者收益法: {valuation_signal.get('reasoning', {}).get('owner_earnings_analysis', {}).get('details', '无数据')}

3. 技术分析 (权重25%):
   信号: {signal_to_chinese(technical_signal)}
   置信度: {technical_signal['confidence']*100:.0f}%
   要点:
   - 趋势跟踪: ADX={technical_signal.get('strategy_signals', {}).get('trend_following', {}).get('metrics', {}).get('adx', '无数据'):.2f}
   - 均值回归: RSI(14)={technical_signal.get('strategy_signals', {}).get('mean_reversion', {}).get('metrics', {}).get('rsi_14', '无数据'):.2f}
   - 动量指标: 
     * 1月动量={technical_signal.get('strategy_signals', {}).get('momentum', {}).get('metrics', {}).get('momentum_1m', '无数据'):.2%}
     * 3月动量={technical_signal.get('strategy_signals', {}).get('momentum', {}).get('metrics', {}).get('momentum_3m', '无数据'):.2%}
     * 6月动量={technical_signal.get('strategy_signals', {}).get('momentum', {}).get('metrics', {}).get('momentum_6m', '无数据'):.2%}
   - 波动性: {technical_signal.get('strategy_signals', {}).get('volatility', {}).get('metrics', {}).get('historical_volatility', '无数据'):.2%}

4. 情绪分析 (权重10%):
   信号: {signal_to_chinese(sentiment_signal)}
   置信度: {sentiment_signal['confidence']*100:.0f}%
   分析: {sentiment_signal.get('reasoning', '无详细分析')}

二、风险评估
风险评分: {risk_signal.get('risk_score', '无数据')}/10
主要指标:
- 波动率: {risk_signal.get('risk_metrics', {}).get('volatility', '无数据')*100:.1f}%
- 最大回撤: {risk_signal.get('risk_metrics', {}).get('max_drawdown', '无数据')*100:.1f}%
- VaR(95%): {risk_signal.get('risk_metrics', {}).get('value_at_risk_95', '无数据')*100:.1f}%
- 市场风险: {risk_signal.get('risk_metrics', {}).get('market_risk_score', '无数据')}/10

三、投资建议
操作建议: {'买入' if action == 'buy' else '卖出' if action == 'sell' else '持有'}
交易数量: {quantity}股
决策置信度: {confidence*100:.0f}%

四、决策依据
{reasoning}

===================================="""

    return {
        "action": action,
        "quantity": quantity,
        "confidence": confidence,
        "agent_signals": agent_signals,
        "分析报告": detailed_analysis
    }
