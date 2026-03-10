from fastapi import FastAPI, UploadFile, File ,APIRouter
import shutil
from pydantic import BaseModel
import os
from agents import Runner
from ai_agents.planner_agent import planner_agent
from ai_agents.reasoning_agent import reasoning_agent
from ai_agents.summarizer_agent import summarizer_agent
from tools.pdf_loader import load_and_chunk_pdf
from memory.vector_store import upsert_records, search_records
import os
from tools.arxiv_downloader import download_arxiv_pdf
from tools.pdf_loader import load_and_chunk_pdf
import pyaudio
import wave
from memory.vector_store import upsert_records
from langchain_openai import ChatOpenAI
from ai_agents.react_search_agent import react_search_agent
from ai_agents.search_agent import react_existing_agent
from tools.paper_search import search_database_tool
from Audio.TTS import translate_speech
from Audio.STT import text_to_speech

app = FastAPI()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

UPLOAD_DIR = "backend/data/papers"
os.makedirs(UPLOAD_DIR, exist_ok=True)
# public_router = APIRouter(prefix="/public", tags=["Public"])

@app.get("/")
def health():
    return {"status": "ok"}



@app.post("/speech-to-text",tags=["Audio"])
def stt_endpoint(audio_file_path: str):
    transcription = translate_speech(audio_file_path)
    return {"message": "Speech transcribed successfully", "transcription": transcription}

# ✅ NEW: Upload PDF from ANY local path (via UI)
@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    records = load_and_chunk_pdf(file_path)
    upsert_records(records)

    return {
        "message": "File uploaded and indexed successfully",
        "filename": file.filename,
        "chunks": len(records)
    }
@app.post("/search")
async def search(query: str):
    """
    Database-only ReAct search.
    No external search.
    1. Search vector DB
    2. Use ReAct agent to reason over results
    3. Return final answer
    
    """

    result = await Runner.run(
        react_existing_agent,
        query
    )

    return {
        "query": query,
        "answer": result.final_output
    }



@app.get("/record",tags=["Audio"])
def record_audio():

    chunk = 1024
    format = pyaudio.paInt16
    channels = 1 
    rate = 44100 
    seconds = 5  # now make this button configurable in the UI and pass as a parameter to this function
    filename = "recorded.wav"

    p = pyaudio.PyAudio()

    stream = p.open(format=format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    frames = []

    for _ in range(0, int(rate / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    return {"message": "Recording completed", "file": filename}



UPLOAD_DIR = "downloaded_papers"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/download-arxiv")
async def download_arxiv(arxiv_url: str):
    """
    1. Download arXiv paper
    2. Chunk PDF
    3. Store in Pinecone
    """

    file_path = download_arxiv_pdf(arxiv_url, UPLOAD_DIR)

    return file_path

class IndexRequest(BaseModel):
    file_path: str
from fastapi.responses import FileResponse

# @app.post("/text-to-speech")
# def tts_endpoint(text: str):

#     output_file = "answer.wav"

#     text_to_speech(text, output_file)

#     return FileResponse(
#         output_file,
#         media_type="audio/wav",
#         filename="answer.wav"
#     )
@app.post("/index-paper")
def index_paper(req: IndexRequest):
    file_path = req.file_path
     # 🔒 Safety check
    if not os.path.exists(file_path):
        return {"error": "File not found", "path": file_path}

    records = load_and_chunk_pdf(file_path)
    upsert_records(records)

    return {
        "message": "Paper indexed successfully",
        "file": file_path,
        "chunks": len(records)
    }
    
from tools.paper_search import search_research_papers
    
   
@app.post("/search_papers")
async def search_papers(query: str):
    
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0)
    results = search_research_papers(query)
    
    return {
        "query": query,
        "results": results
    }
    
@app.post("/filter-arxiv")
async def filter_arxiv(query: str):
    """
    Filter, download, and index arXiv papers based on query
    """

    # ✅ MUST await async function
    search_results = await search_papers(query)

    # search_results is now a dict
    results = search_results.get("results", [])

    # 2️⃣ Filter ONLY arXiv links
    arxiv_links = [
        res["link"]
        for res in results
        if "arxiv.org/abs/" in res.get("link", "")
        or "arxiv.org/pdf/" in res.get("link", "")
    ]

    if not arxiv_links:
        return {
            "message": "No arXiv papers found",
            "downloaded_files": []
        }

    # 3️⃣ Download, chunk, and index
    downloaded_files = []

    for link in arxiv_links:
        file_path = download_arxiv_pdf(link, UPLOAD_DIR)
        downloaded_files.append(file_path)

         

    return {
        "message": "Filtered arXiv papers downloaded and indexed successfully",
        "downloaded_files": downloaded_files,
        "count": len(downloaded_files)
    }


@app.post("/react-search")
async def react_search(query: str):
    result = await Runner.run(react_search_agent, query)

    return {
        "query": query,
        "answer": result.final_output  # ✅ SAFE
    }

# thsi is my main code