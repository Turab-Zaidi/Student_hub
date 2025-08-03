import os
from modules.load_db import load_vector_store
from modules.llm import call_llm
from dotenv import load_dotenv

load_dotenv()

def gen_quiz(question, subject, doc_type=['Subject Content','Previous Year Paper/Sample Paper']):
    vector_store = load_vector_store(subject)
    doc_type = [dt.lower().replace(" ", "_") for dt in doc_type]

    similarities = vector_store.similarity_search_with_score(
        question,
        k=1,
        filter={"soruce_type": {"$in": doc_type}}
    )
    
    if not similarities or similarities[0][1] < 0.75:
        return {
            "type": "fallback",
            "reason": "query_did_not_match_documents",
            "threshold_used": 0.75
        }
    
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 5, "filter": {"soruce_type": {"$in": doc_type}}}
    )

    docs = retriever.get_relevant_documents(question)
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = f"""
        You are an experienced university exam paper creator.

        Based on the following study material, generate 3 high-quality exam-style questions on the topic "{question}". Use academic language and structure them like previous year papers.
        The question should be clear concise and should ask student of some stuff.
        CONTENT:
            {context}
    """

    result = call_llm(prompt, 512)

    return{
        'type': 'quiz',
        'results': result,
        'docs': docs  
    }