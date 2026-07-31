
# Enterprise Knowledge Assistant

An AI-powered Enterprise Knowledge Assistant built using **LangGraph**, **LangChain**, **Ollama**, **ChromaDB**, **FastAPI**, and **Streamlit**. The application enables users to query enterprise documents using natural language and provides accurate, context-aware responses with source citations through a Retrieval-Augmented Generation (RAG) pipeline.

---

## Features

- Intelligent document question answering
- Multi-agent architecture using LangGraph
- Retrieval-Augmented Generation (RAG)
- Metadata-aware document retrieval
- Source citations for every response
- Supports multiple document formats:
  - PDF
  - DOCX
  - PPTX
  - Excel (XLSX)
- FastAPI backend
- Streamlit web interface
- Local LLM inference using Ollama
- ChromaDB vector database

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | LangGraph |
| LLM Framework | LangChain |
| Large Language Model | Ollama (Llama 3.2) |
| Embedding Model | nomic-embed-text |
| Vector Database | ChromaDB |
| Backend API | FastAPI |
| Frontend | Streamlit |
| Programming Language | Python |

---

# Project Architecture

```text
                    +----------------------+
                    |      User            |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |   Streamlit UI       |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |      FastAPI         |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | LangGraph Workflow   |
                    +----------+-----------+
                               |
       ---------------------------------------------------------
       |              |              |              |            |
       v              v              v              v            v

 +-------------+ +-------------+ +-------------+ +-------------+ +-------------+
 | Planner     | | Retriever   | | Reasoning   | | Citation    | | Logger      |
 | Agent       | | Agent       | | Agent       | | Agent       | | Agent       |
 +------+------+ +------+------+ +------+------+ +------+------+ +------+------+
        |               |               |               |               |
        |               |               |               |               |
        |               v               |               |               |
        |      +--------------------+   |               |               |
        |      |    ChromaDB        |   |               |               |
        |      | Vector Database    |   |               |               |
        |      +---------+----------+   |               |               |
        |                |              |               |               |
        |                |              |               |               |
        |        Document Embeddings    |               |               |
        |                               |               |               |
        +-------------------------------+---------------+---------------+
                                        |
                                        v
                              Final Response with Citations
```

---

# Multi-Agent Workflow

### Planner Agent

- Understands the user's question
- Identifies the query intent
- Determines the relevant document type
- Passes retrieval instructions to the Retriever Agent

### Retriever Agent

- Performs metadata-aware semantic search
- Retrieves relevant document chunks from ChromaDB
- Filters by document type when applicable

### Reasoning Agent

- Uses the retrieved context
- Generates accurate natural language responses
- Avoids hallucinations by relying on retrieved documents

### Citation Agent

- Adds source references
- Includes filename, page number, slide number, or row metadata when available

### Logger Agent

- Logs user queries
- Records retrieved sources
- Captures execution information for debugging

---

# Supported Documents

| Format | Retrieval Strategy |
|---------|--------------------|
| PDF | Page-based chunking |
| DOCX | Heading-based chunking |
| PPTX | Slide-wise retrieval |
| Excel | Row-wise retrieval with metadata |

---

# Project Structure

```
enterprise-knowledge-assistant/
│
├── agents/
│   ├── planner.py
│   ├── retriever.py
│   ├── reasoning.py
│   ├── citation.py
│   └── logger.py
│
├── ingestion/
│   ├── loader.py
│   └── build_index.py
│
├── database/
│   └── chroma_db/
│
├── documents/
│
├── frontend/
│
├── api.py
├── app.py
├── requirements.txt
└── README.md
```

---

# Retrieval Pipeline

```
User Question
      │
      ▼
Planner Agent
      │
      ▼
Retriever Agent
      │
      ▼
ChromaDB
      │
      ▼
Relevant Context
      │
      ▼
Reasoning Agent
      │
      ▼
Citation Agent
      │
      ▼
Logger Agent
      │
      ▼
Response
```

---

# Installation

## Clone the Repository

```bash
git clone https://github.com/abrahamsamuelsmithpaul/enterprise-knowledge-assistant-ai.git

cd enterprise-knowledge-assistant-ai
```

---

## Create Virtual Environment

Windows

```bash
python -m venv .venv
```

Activate

PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment

Create a `.env` file.

Example:

```env
OLLAMA_BASE_URL=your llm (I used OLLAMA)
LLM_MODEL=llama3.2:latest
EMBEDDING_MODEL=nomic-embed-text:latest
```

---

## Build the Vector Database

```bash
python ingestion/build_index.py
```

---

## Run FastAPI

```bash
uvicorn api:app --reload
```

---

## Run Streamlit

Open another terminal.

```bash
streamlit run app.py
```

---

# Example Queries

- Summarize the client presentation.
- Explain the Marketing Mart architecture.
- What is the Customer ID mapping?
- Which slide discusses system architecture?
- List the key findings from the report.
- Explain the business process described in the document.

---

# Future Enhancements

- Hybrid Search (Keyword + Semantic)
- Query Expansion
- Reranking Models
- Conversation Memory
- User Authentication
- Role-Based Access Control
- Document Upload from UI
- Cloud Deployment
- Multi-user Support
- Support for SharePoint and Google Drive

---

# Screenshots
Home Screen

> <img width="1356" height="605" alt="image" src="https://github.com/user-attachments/assets/71434735-4567-4882-9b06-4ae0dc332f72" />

Query Interface
<img width="1326" height="602" alt="image" src="https://github.com/user-attachments/assets/dc52ba49-a9e4-49f2-893e-5ffa9bd9b11f" />

Generated Response
<img width="1365" height="610" alt="image" src="https://github.com/user-attachments/assets/fc9132e8-cf22-45e7-8bb6-102c66b801bb" />


Citation Display
<img width="1360" height="606" alt="image" src="https://github.com/user-attachments/assets/27f7b2b0-877f-4063-973f-4e0f292ed07d" />


---

 # Demo
 
<img width="1356" height="610" alt="12" src="https://github.com/user-attachments/assets/64311ac7-dd2c-402d-9e02-fa45c088b54f" />

-----


 # Document
 
[Enterprise_Knowledge_Assistant_Capstone_Report.docx](https://github.com/user-attachments/files/30429792/Enterprise_Knowledge_Assistant_Capstone_Report.docx)

-----

# Author

**Abraham Samuel**

GitHub:

https://github.com/abrahamsamuelsmithpaul

---

# License

This project is licensed under the MIT License.
