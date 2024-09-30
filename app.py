import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()


## load the GROQ And OpenAI API KEY 
groq_api_key=os.getenv('GROQ_API_KEY')
os.environ["GOOGLE_API_KEY"]=os.getenv("GOOGLE_API_KEY")

st.title("AI News AGGREGATOR")

llm=ChatGroq(groq_api_key=groq_api_key,model_name="gemma-7b-it")

prompt=ChatPromptTemplate.from_template(
"""
Answer the questions based on the provided context only.
Please provide the most accurate response based on the question
<context>
{context}
<context>
Questions:{input}

"""
)

from langchain.docstore.document import Document  # Import Document class

# Updated vector embedding function to handle text files
def vector_embedding():

    if "vectors" not in st.session_state:
        st.session_state.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

        # **Change 1: Loading text files with proper encoding and format**
        documents = []
        folder_path = "./posts"
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):  # Ensure we only load .txt files
                try:
                    with open(os.path.join(folder_path, filename), 'r', encoding='windows-1252') as f:
                        content = f.read()  # Load the text content
                        # **Change 2: Create Document objects with page_content**
                        documents.append(Document(page_content=content))
                except UnicodeDecodeError:
                    st.error(f"Error reading file: {filename}")

        # **Change 3: Create documents and chunks from text files**
        st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        st.session_state.final_documents = st.session_state.text_splitter.split_documents(documents)
        
        # **Change 4: Vector embedding of the documents**
        st.session_state.vectors = FAISS.from_documents(st.session_state.final_documents, st.session_state.embeddings)


prompt1=st.text_input("Enter news you want to search")

if st.button("Documents Embedding"):
    vector_embedding()
    st.write("Vector Store DB Is Ready")

import time



if prompt1:
    document_chain=create_stuff_documents_chain(llm,prompt)
    retriever=st.session_state.vectors.as_retriever()
    retrieval_chain=create_retrieval_chain(retriever,document_chain)
    start=time.process_time()
    response=retrieval_chain.invoke({'input':prompt1})
    print("Response time :",time.process_time()-start)
    st.write(response['answer'])

    # With a streamlit expander
    with st.expander("Document Similarity Search"):
        # Find the relevant chunks
        for i, doc in enumerate(response["context"]):
            st.write(doc.page_content)
            st.write("--------------------------------")




