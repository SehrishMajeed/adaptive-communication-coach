from langgraph.graph import StateGraph, END
from .state import CoachingState
from .nodes import compute_deterministic_metrics, evaluate_communication_node, compare_attempts_node

def build_coaching_graph():
    workflow = StateGraph(CoachingState)
    
    workflow.add_node("compute_metrics", compute_deterministic_metrics)
    workflow.add_node("evaluate", evaluate_communication_node)
    workflow.add_node("compare", compare_attempts_node)
    
    workflow.set_entry_point("evaluate")
    workflow.add_edge("evaluate", "compute_metrics")
    
    def route_attempt(state: CoachingState):
        if state.get("attempt_number", 1) > 1 and state.get("previous_attempt_metrics"):
            return "compare"
        return END
        
    workflow.add_conditional_edges("compute_metrics", route_attempt, {"compare": "compare", END: END})
    workflow.add_edge("compare", END)
    
    return workflow.compile()
