import streamlit as st
import requests
import os

# ===============================
# Backend API URLs
# ===============================
BACKEND_URL = "http://127.0.0.1:8000"

UPLOAD_API = f"{BACKEND_URL}/upload-file"
SEARCH_API = f"{BACKEND_URL}/search"
REACT_API = f"{BACKEND_URL}/react-search"
INDEX_API = f"{BACKEND_URL}/index-paper"

# Audio APIs
TTS_API = f"{BACKEND_URL}/text-to-speech"
STT_API = f"{BACKEND_URL}/speech-to-text"
RECORD_API = f"{BACKEND_URL}/record"

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.join(BASE_DIR, "backend", "downloaded_papers")

os.makedirs(PAPER_DIR, exist_ok=True)

# ===============================
# PAGE CONFIG
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
    "Choose a PDF",
    type=["pdf"]
)

if uploaded_file is not None:

    st.sidebar.write("Selected file:", uploaded_file.name)

    if st.sidebar.button("Upload & Index"):

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
# SIDEBAR – EXISTING PAPERS
# ===============================
st.sidebar.header("📂 Available Papers")

all_papers = sorted([
    f for f in os.listdir(PAPER_DIR)
    if f.lower().endswith(".pdf")
])

if "paper_selection" not in st.session_state:
    st.session_state.paper_selection = {}

if not all_papers:
    st.sidebar.info("No papers available")

else:

    for paper in all_papers:

        paper_path = os.path.join(PAPER_DIR, paper)

        st.session_state.paper_selection[paper_path] = st.sidebar.checkbox(
            paper,
            value=st.session_state.paper_selection.get(paper_path, False)
        )

    st.sidebar.divider()

    if st.sidebar.button("⬆ Upload Selected Papers"):

        selected_papers = [
            path for path, selected in st.session_state.paper_selection.items()
            if selected
        ]

        if not selected_papers:
            st.sidebar.warning("Select at least one paper")

        else:

            with st.spinner("Uploading papers to vector DB..."):

                for path in selected_papers:

                    requests.post(
                        INDEX_API,
                        json={"file_path": path}
                    )

            st.sidebar.success("✅ Papers uploaded successfully")


# ===============================
# VOICE INPUT (STT)
# ===============================
st.header("🎤 Voice Question")

if st.button("Record Question"):

    with st.spinner("Recording voice..."):

        r = requests.get(RECORD_API)

        if r.status_code == 200:

            audio_file = r.json()["file"]

            stt = requests.post(
                STT_API,
                params={"audio_file_path": audio_file}
            )

            if stt.status_code == 200:

                query = stt.json()["transcription"]

                st.success("Voice converted to text")
                st.write("Query:", query)

                st.session_state.voice_query = query
                
                


# ===============================
# SEARCH SECTION
# ===============================
st.header("🔎 Ask a Question")

search_type = st.radio(
    "Search Type",
    ["Simple Search", "ReAct Search"],
    horizontal=True
)

query = st.text_input(
    "Enter your question",
    value=st.session_state.get("voice_query", ""),
    placeholder="e.g. What are the contributions of this paper?"
)

# ===============================
# SEARCH BUTTON
# ===============================
if st.button("Search"):

    if not query:
        st.warning("Please enter a question")

    else:

        with st.spinner("Searching documents..."):

            if search_type == "Simple Search":
                api_url = SEARCH_API
            else:
                api_url = REACT_API

            response = requests.post(
                api_url,
                params={"query": query}
            )

        if response.status_code != 200:

            st.error("Search failed")

        else:

            data = response.json()

            st.subheader("🧠 AI Answer")

            if search_type == "Simple Search":
                answer = data.get("answer", "No answer generated")

            else:
                answer = data.get("answer", "No answer generated")

            st.success(answer)

            # ===============================
            # TEXT TO SPEECH
            # ===============================
            import tempfile

            # ===============================
            # TEXT TO SPEECH
            # ===============================
            if st.button("🔊 Listen Answer"):

                    response = requests.post(
                        TTS_API,
                        params={"text": answer}
                    )

                    if response.status_code == 200:

                        # Save audio temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                            f.write(response.content)
                            audio_path = f.name

                        # Play audio
                        st.audio(audio_path, format="audio/wav")

                    else:
                        st.error("TTS failed")