"""Planner agent.

STUB (Step 1): treats the whole query as a single sub-question so the
graph runs end-to-end. Real decomposition logic (asking the LLM to break
the query into N focused sub-questions) lands in a later step.
"""
from app.graph.state import ResearchState


def planner_node(state: ResearchState) -> dict:
    query = state["query"]

    # TODO (future step): prompt the LLM to decompose `query` into a
    # list of focused sub-questions instead of this passthrough.
    sub_questions = [query]

    return {"sub_questions": sub_questions}
