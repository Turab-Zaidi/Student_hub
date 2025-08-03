from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools.tavily_search import TavilySearchResults
from modules.llm import call_llm
from dotenv import load_dotenv

load_dotenv()

def search_and_summarize(question):
    search = TavilySearchResults()
    raw_result = search.run(question)

    prompt = f"""
        You are an academic assistant. Read the following web search results and provide a factual, concise, and helpful answer to the query: "{question}"

        Results:
            {raw_result}
    """

    summary = call_llm(prompt)
    
    return {
        "type": "web",
        "result": summary,
        "raw_results": raw_result
    }
