import os
from modules.load_db import load_vector_store
from modules.llm import call_llm
from dotenv import load_dotenv

load_dotenv()

def summarize_content(question, subject, doc_type='Subject Content'):
    vector_db = load_vector_store(subject)

    similarities = vector_db.similarity_search_with_score(
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

    retriever = vector_db.as_retriever(
        search_kwargs={
            "k": 6,
            "filter": {
                "subject": subject,
                "source_type": doc_type.lower().replace(" ", "_")
            }
        }
    )
    docs = retriever.get_relevant_documents(question)
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = f"""

        Summarize the following study material about "{question}" in 200-300 words not more than that. Summary should be in 4 sections:
        - Introduction
        - Key Concepts
        - Real-World Applications
        - Conclusion

        CONTENT:
            {context}
    """
    result = call_llm(prompt, 1024)

    return{
        'type': 'summary',
        'results': result,
        'docs': docs  
    }