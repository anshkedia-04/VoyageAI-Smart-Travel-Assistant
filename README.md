# 🧭 VoyageAI – Smart Travel Concierge

> **Your AI-powered personal travel architect** — plan smarter, discover off-beat gems, and estimate budgets in seconds.

![Python](https://img.shields.io/badge/Python-3.10%2B-0B2545?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-0F766E?style=for-the-badge&logo=streamlit)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic%20AI-D97706?style=for-the-badge)

## Overview

**VoyageAI** combines a **LangGraph ReAct multi-agent backend** (FastAPI) with a modern **Streamlit Travel Concierge UI** to craft personalized day-by-day itineraries, surface both classic highlights and off-beat spots, estimate trip expenses, and summarize local weather & transit.

## Live Demo

- **Streamlit Frontend**: [VoyageAI Smart Travel Concierge](https://voyageai-smart-travel-assistant-pkrk9xcpwhhynq4h3eylis.streamlit.app/)

## Key Features

- **Structured Trip Brief Builder**: Pick curated quick-start getaways or configure destination, duration, travelers, budget tier, currency, travel interests, and custom requests.
- **Editorial Travel Dossier View**:
  - Flexible Markdown itinerary parser supporting `Day 1:` / `### Day 1:` / `**Day 1**` headings and dedicated logistics sections (Hotels, Dining, Transit, Cost Breakdown, Weather).
  - Session trip history switcher and one-click `.md` itinerary export.
  - Cloud (`Render`) / Localhost (`:8000`) / Custom backend endpoint selector with one-click health ping.
- **Budget & Packing Toolkit**: Interactive multi-category trip cost calculator with a Plotly spend-distribution chart and pre-departure packing checklist.
- **Hardened FastAPI Backend**:
  - `GET /health` endpoint for deployment healthchecks and cold-start wakeups.
  - Cached lazy LangGraph compilation (`_get_compiled_graph`) for fast server boot.

## Run Locally

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure environment variables** (see `.env.name` for required keys such as `GROQ_API_KEY`, `OPENWEATHERMAP_API_KEY`, `GEOAPIFY_API_KEY`, `TAVILY_API_KEY`, `EXCHANGE_RATE_API_KEY`).
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

- **Streamlit Community Cloud**: Point main file path to `streamlit_app.py` (themed via `.streamlit/config.toml`).
- **Render (Backend API)**: Configured via `render.yaml` (`uvicorn main:app --host 0.0.0.0 --port $PORT`).
- **Docker**:
  ```bash
  docker build -t voyageai-travel .
  docker run -p 8501:8501 voyageai-travel
  ```

## Contact

- **Developer**: Ansh Kedia · [anshkedia.04@gmail.com](mailto:anshkedia.04@gmail.com)
