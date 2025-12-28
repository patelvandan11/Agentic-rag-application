from fastapi import FastAPI, UploadFile, File
import shutil
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
