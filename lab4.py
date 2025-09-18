import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader
import os

# --- Fix for ChromaDB sqlite3 issue ---
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb
from chromadb.utils import embedding_functions

# --- Streamlit UI ---
st.title("📚 Lab 4 – Document Retrieval & RAG Chatbot")

st.sidebar.header("Lab 4 Mode")
mode = st.sidebar.radio("Choose part:", ["Part A – Retrieval Test", "Part B – RAG Chatbot"])

# ✅ Load API key
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    st.error("⚠️ OpenAI API key not found in Streamlit secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

# ✅ Initialize Chroma client
chroma_client = chromadb.PersistentClient(path="./ChromaDB_lab4")

def create_vectorDB():
    """Create ChromaDB collection with embeddings of 6 PDFs."""
    collection = chroma_client.get_or_create_collection(
        name="Lab4Collection",
        embedding_function=embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name="text-embedding-3-small"
        )
    )

    # Only embed once
    existing_ids = set(collection.get()["ids"])

    PDF_FOLDER = "pdfs"
    pdf_files = [
        "IST 652 Syllabus.pdf",
        "IST 782 Syllabus.pdf",
        "IST614 Info tech Mgmt & Policy Syllabus.pdf",
        "IST688-BuildingHC-AIAppsV2.pdf",
        "IST691 Deep Learning in Practice Syllabus.pdf",
        "IST736-Text-Mining-Syllabus.pdf",
    ]

    for file in pdf_files:
        if file in existing_ids:
            continue
        file_path = os.path.join(PDF_FOLDER, file)
        if not os.path.exists(file_path):
            continue
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            if text.strip():
                collection.add(
                    documents=[text],
                    metadatas=[{"source": file}],
                    ids=[file]
                )
                st.sidebar.success(f"✅ Embedded: {file}")
        except Exception as e:
            st.sidebar.error(f"❌ Error processing {file}: {e}")

    return collection

# ✅ Initialize vector DB once
if "Lab4_vectorDB" not in st.session_state:
    st.session_state["Lab4_vectorDB"] = create_vectorDB()

collection = st.session_state["Lab4_vectorDB"]

# --- Part A: Retrieval Test ---
if mode == "Part A – Retrieval Test":
    st.subheader("🔍 Retrieval Test (Top 3 Relevant Documents)")

    test_queries = ["Generative AI", "Text Mining", "Data Science Overview"]
    query_choice = st.selectbox("Pick a test query:", test_queries)

    if st.button("Run Test Search"):
        results = collection.query(query_texts=[query_choice], n_results=3)
        st.write(f"### Top 3 results for **{query_choice}**")
        for idx, meta in enumerate(results["metadatas"][0]):
            st.write(f"{idx+1}. {meta['source']}")

# --- Part B: Chatbot with RAG ---
elif mode == "Part B – RAG Chatbot":
    st.subheader("💬 Chatbot (RAG-Enhanced)")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display conversation
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.chat_input("Ask me about the courses..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 🔎 Retrieve top 2 docs
        results = collection.query(query_texts=[user_input], n_results=2)
        retrieved_docs = [doc for doc in results["documents"][0]]
        sources = [meta["source"] for meta in results["metadatas"][0]]

        context = "\n\n".join(retrieved_docs)

        # 🧠 Prompt to LLM
        prompt = f"""
        You are a helpful assistant for course information.
        Use the following retrieved syllabi to answer clearly.
        If you use this info, say "Based on the syllabi I found...".
        
        Context:
        {context}

        Question: {user_input}
        """

        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                stream=True,
            )
            response = st.write_stream(stream)

        st.session_state.messages.append({"role": "assistant", "content": response})

        # Show sources
        with st.expander("📂 Sources used"):
            for s in sources:
                st.write(f"- {s}")
