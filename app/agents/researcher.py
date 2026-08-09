"""Web Researcher agent.

Calls the search tool in app/tools/web_search.py for each sub-question
and collects the results into `findings`.
"""
from app.graph.state import ResearchState
from app.tools.web_search import search_web


def researcher_node(state: ResearchState) -> dict:
    sub_questions = state.get("sub_questions", [])
    findings = []

    for question in sub_questions:
        result = search_web(question)
        findings.append(
            {
                "question": question,
                "findings": result["summary"],
                "sources": result["sources"],
            }
        )

    return {"findings": findings}
