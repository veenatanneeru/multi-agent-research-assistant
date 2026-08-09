"""Shared state passed between agent nodes in the LangGraph graph.

Each agent node receives the current ResearchState, does its job, and
returns a dict of the fields it wants to update. LangGraph merges that
into the running state before handing it to the next node.
"""
from typing import TypedDict


class ResearchState(TypedDict, total=False):
    # The original user question.
    query: str

    # Sub-questions produced by the Planner agent.
    sub_questions: list[str]

    # Raw findings gathered by the Researcher agent, one entry per
    # sub-question: {"question": str, "findings": str, "sources": list[str]}
    findings: list[dict]

    # Final synthesized report produced by the Summarizer agent.
    report: str
