# UI image: Streamlit frontend
FROM python:3.11-slim

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git && rm -rf /var/lib/apt/lists/*

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_CREATE=false
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

WORKDIR /app

COPY ma-min-app/pyproject.toml /app/
# COPY ma-min-app/poetry.lock /app/
RUN poetry install --no-interaction --no-ansi

COPY ma-min-app /app

# UI listens on 8501; needs API_URL at runtime
EXPOSE 8501
ENV API_URL="http://localhost:8000"
CMD ["streamlit", "run", "src/ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

