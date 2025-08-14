from langchain_core.messages import HumanMessage
from agents.state import AgentState, show_agent_reasoning, show_workflow_status
import json
import ast

def data_summary(state: AgentState):
    
    return {
        "messages": state["messages"],
        "data": {
            **state["data"],
        }
    }
