# GyaanAI

GyaanAI is a document-based Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents, ask questions about their content, and receive answers supported by retrieved document sources and evaluation metrics.

## Deployed Application

**Live URL:**  
https://gyaanai.onrender.com/

## Features

- PDF document upload
- Automatic document indexing
- PDF text extraction
- Document chunking with overlapping chunks
- Semantic retrieval
- Keyword-based retrieval
- Hybrid retrieval using Reciprocal Rank Fusion
- Gemini-powered query analysis
- Gemini-powered answer generation
- Source references with page and chunk information
- RAG evaluation metrics
  - Faithfulness
  - Answer Relevancy
  - Context Precision
- Temporary document storage
- Automatic document expiration and cleanup
- Document filename preservation
- Light and dark themes
- Responsive React interface

## Tech Stack

### Frontend

- React
- Vite
- JavaScript
- CSS
- Lucide React

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic

### AI / RAG

- Google Gemini API
- Gemini embeddings
- Qdrant
- Semantic retrieval
- Keyword retrieval
- Reciprocal Rank Fusion
- LLM-based RAG evaluation

## Project Structure

```text
gyaan_ai/
│
├── backend/
│   └── app/
│       ├── api/
│       ├── core/
│       ├── documents/
│       ├── embeddings/
│       ├── generation/
│       ├── query/
│       ├── retrieval/
│       └── storage/
│
├── evaluation/
│   └── service.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── package-lock.json
│
├── data/
│
├── .gitignore
├── README.md
├── requirements.txt
└── test.py
````

## RAG Pipeline

```text
PDF Upload
    ↓
PDF Text Extraction
    ↓
Document Chunking
    ↓
Embedding Generation
    ↓
Qdrant Storage
    ↓
User Question
    ↓
Query Analysis
    ↓
┌───────────────────────┐
│ Semantic Retrieval    │
│ Keyword Retrieval     │
└───────────┬───────────┘
            ↓
Reciprocal Rank Fusion
            ↓
Relevant Contexts
            ↓
Gemini Answer Generation
            ↓
RAG Evaluation
            ↓
Answer + Sources + Metrics
```

## Evaluation Metrics

### Faithfulness

Measures how well the generated answer is supported by the retrieved document context.

```text
0.0 → Unsupported or mostly hallucinated
1.0 → Completely supported by the retrieved context
```

### Answer Relevancy

Measures how directly the generated answer addresses the user's question.

```text
0.0 → Does not answer the question
1.0 → Directly and completely addresses the question
```

### Context Precision

Measures how relevant the retrieved contexts are to answering the user's question.

```text
0.0 → Mostly irrelevant retrieved context
1.0 → Highly relevant retrieved context
```

All evaluation scores are normalized between `0` and `1`.

## Backend Setup

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
```

Run the backend:

```bash
uvicorn backend.app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## Frontend Setup

Move into the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create the frontend environment variable:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Run the development server:

```bash
npm run dev
```

Frontend:

```text
http://localhost:5173
```

## API Endpoints

### Upload Document

```http
POST /documents/upload
```

Uploads and indexes a PDF document.

### Ask a Question

```http
POST /documents/{document_id}/ask
```

Example request:

```json
{
  "question": "Summarise the main points"
}
```

Example response structure:

```json
{
  "document_id": "string",
  "question": "string",
  "answer": "string",
  "sources": [
    {
      "chunk_id": "string",
      "page": 1,
      "score": 0.0,
      "text": "string"
    }
  ],
  "metrics": {
    "faithfulness": 0.0,
    "answer_relevancy": 0.0,
    "context_precision": 0.0
  }
}
```

## Document Lifecycle

Uploaded documents are temporary.

```text
Upload PDF
    ↓
Index document
    ↓
Store metadata and vectors
    ↓
Ask questions
    ↓
Document expires
    ↓
Cleanup
    ├── Delete local PDF
    ├── Delete metadata
    └── Delete Qdrant vectors
```

## Environment Variables

### Backend

```env
GEMINI_API_KEY=
QDRANT_URL=
QDRANT_API_KEY=
```

### Frontend

```env
VITE_API_URL=
```

Never commit `.env` files or API keys to the repository.

## Deployment

The application is deployed on Render.

Frontend:

```text
https://gyaanai.onrender.com/
```

The frontend communicates with the deployed FastAPI backend through `VITE_API_URL`.

Environment variables are configured separately on the deployment platform.

## Development Workflow

Run the backend:

```bash
uvicorn backend.app.main:app --reload
```

Run the frontend in a separate terminal:

```bash
cd frontend
npm run dev
```
