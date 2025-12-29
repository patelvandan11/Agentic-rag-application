import requests
from dotenv import load_dotenv
import os

load_dotenv()

SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
SEARCH_API_URL = "https://www.searchapi.io/api/v1/search"


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
