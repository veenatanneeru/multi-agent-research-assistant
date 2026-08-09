"""Summarizer agent.

Synthesizes the collected findings into a final Markdown report using
the local LLM (via Ollama).
"""
from app.config.llm import get_llm
from app.graph.state import ResearchState

SYSTEM_PROMPT = """You are a research report writer. Given a user's \
research question and a set of findings gathered by a research agent, \
write a clear, well-structured Markdown report answering the question. \
If the findings are placeholder/stub text (not real research), say so \
plainly instead of inventing facts."""


def summarizer_node(state: ResearchState) -> dict:
    llm = get_llm(temperature=0.3)

    findings = state.get("findings", [])
    findings_text = "\n\n".join(
        f"Q: {f['question']}\nFindings: {f['findings']}" for f in findings
    )

    prompt = (
        f"Research question: {state['query']}\n\n"
        f"Findings gathered:\n{findings_text}\n\n"
        "Write the final report now."
    )

    response = llm.invoke(
        [
            ("system", SYSTEM_PROMPT),
            ("human", prompt),
        ]
    )

    return {"report": response.content}
