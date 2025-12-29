import requests
from dotenv import load_dotenv
import os
import pinecone as pc
load_dotenv()

NAMESPACE=os.getenv("NAMESPACE")
region=os.getenv("region")
INDEX_NAME=os.getenv("INDEX_NAME")
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
PINECONE_API_KEY=os.getenv("PINECONE_API_KEY")
SEARCH_API_URL = "https://www.searchapi.io/api/v1/search"


pc = pc.Pinecone(api_key=PINECONE_API_KEY, environment=region)

def search_research_papers(query: str, max_results: int = 5):
    """
    Search research papers using SearchAPI
    
    
    """
    params = {
        "engine": "google_ai_mode",
        "q": query,
        "api_key": SEARCH_API_KEY
    }

    response = requests.get(SEARCH_API_URL, params=params)
    response.raise_for_status()

    data = response.json()

    references = data.get("reference_links", [])[:max_results]

    results = []
    for ref in references:
        results.append({
            "title": ref.get("title"),
            "link": ref.get("link"),
            "source": ref.get("source")
        })

    return results

from agents import function_tool
from typing import List, Dict
from tools.paper_search import search_research_papers


from agents import function_tool
from pinecone import Pinecone

# Initialize once (global)
pc = Pinecone(api_key=PINECONE_API_KEY)
INDEX_NAME = os.getenv("INDEX_NAME")


@function_tool
def search_database_tool(query: str, top_k: int = 5):
    """
    Search ONLY the internal vector database.
    """

    index = pc.Index(INDEX_NAME)

    results = index.search(
        namespace="default",
        query={
            "top_k": top_k,
            "inputs": {
                "text": query
            }
        }
    )

    return [
        {
            "score": round(match["score"], 3),
            "page": match["metadata"].get("page"),
            "text": match["metadata"].get("chunk_text")
        }
        for match in results["matches"]
    ]
