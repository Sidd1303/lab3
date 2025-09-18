import streamlit as st

# Multipage navigation
nav = st.navigation([
    st.Page("home.py", title="🏠 Home"),
    st.Page("lab1_qa.py", title="🧪 Lab 2c: Summarizer"),
    st.Page("lab3.py", title="💬 Lab 3: Chatbot"),
    st.Page("lab4.py", title="🧩 Lab 4: VectorDB (Chroma)"),  # ✅ Added
    st.Page("extra.py", title="📄 Extra Page"),
])

nav.run()

