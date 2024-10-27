from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import subprocess
import threading
import time
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.docstore.document import Document  # Import Document class
from langchain.chains import create_retrieval_chain
from dotenv import load_dotenv

load_dotenv()


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi import HTTPException
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS", "GET"],
    allow_headers=["*"],
)

groq_api_key = os.getenv('GROQ_API_KEY')
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

llm = ChatGroq(groq_api_key=groq_api_key, model_name="gemma-7b-it")

# To store embeddings and documents
embeddings = None
vectors = None
text_splitter = None

class Query(BaseModel):
    input: str

def vector_embedding():
    global embeddings, vectors, text_splitter

    if embeddings is None:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    documents = []
    folder_path = "posts"
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            try:
                with open(os.path.join(folder_path, filename), 'r', encoding='windows-1252') as f:
                    content = f.read()
                    documents.append(Document(page_content=content))
            except UnicodeDecodeError:
                continue  # Skip unreadable files

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    final_documents = text_splitter.split_documents(documents)
    vectors = FAISS.from_documents(final_documents, embeddings)

def scrape_and_update_embeddings():
    while True:
        subprocess.run(['python', 'scrap.py'])
        vector_embedding()
        time.sleep(600)  # Update every 10 minutes

# Start the background thread for scraping
scraping_thread = threading.Thread(target=scrape_and_update_embeddings, daemon=True)
scraping_thread.start()

@app.on_event("startup")
async def startup_event():
    vector_embedding()

@app.post("/query")
async def query_news(query: Query):
    if vectors is None:
        raise HTTPException(status_code=500, detail="Vectors not initialized.")
    
    prompt = ChatPromptTemplate.from_template(
        """
        Answer the questions based on the provided context only.Make sure response in not in bold
        Please provide the most accurate keyword response based on the question and in different lines
        <context>
        {context}
        <context>
        Questions:{input}
        """
    )

    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = vectors.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    response = retrieval_chain.invoke({'input': query.input})
    return {"answer": response['answer'], "context": response["context"]}