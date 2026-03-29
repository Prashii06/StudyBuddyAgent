import os
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from agents.coordinator import CoordinatorAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

agent = CoordinatorAgent()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("SmartDesk Phase 1 agent starting up...")
    yield
    logger.info("SmartDesk Phase 1 agent shutting down.")

app = FastAPI(
    title="SmartDesk Phase 1 — AI Study Buddy Agent",
    description="Single ADK + Gemini agent for lecture summarization and intent classification",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ──────────────────────────────────────────────────

class AgentRequest(BaseModel):
    message: Optional[str] = None
    query: Optional[str] = None          # alias for message

class BatchRequest(BaseModel):
    messages: List[str]

class AgentResponse(BaseModel):
    intent: Optional[str]
    agent: Optional[str]
    confidence: Optional[str]
    parameters: Optional[dict]
    response: str
    status: str


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "agent": "SmartDesk Phase 1"}


@app.post("/run-agent", response_model=AgentResponse)
def run_agent(body: AgentRequest):
    text = body.message or body.query
    if not text or not text.strip():
        raise HTTPException(status_code=422, detail="Provide 'message' or 'query' in the request body.")

    start = time.time()
    logger.info(f"[/run-agent] input: {text[:120]}")
    result = agent.run(text.strip())
    logger.info(f"[/run-agent] completed in {time.time()-start:.2f}s | intent={result.get('intent')}")
    return result


@app.post("/batch")
def batch_run(body: BatchRequest):
    if len(body.messages) > 5:
        raise HTTPException(status_code=422, detail="Maximum 5 messages per batch request.")

    results = []
    for msg in body.messages:
        try:
            results.append(agent.run(msg.strip()))
        except Exception as e:
            results.append({"status": "error", "message": str(e), "intent": None,
                            "agent": None, "confidence": None, "parameters": None, "response": ""})
    return {"results": results, "count": len(results)}