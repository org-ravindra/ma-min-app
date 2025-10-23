#!/usr/bin/env bash
set -euo pipefail
uvicorn src.ma_app.api:app --reload &
streamlit run src/ui/app.py
