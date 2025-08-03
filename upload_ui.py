import streamlit as st
from modules.upload import save_pdf
from modules.chunk_embed import chunk_and_store

st.title("StudentHub AI")

subject = st.text_input("Enter the subject name:")
doc_type = st.selectbox("Select the document type:", ["Subject Content", "Syllabus","Previous Year Paper/Sample Paper"])

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file and subject and doc_type:
    if st.button("Upload & Process"):
        with st.spinner("Processing file, please wait..."):
            file_path = save_pdf(uploaded_file, subject, doc_type)
            chunk_and_store(file_path, subject, doc_type)
        st.success("File uploaded and processed successfully!")
