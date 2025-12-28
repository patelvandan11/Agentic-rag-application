import streamlit as st
import requests

# ===============================
# Backend API URLs
# ===============================
BACKEND_URL = "http://127.0.0.1:8000"
UPLOAD_API = f"{BACKEND_URL}/upload-file"
SEARCH_API = f"{BACKEND_URL}/search"

# ===============================
# Page Config
# ===============================
st.set_page_config(
    page_title="Agentic RAG – Research Assistant",
    layout="wide"
)

st.title("📚 Agentic RAG – Research Assistant")
st.write("Upload research PDFs and ask questions using RAG + Pinecone.")

# ===============================
# SIDEBAR – FILE UPLOAD
# ===============================
st.sidebar.header("📄 Upload Document")

uploaded_file = st.sidebar.file_uploader(
    "Choose a PDF from any location",
    type=["pdf"]
)

if uploaded_file is not None:
    st.sidebar.write("Selected file:", uploaded_file.name)

    if st.sidebar.button("Upload & Index"):
        # ✅ FIXED HERE
        with st.spinner("Uploading and indexing PDF..."):
            response = requests.post(
                UPLOAD_API,
                files={"file": uploaded_file}
            )

        if response.status_code == 200:
            data = response.json()
            st.sidebar.success("✅ File indexed successfully")
            st.sidebar.write("Chunks created:", data["chunks"])
        else:
            st.sidebar.error("❌ Upload failed")

# ===============================
# MAIN – SEARCH SECTION
# ===============================
st.header("🔎 Ask a Question")

query = st.text_input(
    "Enter your question based on uploaded documents",
    placeholder="e.g. What are the key contributions of this paper?"
)

if st.button("Search"):
    if not query:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching documents..."):
            response = requests.post(
                SEARCH_API,
                params={"query": query}
            )

        if response.status_code != 200:
            st.error("❌ Search failed")
        else:
            data = response.json()

            # ===============================
            # ANSWER SECTION
            # ===============================
            st.subheader("🧠 AI Answer")
            st.success(data.get("answer", "No answer generated"))

            # ===============================
            # RETRIEVED CONTEXT
            # ===============================
            st.subheader("📄 Retrieved Context")

            results = data.get("results", [])

            if not results:
                st.info("No matching documents found.")
            else:
                for idx, r in enumerate(results, start=1):
                    with st.expander(
                        f"Result {idx} | Score: {r['score']} | Page: {r['page']}"
                    ):
                        st.write(r["text"])
