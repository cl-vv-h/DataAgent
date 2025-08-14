from langgraph.graph import START, END, StateGraph
from agents.state import AgentState
from agents.market_data import market_data_agent
from agents.technicals import technical_analyst_agent
from agents.fundamentals import fundamentals_agent
from agents.sentiment import sentiment_agent
from agents.valuation import valuation_agent
from agents.researcher_bull import researcher_bull_agent
from agents.researcher_bear import researcher_bear_agent
from agents.debate_room import debate_room_agent
from agents.risk_manager import risk_management_agent
from agents.portfolio_manager import portfolio_management_agent
from agents.short_term import short_term_agent
from agents.long_term import long_term_agent

# Define the new workflow
workflow = StateGraph(AgentState)

# # Add nodes
workflow.add_node("market_data_agent", market_data_agent)
workflow.add_node("short_term_agent", short_term_agent)
workflow.add_node("long_term_agent", long_term_agent)
workflow.add_node("technical_analyst_agent", technical_analyst_agent)
workflow.add_node("fundamentals_agent", fundamentals_agent)
workflow.add_node("sentiment_agent", sentiment_agent)
workflow.add_node("valuation_agent", valuation_agent)
workflow.add_node("researcher_bull_agent", researcher_bull_agent)
workflow.add_node("researcher_bear_agent", researcher_bear_agent)
workflow.add_node("debate_room_agent", debate_room_agent)
workflow.add_node("risk_management_agent", risk_management_agent)
workflow.add_node("portfolio_management_agent", portfolio_management_agent)

# Define the workflow
workflow.set_entry_point("market_data_agent")

# Market Data to Analysts
workflow.add_edge("market_data_agent", "short_term_agent")
workflow.add_edge("market_data_agent", "long_term_agent")
workflow.add_edge("market_data_agent", "technical_analyst_agent")
workflow.add_edge("market_data_agent", "fundamentals_agent")
workflow.add_edge("market_data_agent", "sentiment_agent")
workflow.add_edge("market_data_agent", "valuation_agent")

# # Analysts to Researchers
# workflow.add_edge("technical_analyst_agent", "researcher_bull_agent")
# workflow.add_edge("fundamentals_agent", "researcher_bull_agent")
# workflow.add_edge("sentiment_agent", "researcher_bull_agent")
# workflow.add_edge("valuation_agent", "researcher_bull_agent")

# workflow.add_edge("technical_analyst_agent", "researcher_bear_agent")
# workflow.add_edge("fundamentals_agent", "researcher_bear_agent")
# workflow.add_edge("sentiment_agent", "researcher_bear_agent")
# workflow.add_edge("valuation_agent", "researcher_bear_agent")

# # Researchers to Debate Room
# workflow.add_edge("researcher_bull_agent", "debate_room_agent")
# workflow.add_edge("researcher_bear_agent", "debate_room_agent")

# # Debate Room to Risk Management
# workflow.add_edge("debate_room_agent", "portfolio_management_agent")

workflow.add_edge(["short_term_agent", "long_term_agent", "technical_analyst_agent", "fundamentals_agent", "sentiment_agent", "valuation_agent"], "portfolio_management_agent")

# Risk Management to Portfolio Management
# workflow.add_edge("risk_management_agent", "portfolio_management_agent")
# workflow.add_edge("portfolio_management_agent", END)
workflow.add_edge("portfolio_management_agent", END)

app = workflow.compile() 