import os
import json
import requests
import streamlit as st

# Use service name by default so UI->API works inside Docker
API_URL = os.getenv("API_URL", "http://ma-api:8000")

st.set_page_config(page_title="Master Architect – Minimal App", layout="wide")
st.title("Master Architect – Minimal App")

with st.sidebar:
    st.header("Settings")
    k = st.number_input("Top-K context", min_value=0, max_value=10, value=4, step=1)
    model = st.text_input("Model override (optional)", value="")
    st.caption(f"API: {API_URL}")

prompt = st.text_area(
    "Describe what you want to design",
    height=180,
    placeholder="e.g., Design a real-time data ingestion on AWS with cost guardrails",
)

col1, col2 = st.columns([1, 1])
with col1:
    run = st.button("Generate", type="primary")
with col2:
    health = st.button("API Health Check")

# --- Health check ---
if health:
    try:
        r = requests.get(f"{API_URL}/health", timeout=10)
        r.raise_for_status()
        st.success(r.json())
    except Exception as e:
        st.error(f"Health check failed: {e}")

# --- Generate ---
if run:
    if not prompt.strip():
        st.warning("Please enter a prompt.")
    else:
        with st.spinner("Generating..."):
            try:
                payload = {"prompt": prompt.strip(), "k": int(k)}
                if model.strip():
                    payload["model"] = model.strip()
                r = requests.post(f"{API_URL}/generate", json=payload, timeout=180)
                r.raise_for_status()
                data = r.json()
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()

        # Header line (only if present)
        run_id = data.get("run_id")
        latency_ms = data.get("latency_ms")
        if run_id is not None or latency_ms is not None:
            st.success(f"Run ID: {run_id} · Latency: {latency_ms} ms")

        # Sections fallback to 'output'
        sections = data.get("sections") or []
        files = data.get("files") or []

        if sections:
            tabs = st.tabs([s.get("title", f"Section {i+1}") for i, s in enumerate(sections)])
            for t, s in zip(tabs, sections):
                with t:
                    st.markdown(s.get("body", ""))
        else:
            st.subheader("Output")
            st.markdown(data.get("output", "_(no output)_"))

        # Artifacts (optional)
        if files:
            st.subheader("Artifacts")
            for f in files:
                p = f.get("path")
                name = f.get("name") or (os.path.basename(p) if p else "file")
                if not p:
                    st.write(name)
                    continue
                try:
                    with open(p, "rb") as fh:
                        st.download_button(label=f"Download {name}", data=fh, file_name=name)
                except Exception:
                    # If file is not on UI container FS, at least show metadata
                    st.write(name, p)
