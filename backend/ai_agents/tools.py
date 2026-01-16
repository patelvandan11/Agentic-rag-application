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
    Search for research papers online using external search APIs.
    
    This tool searches the web for research papers related to the given query.
    It returns a list of papers with their titles, links, and sources.
    
    Args:
        query: The search query string (e.g., "transformer neural networks", "BERT architecture")
        
    Returns:
        List of dictionaries, each containing:
        - title: Paper title
        - link: URL to the paper
        - source: Source/publication venue
        
    Example:
        search_papers_tool("attention mechanisms in deep learning")
        Returns: [{"title": "...", "link": "...", "source": "..."}, ...]
    """
    return search_research_papers(query)


@function_tool
def download_arxiv_tool(arxiv_url: str):
    """
    Download a research paper PDF from arXiv.
    
    This tool downloads a PDF file from arXiv given a valid arXiv URL.
    The paper is saved locally and can then be indexed into the vector database.
    
    Args:
        arxiv_url: Full arXiv URL (e.g., "https://arxiv.org/abs/1706.03762" or "https://arxiv.org/pdf/1706.03762.pdf")
        
    Returns:
        String path to the downloaded PDF file (e.g., "downloaded_papers/1706.03762.pdf")
        
    Raises:
        May raise exceptions if the URL is invalid or download fails
        
    Example:
        download_arxiv_tool("https://arxiv.org/abs/1706.03762")
        Returns: "downloaded_papers/1706.03762.pdf"
    """
    return download_arxiv_pdf(arxiv_url, UPLOAD_DIR)


@function_tool
def index_pdf_tool(file_path: str):
    """
    Index a PDF file into the vector database for semantic search.
    
    This tool processes a PDF file by:
    1. Loading and chunking the PDF into smaller text segments
    2. Generating embeddings for each chunk
    3. Storing the chunks with metadata (page numbers, text) in the vector database
    
    After indexing, the PDF content becomes searchable using semantic search tools.
    
    Args:
        file_path: Path to the PDF file to index (e.g., "downloaded_papers/1706.03762.pdf")
        
    Returns:
        String confirmation message indicating how many chunks were indexed
        
    Example:
        index_pdf_tool("downloaded_papers/1706.03762.pdf")
        Returns: "Indexed 45 chunks from downloaded_papers/1706.03762.pdf"
    """
    records = load_and_chunk_pdf(file_path)
    upsert_records(records)
    return f"Indexed {len(records)} chunks from {file_path}"
