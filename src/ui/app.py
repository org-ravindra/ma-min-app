import streamlit as st
st.title("Master Architect – Minimal App")
prompt = st.text_area("Describe what you want to design")
if st.button("Generate"):
st.info("(Stub) Call API /generate here and render sections…")
