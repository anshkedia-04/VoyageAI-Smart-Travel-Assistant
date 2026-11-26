FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash appuser

COPY requirements.txt setup.py ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser agent ./agent
COPY --chown=appuser:appuser config ./config
COPY --chown=appuser:appuser exception ./exception
COPY --chown=appuser:appuser logger ./logger
COPY --chown=appuser:appuser prompt_library ./prompt_library
COPY --chown=appuser:appuser tools ./tools
COPY --chown=appuser:appuser utils ./utils
COPY --chown=appuser:appuser ui ./ui
COPY --chown=appuser:appuser main.py streamlit_app.py ./

USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
