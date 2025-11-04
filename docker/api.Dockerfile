# API image: FastAPI + Uvicorn
FROM python:3.11-slim

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps (build tools + git if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git && rm -rf /var/lib/apt/lists/*

# Install Poetry (no virtualenv inside container)
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_CREATE=false
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

WORKDIR /app

# Copy only dependency files first to leverage Docker layer caching
COPY ma-min-app/pyproject.toml /app/
# If you have poetry.lock, copy it too:
# COPY ma-min-app/poetry.lock /app/

RUN poetry install --no-interaction --no-ansi

# Now copy the application source
COPY ma-min-app /app

EXPOSE 8000
CMD ["uvicorn", "src.ma_app.api:app", "--host", "0.0.0.0", "--port", "8000"]

