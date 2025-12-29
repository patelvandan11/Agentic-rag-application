from agents import function_tool
from tools.paper_search import search_research_papers
from tools.arxiv_downloader import download_arxiv_pdf
from memory.vector_store import upsert_records
from tools.pdf_loader import load_and_chunk_pdf
import os

UPLOAD_DIR = "downloaded_papers"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@function_tool
def search_papers_tool(query: str):
    """
    Search research papers related to the query.
    """
    return search_research_papers(query)


@function_tool
def download_arxiv_tool(arxiv_url: str):
    """
    Download an arXiv paper and return file path.
    """
    return download_arxiv_pdf(arxiv_url, UPLOAD_DIR)


@function_tool
def index_pdf_tool(file_path: str):
    """
    Index a downloaded PDF into vector database.
    """
    records = load_and_chunk_pdf(file_path)
    upsert_records(records)
    return f"Indexed {len(records)} chunks from {file_path}"
