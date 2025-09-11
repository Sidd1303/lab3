import streamlit as st
from openai import OpenAI

st.title("📄 Lab 2c: Document Summarizer")

st.write(
    "Upload a document and choose how you’d like it summarized. "
    "The app will generate a summary automatically using the model you select."
)

# ✅ Get API key from Streamlit secrets
try:
    openai_api_key = st.secrets["openai"]["api_key"]
except Exception:
    st.error("⚠️ OpenAI API key not found in Streamlit secrets.")
    st.stop()

# OpenAI client
client = OpenAI(api_key=openai_api_key)

# Sidebar controls
st.sidebar.header("Summary Options")

summary_type = st.sidebar.radio(
    "Choose summary style:",
    [
        "Summarize in 100 words",
        "Summarize in 2 connecting paragraphs",
        "Summarize in 5 bullet points",
    ],
)

use_advanced = st.sidebar.checkbox("Use Advanced Model (gpt-4o)", value=False)

# Model selection
if use_advanced:
    model_name = "gpt-4o"
else:
    model_name = "gpt-4o-mini"

st.sidebar.write(f"📌 Model in use: **{model_name}**")

# File uploader
uploaded_file = st.file_uploader("Upload a document (.txt or .md)", type=("txt", "md"))

if uploaded_file:
    document = uploaded_file.read().decode()

    # Build instruction prompt
    instructions = f"""
    You are a helpful assistant. Summarize the document as per the chosen style.

    Document:
    {document}

    Task:
    {summary_type}
    """

    # Generate summary
    with st.spinner("⏳ Generating summary..."):
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": instructions}],
        )

    summary = response.choices[0].message.content
    st.subheader("📌 Summary")
    st.write(summary)
