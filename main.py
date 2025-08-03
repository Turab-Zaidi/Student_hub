from langgraph.graph import StateGraph, END, START, MessagesState
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict,  List,Optional, Literal,Annotated
from langchain_core.messages import BaseMessage,HumanMessage, AIMessage
from tools import duck_duck_go, qa_from_docs, quiz_generator,  summarizer
from pydantic import BaseModel
import operator
from dotenv import load_dotenv

load_dotenv()


class AgentState(TypedDict):
    messages: List[BaseMessage]
    subject: str
    intent: Optional[Literal["qa", "quiz", "summary","fallback"]]
    tool_result:Optional[Annotated[List[str],operator.add]]

class IntentClassifier(BaseModel):
    intent: Optional[Literal["qa", "quiz", "summary", "fallback"]]


def classify_intent(state: AgentState) -> AgentState:
    history = "\n".join([
        f"{'User' if isinstance(m, HumanMessage) else 'AI'}: {m.content}"
        for m in state["messages"][:-1 ]
    ])
    query = state["messages"][-1].content

    prompt = f"""
You are a university assistant. Classify the user's intent based on their most recent message.
History:
{history}

Latest message:
"{query}"

Return only one of these labels:
- "qa": user is asking a factual and completely topic related question relaeted to the {state["subject"]}
- "quiz": user is asking to generate questions regarding the subject {state["subject"]}
- "summary": user is asking to summarize content that belongs to the subject {state["subject"]}
- "fallback" : if the query is very general and does not match with this subject {state["subject"]}
Always output 'fallback' if the query is not related to the subject {state["subject"]}.

*** Very Important**: Your output must be a single word only no other output is accepted in any case.
    Answer with one of these only: qa, quiz, summary, fallback
    Output:
"""
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)
    structured_llm = llm.with_structured_output(IntentClassifier)
    intent = structured_llm.invoke(prompt)
    state["intent"] = intent.intent 
    return state

def run_tool(state: AgentState) -> AgentState:
    if state["intent"] == "qa":
        return 'qa'
    elif state["intent"] == "quiz":
        return 'quiz'
    elif state['intent'] == "summary":
        return 'summary'
    else:
        return 'fallback'
    

def qa_wrapper(state: AgentState) -> AgentState:
    query = state["messages"][-1].content
    result = qa_from_docs.qa_from_docs(query,state["subject"])
    state["tool_result"] = result
    return state

def quiz_wrapper(state: AgentState) -> AgentState:
    query = state["messages"][-1].content
    result = quiz_generator.gen_quiz(query, state["subject"])
    state["tool_result"] = result
    return state

def summary_wrapper(state: AgentState) -> AgentState:
    query = state["messages"][-1].content
    result = summarizer.summarize_content(query, state["subject"])
    state["tool_result"] = result
    return state

def fallback_wrapper(state: AgentState) -> AgentState:
    query = state["messages"][-1].content
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)

    context_messages = state["messages"][:-1]  
    conversation_history = ""

    for msg in context_messages[-5:]:
        if isinstance(msg, HumanMessage):
            conversation_history += f"User: {msg.content}\n"
        elif isinstance(msg, AIMessage):
            conversation_history += f"Assistant: {msg.content}\n"

    search_query_prompt = f"""
        You are an assistant that helps refine search queries.
        Given the following conversation history and the latest user query,
        generate a concise and effective search query that accurately captures what the user is asking for.
        Prioritize the most recent information and the core intent of the user.

        Conversation History:
        {conversation_history}

        Latest User Query:
        {query}

        Your refined search query:
    """

    refined_search_query_response = llm.invoke(search_query_prompt)
    refined_search_query = refined_search_query_response.content.strip()
    
    result = duck_duck_go.search_and_summarize(refined_search_query)
    state["tool_result"] = result
    return state

def check_tool_result(state: AgentState) -> AgentState:
    if state["tool_result"]['type'] in ['summary', 'quiz', 'answer','web']:
        return 'build_response'
    else:
        return 'fallback'
    
def build_response(state: AgentState) -> AgentState:
    from langchain_core.messages import AIMessage
    response = state["tool_result"]["result"]
    state["messages"].append(AIMessage(content=response))
    return state

def check_quit(state: AgentState) -> str:
    latest = state["messages"][-1].content.strip().lower()
    return "end" if latest == "quit" else "continue"
    
Graph  = StateGraph(AgentState) 

Graph.add_node('intent_classifier', classify_intent)
Graph.add_node('qa_tool',qa_wrapper)
Graph.add_node('quiz_tool', quiz_wrapper)
Graph.add_node('summary_tool', summary_wrapper)
Graph.add_node('fallback_tool', fallback_wrapper)
Graph.add_node("build_response", build_response)

Graph.add_conditional_edges(
    START,
    check_quit,
    {
        "continue": "intent_classifier",  # proceed with normal graph
        "end": END                        # immediately stop if "quit"
    }
)

Graph.add_conditional_edges(
    "intent_classifier",
    run_tool,
    {
        "qa": "qa_tool",
        "quiz": "quiz_tool",
        "summary": "summary_tool",
        "fallback": "fallback_tool"
    }
)

Graph.add_conditional_edges(
    "qa_tool",
    check_tool_result,
    {
        "build_response": "build_response",
        "fallback": "fallback_tool"
    }
)

Graph.add_conditional_edges(
    "quiz_tool",
    check_tool_result,
    {
        "build_response": "build_response",
        "fallback": "fallback_tool"
    }
)
Graph.add_conditional_edges(
    "summary_tool",
    check_tool_result,  
    {
        "build_response": "build_response",
        "fallback": "fallback_tool"
    }
)

Graph.add_edge("fallback_tool", "build_response")

Graph.add_edge(
    "build_response",  
    END
)
workflow = Graph.compile()