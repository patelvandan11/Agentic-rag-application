from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")
NAMESPACE ="vandan"
region = os.getenv("region")


pc = Pinecone(api_key=PINECONE_API_KEY)

# Create index ONCE
if not pc.has_index(INDEX_NAME):
    pc.create_index_for_model(
        name=INDEX_NAME,
        cloud="aws",
        region=region,
        embed={
            "model": "llama-text-embed-v2",
            "field_map": {"text": "chunk_text"}
        }
    )

index = pc.Index(INDEX_NAME)


def upsert_records(records: list[dict]):
    if not records:
        return

    index.upsert_records(
        namespace=NAMESPACE,
        records=records
    )


def search_records(query: str, top_k: int = 5):
    """
    Search records in the vector database.
    
    Args:
        query: Search query string
        top_k: Number of results to return
        
    Returns:
        List of matching records with metadata
    """
    try:
        # Use query method for Pinecone serverless with managed embeddings
        results = index.query(
            namespace=NAMESPACE,
            top_k=top_k,
            data=query
        )
        
        # Handle different response formats
        if isinstance(results, dict):
            if "matches" in results:
                return results["matches"]
            elif "result" in results and "hits" in results["result"]:
                return results["result"]["hits"]
            elif "hits" in results:
                return results["hits"]
        elif isinstance(results, list):
            return results
        
        return []
    except Exception as e:
        print(f"Error searching records: {e}")
        return []
