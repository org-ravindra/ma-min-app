# MA Minimal App
Run locally with either OpenAI or Ollama. See /src/ui/app.py for Streamlit UI.

## Quickstart
1. `cp .env.example .env` and fill keys or set `LLM_PROVIDER=ollama`.
2. `poetry install`
3. `python scripts/ingest_corpus.py`
4. `bash scripts/dev_server.sh`
