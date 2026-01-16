import requests
from dotenv import load_dotenv
import os
from pinecone import Pinecone
from agents import function_tool
from typing import List, Dict

load_dotenv()

# Environment variables
NAMESPACE = os.getenv("NAMESPACE", "vandan")
INDEX_NAME = os.getenv("INDEX_NAME")
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
SEARCH_API_URL = "https://www.searchapi.io/api/v1/search"

# Initialize Pinecone client once (reused for database searches)
_pinecone_client = None
_pinecone_index = None


def _get_pinecone_index():
    """Get or create Pinecone index instance (singleton pattern)."""
    global _pinecone_client, _pinecone_index
    
    if _pinecone_index is None:
        if _pinecone_client is None:
            _pinecone_client = Pinecone(api_key=PINECONE_API_KEY)
        _pinecone_index = _pinecone_client.Index(INDEX_NAME)
    
    return _pinecone_index


def search_research_papers(query: str, max_results: int = 5):
    """
    Search research papers using SearchAPI.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of dictionaries containing title, link, and source for each paper
    """
    if not SEARCH_API_KEY:
        return []
        
    params = {
        "engine": "google_ai_mode",
        "q": query,
        "api_key": SEARCH_API_KEY
    }

    try:
        response = requests.get(SEARCH_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        references = data.get("reference_links", [])[:max_results]

        results = []
        for ref in references:
            results.append({
                "title": ref.get("title", "Untitled"),
                "link": ref.get("link", ""),
                "source": ref.get("source", "Unknown")
            })

        return results
    except Exception as e:
        print(f"Error searching research papers: {e}")
        return []


@function_tool
def search_database_tool(query: str, top_k: int = 5) -> List[Dict]:
    """
    Search the internal vector database for relevant document chunks.
    
    This tool searches through previously indexed research papers and documents
    stored in the vector database. It uses semantic similarity to find the most
    relevant chunks that match the query.
    
    Args:
        query: The search query string to find relevant content
        top_k: Number of top results to return (default: 5, max recommended: 20)
        
    Returns:
        List of dictionaries containing:
        - score: Relevance score (0-1, higher is better)
        - page: Page number where the chunk was found
        - text: The actual text content of the chunk
        
    Example:
        search_database_tool("transformer architecture", top_k=5)
    """
    if not INDEX_NAME or not PINECONE_API_KEY:
        return []
    
    if not query or not query.strip():
        return []
    
    try:
        index = _get_pinecone_index()
        
        # Use the same query format as vector_store.py for consistency
        # This format works with Pinecone serverless and managed embeddings (llama-text-embed-v2)
        results = index.query(
            namespace=NAMESPACE,
            top_k=top_k,
            data=query
        )
        
        # Handle response format - Pinecone serverless returns results in "matches" or "hits"
        matches = []
        if isinstance(results, dict):
            # Check for different possible response structures
            if "matches" in results:
                matches = results["matches"]
            elif "result" in results:
                if isinstance(results["result"], dict) and "hits" in results["result"]:
                    matches = results["result"]["hits"]
                elif isinstance(results["result"], list):
                    matches = results["result"]
            elif "hits" in results:
                matches = results["hits"]
        elif isinstance(results, list):
            matches = results
        
        formatted_results = []
        for match in matches:
            # Extract metadata and score from match object
            metadata = {}
            score = 0.0
            
            if isinstance(match, dict):
                metadata = match.get("metadata", {})
                score = match.get("score", match.get("_score", 0.0))
            else:
                # Handle object attributes
                metadata = getattr(match, "metadata", None) or {}
                score = getattr(match, "score", None) or getattr(match, "_score", 0.0)
            
            # Ensure metadata is a dict
            if not isinstance(metadata, dict):
                metadata = {}
            
            chunk_text = metadata.get("chunk_text", "")
            page = metadata.get("page", 0)
            
            if chunk_text:  # Only include results with text
                formatted_results.append({
                    "score": round(float(score), 3),
                    "page": int(page) if page else 0,
                    "text": chunk_text
                })
        
        return formatted_results
        
    except Exception as e:
        print(f"Error searching database: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return empty list on error to allow agent to continue
        return []
