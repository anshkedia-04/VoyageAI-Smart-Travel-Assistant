# 🧭 VoyageAI – Smart Travel Concierge

> **Your AI-powered personal travel architect** — plan smarter, discover off-beat gems, and estimate budgets in seconds.

![Python](https://img.shields.io/badge/Python-3.11%2B-0B2545?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-0F766E?style=for-the-badge&logo=streamlit)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic%20AI-D97706?style=for-the-badge)

## Overview

**VoyageAI** combines a **LangGraph ReAct multi-agent backend** (`FastAPI`) with a modern **Streamlit Travel Concierge UI** to craft personalized day-by-day itineraries, surface both classic highlights and off-beat spots, estimate trip expenses, and summarize local weather & transit.

## Key Features

- **Structured Trip Brief Builder**: Curated quick-start getaways plus destination, duration, travelers, budget tier, currency, travel interests, off-beat toggle, and custom notes.
- **Editorial Travel Dossier View**:
  - Safe, flexible Markdown itinerary parser supporting varied `Day N` headings and logistics sections (`Hotels`, `Restaurants`, `Transportation`, `Cost Breakdown`, `Per Day Expense Budget`, `Weather`).
  - Session trip history switcher and one-click `.md` itinerary download.
  - Configurable execution modes: configured/cloud FastAPI backend, `localhost:8000`, custom URL, or standalone **Direct API (Groq / OpenAI)** mode.
- **Budget & Packing Toolkit**: Interactive multi-category trip cost calculator with a Plotly spend-distribution chart and pre-departure packing checklist.
- **Production-Hardened Backend & Tooling**:
  - Request ID & latency logging middleware, `GET /health` provider/tool readiness report, `recursion_limit` guard, and `503` diagnostic handling for missing credentials.
  - Timeouts, metric units, and graceful fallbacks across Weather, Geoapify/Tavily Place Search, and Currency tools.

## Run Locally

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure environment variables**:
   Copy `.env.example` to `.env` and add at least `GROQ_API_KEY` or `OPENAI_API_KEY` (plus optional `OPENWEATHERMAP_API_KEY`, `GEOAPIFY_API_KEY`, `TAVILY_API_KEY`, `EXCHANGE_RATE_API_KEY`).
3. **Start the FastAPI backend**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
4. **Start the Streamlit frontend**:
   ```bash
   streamlit run streamlit_app.py
   ```

### Run Tests

```bash
python -m unittest discover -s tests -v
```

## Deployment

- **Full Stack with Docker Compose**:
  ```bash
  cp .env.example .env
  docker compose up --build
  ```
  Starts `backend` (`http://localhost:8000`) with `/health` check and `frontend` (`http://localhost:8501`) automatically wired via `VOYAGEAI_BACKEND_URL=http://backend:8000`.
- **Render (Backend API)**: Configured via `render.yaml` (`healthCheckPath: /health`, `uvicorn main:app --host 0.0.0.0 --port $PORT`).
- **Streamlit Community Cloud (Frontend)**: Point main file path to `streamlit_app.py` (supports `Direct API` via `st.secrets` or a connected `VOYAGEAI_BACKEND_URL`).

## Contact

- **Developer**: Ansh Kedia · [anshkedia.04@gmail.com](mailto:anshkedia.04@gmail.com)
