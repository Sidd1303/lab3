import streamlit as st
from openai import OpenAI

st.title("💬 Lab 3: Streaming Chatbot with Conversation Buffer")

st.write(
    "This chatbot streams responses in real time. "
    "It only remembers the last 2 user messages and their responses."
)

# ✅ Get API key from Streamlit secrets
try:
    openai_api_key = st.secrets["openai"]["api_key"]
except Exception:
    st.error("⚠️ OpenAI API key not found in Streamlit secrets.")
    st.stop()

# OpenAI client
client = OpenAI(api_key=openai_api_key)

# Sidebar for model choice
st.sidebar.header("Chatbot Settings")
use_advanced = st.sidebar.checkbox("Use Advanced Model (gpt-4o)", value=False)

model_name = "gpt-4o" if use_advanced else "gpt-4o-mini"
st.sidebar.write(f"📌 Model in use: **{model_name}**")

# Initialize message history if not exists
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input box
if prompt := st.chat_input("Type your message..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build context (only last 2 user-assistant pairs)
    context_messages = st.session_state.messages[-4:]

    # Stream assistant response
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=model_name,
            messages=context_messages,
            stream=True,
        )
        response = st.write_stream(stream)

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Ensure buffer only keeps last 2 exchanges (user + assistant)
    if len(st.session_state.messages) > 4:
        st.session_state.messages = st.session_state.messages[-4:]
