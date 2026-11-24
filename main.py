from functools import lru_cache
from typing import Literal
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from starlette.responses import JSONResponse

load_dotenv()

app = FastAPI(
    title="VoyageAI Travel Agent API",
    version="1.1.0",
    description="LangGraph-powered AI travel planning backend with weather, place search, and budget tools.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    question: str = Field(..., min_length=2, description="Travel planning prompt or destination query.")
    model_provider: Literal["groq", "openai"] = Field(
        default="groq",
        description="LLM provider configured in config/config.yaml.",
    )


@lru_cache(maxsize=2)
def _get_compiled_graph(model_provider: str):
    """Lazily build and cache the LangGraph agent so server boot stays fast."""
    from agent.agentic_workflow import GraphBuilder

    graph = GraphBuilder(model_provider=model_provider)
    return graph()


@app.get("/")
async def root():
    return JSONResponse(content={"message": "VoyageAI Backend is Running Successfully!"})


@app.get("/health")
async def health():
    return JSONResponse(
        content={
            "status": "ok",
            "groq_configured": bool(os.getenv("GROQ_API_KEY")),
            "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        }
    )


@app.post("/query")
async def query_travel_agent(query: QueryRequest):
    try:
        react_app = _get_compiled_graph(query.model_provider)
        output = react_app.invoke({"messages": [query.question]})

        if isinstance(output, dict) and "messages" in output and output["messages"]:
            final_output = output["messages"][-1].content
        else:
            final_output = str(output)

        return {"answer": final_output}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})