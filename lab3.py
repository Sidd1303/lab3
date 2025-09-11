import streamlit as st
from openai import OpenAI

st.title("💬 Lab 3: Refined Chatbot with Conversation Buffer (30)")

st.write(
    "Ask me a question! I’ll explain in a way a 10-year-old can understand. "
    "After answering, I’ll ask if you want more info. "
    "The bot remembers up to the last 30 messages."
)

# ✅ Get API key from secrets
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

# Session state to track mode
if "mode" not in st.session_state:
    st.session_state.mode = "ask"  # "ask", "more_info"
if "last_question" not in st.session_state:
    st.session_state.last_question = None

# Conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if user_input := st.chat_input("Type your message..."):

    if st.session_state.mode == "ask":
        # Save user’s question
        st.session_state.last_question = user_input
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Bot answers simply + asks for more info
        instructions = f"""
        You are a chatbot talking to a 10-year-old. 
        Answer the following question in simple words. 
        After the explanation, ask exactly: "DO YOU WANT MORE INFO".
        Question: {user_input}
        """
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": instructions}],
                stream=True,
            )
            response = st.write_stream(stream)

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.mode = "more_info"

    elif st.session_state.mode == "more_info":
        # Save user reply
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        if user_input.lower() in ["yes", "y"]:
            # Give more info, then re-ask
            instructions = f"""
            You already explained the answer to this question:
            {st.session_state.last_question}

            Now, provide a deeper but still simple explanation suitable for a 10-year-old.
            At the end, again ask: "DO YOU WANT MORE INFO".
            """
            with st.chat_message("assistant"):
                stream = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": instructions}],
                    stream=True,
                )
                response = st.write_stream(stream)

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.mode = "more_info"

        elif user_input.lower() in ["no", "n"]:
            # Reset to new cycle
            with st.chat_message("assistant"):
                reply = "Okay! What question can I help you with next?"
                st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.mode = "ask"

        else:
            # Invalid input
            with st.chat_message("assistant"):
                reply = "Please answer with 'yes' or 'no'. DO YOU WANT MORE INFO?"
                st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.mode = "more_info"

    # 🔑 Enforce buffer (keep last 30 messages max)
    if len(st.session_state.messages) > 30:
        st.session_state.messages = st.session_state.messages[-30:]
