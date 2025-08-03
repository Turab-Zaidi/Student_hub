from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import os

def chunk_and_store(file_path, subject, doc_type,persist_dir = "embeddings"):
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()

    for doc in docs:
        doc.metadata['subject'] = subject.lower().replace(" ", "_")
        doc.metadata['source_type'] = doc_type.lower().replace(" ", "_")
        doc.metadata['file'] = os.path.basename(file_path)

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    db_path = os.path.join(persist_dir, subject.lower().replace(" ", "_"))
    vector_db = Chroma.from_documents(chunks, embedding, persist_directory=db_path)
    vector_db.persist()
    return vector_db

