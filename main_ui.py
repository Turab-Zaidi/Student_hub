import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from main import workflow
from typing import List
import os

SUBJECTS = ["Compiler Design", "Internet Protocol"]


st.set_page_config(page_title="StudentHub AI", page_icon="🧠", layout="wide")
st.sidebar.title(" StudentHub Assistant")

st.title("🎓 Ask Anything About Your Subject")

if "subject" not in st.session_state:
    st.session_state.subject = SUBJECTS[0]  
if "last_subject" not in st.session_state:
    st.session_state.last_subject = st.session_state.subject
if "chat_history" not in st.session_state:
    st.session_state.chat_history: List = []

selected_subject = st.sidebar.selectbox(
    "Select Subject", SUBJECTS, index=SUBJECTS.index(st.session_state.subject)
)
st.session_state.subject = selected_subject

if st.session_state.subject != st.session_state.last_subject:
    st.session_state.chat_history = []
    st.session_state.last_subject = st.session_state.subject

if st.sidebar.button("🧹 Clear Chat"):
    st.session_state.chat_history = []


for msg in st.session_state.chat_history:
    role = "👤 You" if isinstance(msg, HumanMessage) else "🤖 Assistant"
    st.markdown(f"**{role}:** {msg.content}", unsafe_allow_html=True)

user_input = st.chat_input("Type your question here or type 'quit' to end...")




if user_input:
    st.session_state.chat_history.append(HumanMessage(content=user_input))

    initial_state = {
        "messages": st.session_state.chat_history,
        "subject": st.session_state.subject,
        "intent": None,
        "tool_result": None
    }
    with st.spinner("Processing Input"):
        final_state = workflow.invoke(initial_state)

    ai_reply = final_state["tool_result"]["result"]
    st.rerun()
