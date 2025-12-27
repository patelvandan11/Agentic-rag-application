from langchain.vectorstores import FAISS
from tools.embeddings import get_embeddings

def create_vector_store(texts: list[str]):
    embeddings = get_embeddings()
    return FAISS.from_texts(texts, embeddings)
