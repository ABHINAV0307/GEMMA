from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
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
from langchain.docstore.document import Document
from langchain.chains import create_retrieval_chain
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize environment variables
groq_api_key = os.getenv('GROQ_API_KEY')
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Initialize the LLM
llm = ChatGroq(groq_api_key=groq_api_key, model_name="gemma-7b-it")

# Global variables for embeddings and vectors
embeddings = None
vectors = None
text_splitter = None

# Pydantic model for query
class Query(BaseModel):
    input: str

def vector_embedding():
    """Initialize vector embeddings from text files"""
    global embeddings, vectors, text_splitter
    
    if embeddings is None:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    documents = []
    folder_path = "posts"
    
    # Read all text files from the posts directory
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            try:
                with open(os.path.join(folder_path, filename), 'r', encoding='windows-1252') as f:
                    content = f.read()
                    documents.append(Document(page_content=content))
            except UnicodeDecodeError:
                continue  # Skip files that can't be read
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    final_documents = text_splitter.split_documents(documents)
    
    # Create vector store
    vectors = FAISS.from_documents(final_documents, embeddings)

def scrape_and_update_embeddings():
    """Background task to periodically update embeddings"""
    while True:
        subprocess.run(['python', 'scrap.py'])
        vector_embedding()
        time.sleep(600)  # Wait 10 minutes before next update

# Start background scraping thread
scraping_thread = threading.Thread(target=scrape_and_update_embeddings, daemon=True)
scraping_thread.start()

@app.on_event("startup")
async def startup_event():
    """Initialize embeddings on startup"""
    vector_embedding()

@app.get("/")
async def read_root():
    """Serve the main HTML file"""
    return FileResponse('static/index.html')

@app.post("/query")
async def query_news(query: Query):
    """Handle queries and return relevant information"""
    if vectors is None:
        raise HTTPException(status_code=500, detail="Vectors not initialized.")
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_template(
        """
        Answer the questions based on the provided context only. Make sure response is not in bold.
        Please provide the most accurate keyword response based on the question and in different lines.
        
        <context>
        {context}
        </context>
        
        Question: {input}
        """
    )
    
    # Create document chain
    document_chain = create_stuff_documents_chain(llm, prompt)
    
    # Create retriever and retrieval chain
    retriever = vectors.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
    # Get response
    response = retrieval_chain.invoke({'input': query.input})
    
    return {
        "answer": response['answer'],
        "context": response["context"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return {
        "error": str(exc),
        "type": type(exc).__name__
    }, 500

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
