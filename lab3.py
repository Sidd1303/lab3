import streamlit as st
from openai import OpenAI

st.title("💬 Lab 3: Streaming Chatbot")

st.write("This chatbot streams responses in real time using OpenAI models.")

# ✅ Get API key from Streamlit secrets
try:
    openai_api_key = st.secrets["openai"]["api_key"]
except Exception:
    st.error("⚠️ OpenAI API key not found in Streamlit secrets.")
    st.stop()

# Create OpenAI client
client = OpenAI(api_key=openai_api_key)

# Sidebar for model choice
st.sidebar.header("Chatbot Settings")
use_advanced = st.sidebar.checkbox("Use Advanced Model (gpt-4o)", value=False)

model_name = "gpt-4o" if use_advanced else "gpt-4o-mini"
st.sidebar.write(f"📌 Model in use: **{model_name}**")

# Maintain chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input box
if prompt := st.chat_input("Type your message..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response (streamed)
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=model_name,
            messages=st.session_state.messages,
            stream=True,
        )
        response = st.write_stream(stream)

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})
