"""
LangGraph workflow for the Student Database chatbot.

Graph shape:

    START
      │
      ▼
   classify  ──┬──► greeting_node ──┐
               ├──► database_query ─┤
               └──► general_node ───┤
                                    ▼
                                 format
                                    │
                                    ▼
                                   END
"""
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.chatbot.nodes import (
    classify_node,
    database_query_node,
    format_node,
    general_node,
    greeting_node,
)


class ChatState(TypedDict, total=False):
    """
    Shared state passed between nodes.

    total=False means all keys are optional — nodes can add them
    as they go. This is what makes LangGraph merge updates instead
    of replacing the whole state on every node return.
    """

    question: str
    category: str
    context: str
    reply: str


def _route_by_category(state: ChatState) -> str:
    """
    Conditional edge: decides which handler node to go to next
    based on `state["category"]`.
    """
    category = state.get("category", "general")
    if category == "greeting":
        return "greeting_node"
    if category == "database_query":
        return "database_query_node"
    return "general_node"


def build_graph():
    """Build and compile the LangGraph workflow."""
    graph = StateGraph(ChatState)

    # Register nodes
    graph.add_node("classify", classify_node)
    graph.add_node("greeting_node", greeting_node)
    graph.add_node("database_query_node", database_query_node)
    graph.add_node("general_node", general_node)
    graph.add_node("format", format_node)

    # Entry point
    graph.add_edge(START, "classify")

    # Conditional branch after classification
    graph.add_conditional_edges(
        "classify",
        _route_by_category,
        {
            "greeting_node": "greeting_node",
            "database_query_node": "database_query_node",
            "general_node": "general_node",
        },
    )

    # All handlers flow into `format`
    graph.add_edge("greeting_node", "format")
    graph.add_edge("database_query_node", "format")
    graph.add_edge("general_node", "format")

    # End
    graph.add_edge("format", END)

    return graph.compile()


# Module-level compiled graph — imported by the route
compiled_graph = build_graph()


def ask(question: str) -> dict:
    """
    Convenience function: run the graph for a single question.

    Returns:
        {
            "question": ...,
            "category": ...,
            "reply": ...
        }
    """
    initial_state: ChatState = {"question": question}
    final_state = compiled_graph.invoke(initial_state)
    return {
        "question": question,
        "category": final_state.get("category", "unknown"),
        "reply": final_state.get("reply", "(no reply)"),
    }