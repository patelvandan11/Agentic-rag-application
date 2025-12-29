from fastapi import FastAPI, UploadFile, File
import shutil
from pydantic import BaseModel
import os
from agents import Runner
from ai_agents.planner_agent import planner_agent
from ai_agents.reasoning_agent import reasoning_agent
from ai_agents.summarizer_agent import summarizer_agent
from tools.pdf_loader import load_and_chunk_pdf
from memory.vector_store import upsert_records, search_records
from langchain_openai import ChatOpenAI


app = FastAPI()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

UPLOAD_DIR = "backend/data/papers"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def health():
    return {"status": "ok"}


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
    #  Vector search
    hits = search_records(query)

    # Process results
    processed_results = [
        {
            "score": round(hit["_score"], 3),
            "page": hit["fields"].get("page"),
            "text": hit["fields"]["chunk_text"]
        }
        for hit in hits
    ]

    # Build context for LLM
    context = "\n\n".join(
        f"(page {r['page']}) {r['text']}"
        for r in processed_results
    )

    # Call LLM / Agent
    llm_input = f"""
    Answer the question using ONLY the context below.

    Question:
    {query}

    Context:
    {context}
    """

    llm_response = await Runner.run(
        reasoning_agent,
        llm_input
    )

    # Final response
    return {
        "query": query,
        "results": processed_results,
        "answer": llm_response.final_output
    }

 
import os

from tools.arxiv_downloader import download_arxiv_pdf
from tools.pdf_loader import load_and_chunk_pdf
from memory.vector_store import upsert_records
 

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
