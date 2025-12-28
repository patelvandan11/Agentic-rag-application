from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")
NAMESPACE = os.getenv("NAMESPACE")
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
    results = index.search(
        namespace=NAMESPACE,
        query={
            "top_k": top_k,
            "inputs": {"text": query}
        }
    )
    return results["result"]["hits"]
