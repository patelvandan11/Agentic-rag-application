import streamlit as st
import requests
import os

# ===============================
# Backend API URLs
# ===============================
PAPER_DIR = "backend/downloaded_papers"
INDEX_API = "http://127.0.0.1:8000/index-paper"
BACKEND_URL = "http://127.0.0.1:8000"
UPLOAD_API = f"{BACKEND_URL}/upload-file"
SEARCH_API = f"{BACKEND_URL}/search"
ARXIV_SEARCH_API = f"{BACKEND_URL}/search_papers"
ARXIV_FILTER_API = f"{BACKEND_URL}/filter-arxiv"
REACT_API = f"{BACKEND_URL}/react-search"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER_DIR = os.path.join(BASE_DIR, "backend", "downloaded_papers")
UPLOAD_DIR="backend/data/papers"
UPLOAD_API = f"{BACKEND_URL}/upload-file"


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
import os
# ===============================
# SIDEBAR – FILE UPLOAD

os.makedirs(UPLOAD_DIR, exist_ok=True)

pdf_files = [
    f for f in os.listdir(UPLOAD_DIR)
    if f.lower().endswith(".pdf")
]


import os
import streamlit as st
import requests



# ===============================
# Config
# ===============================



st.sidebar.header("📂 Available Papers")

# Ensure directory exists
os.makedirs(PAPER_DIR, exist_ok=True)

# Get ALL PDFs from disk
all_papers = sorted([
    f for f in os.listdir(PAPER_DIR)
    if f.lower().endswith(".pdf")
])

# Track checkbox state
if "paper_selection" not in st.session_state:
    st.session_state.paper_selection = {}

if not all_papers:
    st.sidebar.info("No papers available.")
else:
    st.sidebar.caption("Select papers to upload into vector database")

    for paper in all_papers:
        paper_path = os.path.join(PAPER_DIR, paper)

        st.session_state.paper_selection[paper_path] = st.sidebar.checkbox(
            paper,
            value=st.session_state.paper_selection.get(paper_path, False)
        )

    st.sidebar.divider()

    if st.sidebar.button("⬆️ Upload Selected Papers"):
        selected_papers = [
            path for path, selected in st.session_state.paper_selection.items()
            if selected
        ]

        if not selected_papers:
            st.sidebar.warning("Please select at least one paper.")
        else:
            with st.spinner("Uploading selected papers to vector DB..."):
                for path in selected_papers:
                    requests.post(
                        INDEX_API,
                        json={"file_path": path}
                    )

            st.sidebar.success("✅ Selected papers uploaded successfully!")

# ===============================
# ===============================
# MAIN – SEARCH SECTION
# ===============================
st.header("🔎 Ask a Question")

# 🔹 Search type selector
search_type = st.radio(
    "Select Search Type",
    ["Simple Search", "ReAct Search"],
    horizontal=True
)

query = st.text_input(
    "Enter your question based on uploaded documents",
    placeholder="e.g. What are the key contributions of this paper?"
)

if st.button("Search"):
    if not query:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching documents..."):

            # 🔹 Choose API based on search type
            if search_type == "Simple Search":
                api_url = SEARCH_API   # e.g. /search
            else:
                api_url = REACT_API           # e.g. /react-search

            response = requests.post(
                api_url,
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
                        f"Result {idx} | Score: {r.get('score')} | Page: {r.get('page')}"
                    ):
                        st.write(r.get("text"))
