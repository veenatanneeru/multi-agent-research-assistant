"""FastAPI entrypoint for the Multi-Agent Research Assistant."""
import logging

from fastapi import FastAPI
from pydantic import BaseModel

from app.config.settings import settings
from app.graph.build_graph import research_graph

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Multi-Agent Research Assistant",
    description="LangGraph-orchestrated agents that research a question "
    "and return a synthesized report.",
    version="0.1.0",
)


class ResearchRequest(BaseModel):
    query: str


class ResearchResponse(BaseModel):
    query: str
    sub_questions: list[str]
    findings: list[dict]
    report: str


@app.get("/health")
def health():
    return {"status": "ok", "model": settings.ollama_model}


@app.post("/research", response_model=ResearchResponse)
def research(req: ResearchRequest):
    logger.info("Received research request: %s", req.query)

    result = research_graph.invoke({"query": req.query})

    return ResearchResponse(
        query=req.query,
        sub_questions=result.get("sub_questions", []),
        findings=result.get("findings", []),
        report=result.get("report", ""),
    )
