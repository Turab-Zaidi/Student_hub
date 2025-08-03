from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
import os

def load_vector_store(subject, persist_dir="embeddings"):
    embedder = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    db_path = os.path.join(persist_dir, subject.lower().replace(" ", "_"))
    return Chroma(persist_directory=db_path, embedding_function=embedder)