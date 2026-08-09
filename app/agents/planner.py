"""Planner agent.

Uses the local LLM to break the user's research question into 2-4
focused sub-questions, so the Researcher agent can search each one
separately instead of running one broad search. Falls back to treating
the whole query as a single sub-question if the LLM output can't be
parsed (e.g. simple questions, or an unexpected response format).
"""
import json
import logging

from app.config.llm import get_llm
from app.graph.state import ResearchState

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a research planner. Given a user's research \
question, break it down into 2 to 4 focused sub-questions that together \
would give a thorough answer to the original question.

Respond with ONLY a JSON array of strings, nothing else. No markdown, \
no explanation. Example:
["What is X?", "How does X affect Y?", "What are the risks of X?"]

If the question is already narrow and specific, it's fine to return \
just 1-2 sub-questions instead of forcing extra ones."""


def _parse_sub_questions(raw_text: str, fallback_query: str) -> list[str]:
    """Try to parse the LLM's JSON array response. Falls back to a
    single-item list (the original query) if parsing fails for any
    reason, so the graph always has something valid to work with.
    """
    text = raw_text.strip()

    # Some models wrap JSON in markdown code fences despite instructions;
    # strip those if present.
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        parsed = json.loads(text)
        if isinstance(parsed, list) and all(isinstance(q, str) for q in parsed):
            cleaned = [q.strip() for q in parsed if q.strip()]
            if cleaned:
                return cleaned
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning("Could not parse planner output as JSON: %s", exc)

    logger.warning(
        "Falling back to single sub-question (raw planner output: %r)", raw_text
    )
    return [fallback_query]


def planner_node(state: ResearchState) -> dict:
    query = state["query"]
    llm = get_llm(temperature=0.2)

    response = llm.invoke(
        [
            ("system", SYSTEM_PROMPT),
            ("human", f"Research question: {query}"),
        ]
    )

    sub_questions = _parse_sub_questions(response.content, fallback_query=query)

    return {"sub_questions": sub_questions}
