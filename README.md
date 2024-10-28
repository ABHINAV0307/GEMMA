
# AI-Based News Aggregator

This project is an AI-powered news aggregator that scrapes real-time news data from a set of reputable news portals and allows users to interact with it through natural language queries. The application uses a Large Language Model (LLM) to retrieve relevant news articles based on user inputs.

## Components

### 1. Data Sources
- **Selected News Portals**:
  - **Moneycontrol**: Scrapes news data from the Moneycontrol News page.
  - **BBC News**: Scrapes news data from the BBC News portal.

**Technology Used**: 
- `BeautifulSoup` and `requests` libraries are used to scrape data from these websites.

---

### 2. Data Scraping
- **Scraping Logic**: 
  - For each selected news portal, the `scrap.py` file contains functions to scrape headlines, descriptions, and links to the articles.
  - The scraped data is stored as `.txt` files in a folder called `posts/`.

**Technology Used**: 
- **BeautifulSoup**: Parses HTML content of the news pages.
- **requests**: Fetches HTML content from news websites.

---

### 3. Data Preprocessing
- **Preprocessing Logic**: 
  - The scraped news data (stored in `.txt` files) is loaded and split into chunks to make it more manageable and easier to query.
  - The **RecursiveCharacterTextSplitter** is used to break the text into smaller, relevant sections.

**Technology Used**:
- **RecursiveCharacterTextSplitter** from LangChain for splitting the data into manageable chunks.

---

### 4. Vector Database
- **Vector Embedding**: 
  - The text chunks are embedded using **Google Generative AI Embeddings**.
  - The resulting vectors are stored in **FAISS** (a vector database) for efficient querying.

**Technology Used**:
- **Google Generative AI Embeddings**: For converting text into vector embeddings.
- **FAISS**: A vector database for storing and querying the embeddings.

---

### 5. Interaction Layer
- **Large Language Model (LLM)**: 
  - Integrated **LangChain** with **ChatGroq** (LLM) to interact with the vector database and respond to user queries.
  - The LLM generates responses based on the news data stored in the vector database.

**Technology Used**:
- **ChatGroq**: For interacting with the data and answering user queries.
- **LangChain**: For creating retrieval and document chains.

---

### 6. User Interaction
- **User Input**: 
  - Users can enter a keyword (e.g., "Adani," "Reliance") into the frontend interface.
- **Response Generation**: 
  - The LLM queries the vector database and retrieves the most relevant news articles based on the user's input.

**Technology Used**:
- **HTML,CSS,Javascript**: For the front-end, enabling user interaction and displaying search results.
- **LangChain**: For processing the user's input and generating relevant responses.

### 7. Front End
- **User Input**: 
  - Used HTML,CSS and Javascript to build front of the website.
- **Response Generation**: 
  - In ths user can enter the news in news search box and they will get response in accordance to that 

**Technology Used**:
- **HTML,CSS,Javascript**: For the front-end, enabling user interaction and displaying search results.
- **LangChain**: For processing the user's input and generating relevant responses.


---

### 8. Expected Outcomes
- **Timely and Relevant Updates**: Users receive real-time, relevant news updates based on the keywords they provide.
- **Natural Language Interaction**: The use of a language model enhances the user experience, allowing users to interact naturally with the news data.

## How to Run

1. **Create a virtual environment**:
   ```bash
   python -m venv venv

2. **Activate the virtual environment**:
   ```bash
   .\venv\Scripts\activate

3. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt

4. **Create a .env file in the root directory and add your API keys**:
   GROQ_API_KEY=your_groq_api_key
   GOOGLE_API_KEY=your_google_api_key

5. **Run the front in static file that is index.html**:

6. **Run the project**:
   ```bash
   fastapi run app.py

---

## Data Flow 
![image](https://github.com/user-attachments/assets/088bf5d3-41d5-4c94-8ba2-98d78b558dc5)
 
---





