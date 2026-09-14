from langgraph.graph import StateGraph, END
from .state import CoachingState
from .nodes import compute_deterministic_metrics, evaluate_communication_node


def build_coaching_graph():
    # Deliberately linear until owned, comparable attempts exist. Retain the
    # workflow seam without claiming this slice provides adaptive coaching.
    workflow = StateGraph(CoachingState)
    workflow.add_node("evaluate", evaluate_communication_node)
    workflow.add_node("measure", compute_deterministic_metrics)
    workflow.set_entry_point("evaluate")
    workflow.add_edge("evaluate", "measure")
    workflow.add_edge("measure", END)
    return workflow.compile()
