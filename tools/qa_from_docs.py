import os
from modules.load_db import load_vector_store
from modules.llm import call_llm
from dotenv import load_dotenv

load_dotenv()

def qa_from_docs(question, subject, doc_type = 'Subject Content'):
    vector_store = load_vector_store(subject)

    similarities = vector_store.similarity_search_with_score(
        question,
        k=1,
        filter={"source_type": doc_type.lower().replace(" ", "_")}
    )
    
    if not similarities or similarities[0][1] < 0.75:
        return {
            "type": "fallback",
            "reason": "query_did_not_match_documents",
            "threshold_used": 0.75
        }


    retriever = vector_store.as_retriever(
        search_kwargs={"k": 5, "filter": {"source_type": doc_type.lower().replace(" ", "_")}}
    )

    docs = retriever.get_relevant_documents(question)
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = f"""You are an assistant answering based on the given context.

        Context:
            {context}\n
        Question: 
            {question}\n
        Answer:
    """
    result = call_llm(prompt, 1024)
    return {
        'type': 'answer',
        'results': result, 
        'docs': docs
    }