"""Builds the LangGraph state graph connecting Planner -> Researcher ->
Summarizer. This is the orchestration layer: agents themselves live in
app/agents/, this file just wires them together into a runnable graph.
"""
from langgraph.graph import END, StateGraph

from app.agents.planner import planner_node
from app.agents.researcher import researcher_node
from app.agents.summarizer import summarizer_node
from app.graph.state import ResearchState


def build_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("summarizer", summarizer_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "summarizer")
    graph.add_edge("summarizer", END)

    return graph.compile()


# Compiled once at import time; reused across requests.
research_graph = build_graph()
