from langgraph.graph import StateGraph, END
from .state import CoachingState
from .nodes import compute_deterministic_metrics, evaluate_communication_node

def build_coaching_graph():
    workflow = StateGraph(CoachingState)
    
    workflow.add_node("compute_metrics", compute_deterministic_metrics)
    workflow.add_node("evaluate", evaluate_communication_node)
    
    workflow.set_entry_point("compute_metrics")
    workflow.add_edge("compute_metrics", "evaluate")
    workflow.add_edge("evaluate", END)
    
    return workflow.compile()
