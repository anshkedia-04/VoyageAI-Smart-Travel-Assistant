from functools import lru_cache
import os
import time
from typing import Literal
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from starlette.responses import JSONResponse

from exception.exceptionhandling import ConfigurationError
from logger.logging import get_logger

load_dotenv()
logger = get_logger("voyageai.api")

app = FastAPI(
    title="VoyageAI Travel Agent API",
    version="1.2.0",
    description="LangGraph-powered AI travel planning backend with weather, place search, and budget tools.",
)

raw_origins = os.getenv("CORS_ORIGINS", "*").strip()
allowed_origins = ["*"] if raw_origins == "*" else [o.strip() for o in raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allowed_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "%s %s -> %s (%.1f ms) [req=%s]",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
        request_id,
    )
    return response


class QueryRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    question: str = Field(
        ...,
        min_length=2,
        max_length=4000,
        description="Travel planning prompt or destination query.",
    )
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
            "version": app.version,
            "groq_configured": bool(os.getenv("GROQ_API_KEY")),
            "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
            "tools_configured": {
                "weather": bool(os.getenv("OPENWEATHERMAP_API_KEY")),
                "geoapify": bool(os.getenv("GEOAPIFY_API_KEY")),
                "tavily": bool(os.getenv("TAVILY_API_KEY")),
                "currency": bool(os.getenv("EXCHANGE_RATE_API_KEY")),
            },
        }
    )


@app.post("/query")
async def query_travel_agent(query: QueryRequest):
    try:
        react_app = _get_compiled_graph(query.model_provider)
        output = react_app.invoke(
            {"messages": [query.question]},
            config={"recursion_limit": 25},
        )

        if isinstance(output, dict) and "messages" in output and output["messages"]:
            final_output = output["messages"][-1].content
        else:
            final_output = str(output)

        return {"answer": final_output}
    except ConfigurationError as exc:
        logger.warning("Configuration error on /query: %s", exc)
        return JSONResponse(status_code=503, content={"error": str(exc)})
    except Exception as exc:
        logger.exception("Unhandled error during /query execution")
        return JSONResponse(status_code=500, content={"error": f"Agent execution failed: {exc}"})
