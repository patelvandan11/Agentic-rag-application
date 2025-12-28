from langchain_community.document_loaders import PyPDFLoader


from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_and_chunk_pdf(pdf_path: str):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(documents)

    records = []
    for i, doc in enumerate(chunks):
        records.append({
            "_id": f"{pdf_path}-{i}",
            "chunk_text": doc.page_content,
            "page": doc.metadata.get("page", 0)
        })

    return records