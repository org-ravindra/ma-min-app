import json
import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Master Architect – Minimal App", layout="wide")
st.title("Master Architect – Minimal App")

with st.sidebar:
    st.header("Settings")
    k = st.number_input("Top-K context", min_value=0, max_value=10, value=4, step=1)
    model = st.text_input("Model override (optional)", value="")
    st.caption("API: " + API_URL)

prompt = st.text_area("Describe what you want to design", height=180, placeholder="e.g., Design a real-time data ingestion on AWS with cost guardrails")

col1, col2 = st.columns([1,1])
with col1:
    run = st.button("Generate", type="primary")
with col2:
    health = st.button("API Health Check")

if health:
    try:
        r = requests.get(f"{API_URL}/health", timeout=10)
        st.success(r.json())
    except Exception as e:
        st.error(f"Health check failed: {e}")

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

        st.success(f"Run ID: {data.get('run_id')} · Latency: {data.get('latency_ms')} ms")
        tabs = st.tabs([s.get("title", f"Section {i+1}") for i, s in enumerate(data.get("sections", []))])
        for t, s in zip(tabs, data.get("sections", [])):
            with t:
                st.markdown(s.get("body", ""))

        st.subheader("Artifacts")
        for f in data.get("files", []):
            p = f.get("path")
            name = f.get("name")
            try:
                with open(p, "rb") as fh:
                    st.download_button(label=f"Download {name}", data=fh, file_name=name)
            except Exception:
                st.write(name, p)

