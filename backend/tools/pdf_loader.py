from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def load_and_chunk_pdf(pdf_path: str):
    # 1️⃣ Load PDF (page-wise)
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()  # List[Document]

    # 2️⃣ Text Splitter (research-optimized)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=250,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    records = []

    # 3️⃣ Page-aware chunking (VERY IMPORTANT)
    for page in pages:
        page_chunks = splitter.split_text(page.page_content)

        for i, chunk in enumerate(page_chunks):
            records.append({
                "_id": f"{pdf_path}-page{page.metadata.get('page', 0)}-chunk{i}",
                "chunk_text": chunk,
                "page": page.metadata.get("page", 0),
                "type": "text"
            })

    return records
