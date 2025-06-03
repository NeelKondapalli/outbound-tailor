import streamlit as st
import pandas as pd
import tempfile
import os
from fill import run_personalization

st.title("Outreach Personalizer")
st.write("Upload a CSV file with company names and domains. The app will browser recent news and make a 1-2 sentence outreach message for each company.")

@st.cache_data(show_spinner=False)
def personalize_from_uploaded_file(uploaded_bytes, anthropic_key, linkup_key):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_input:
        tmp_input.write(uploaded_bytes)
        tmp_input_path = tmp_input.name
    tmp_output_path = tmp_input_path.replace(".csv", "_outreach.xlsx")
    result_path = run_personalization(tmp_input_path, tmp_output_path, anthropic_key, linkup_key)

    if result_path:
        with open(result_path, "rb") as f:
            file_bytes = f.read()
        os.remove(result_path)
    else:
        file_bytes = None
    os.remove(tmp_input_path)
    return file_bytes

if "anthropic_api_key" not in st.session_state:
    st.session_state.anthropic_api_key = ""

if "linkup_api_key" not in st.session_state:
    st.session_state.linkup_api_key = ""

anthropic_key = st.text_input(
        "Anthropic API Key",
        st.session_state.anthropic_api_key,
        key="anthropic_key",
)
linkup_key = st.text_input(
        "Linkup API Key",
        st.session_state.linkup_api_key,
        key="linkup_key",
)

if anthropic_key:
    st.session_state.anthropic_api_key = anthropic_key

if linkup_key:
    st.session_state.linkup_api_key = linkup_key


if st.session_state.anthropic_api_key != "" and st.session_state.linkup_api_key != "":
    st.info("API Key is set. You can now upload a CSV file to begin.")
    uploaded_file = st.file_uploader("Upload your company names CSV", type=["csv"])

    if uploaded_file is not None:
        with st.spinner("Processing..."):
            file_bytes = personalize_from_uploaded_file(uploaded_file.getvalue(), st.session_state.anthropic_api_key, st.session_state.linkup_api_key)
        if file_bytes:
            st.success(f"Done. Download below:")
            st.download_button(
                label="Download personalized XLSX",
                data=file_bytes,
                file_name="personalized.xlsx",
                mime="text/xlsx"
            )
        else:
            st.warning("Could not find any companies in the CSV file.")
    else:
        st.info("Please upload a CSV file to begin.")