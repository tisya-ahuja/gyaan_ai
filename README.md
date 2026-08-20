
# GyaanAI

GyaanAI is a document-based RAG application that allows users to upload PDF documents and ask questions about their contents.

## Deployed Application

**Live URL:**  
[Add deployed link here]

## Features

- PDF document upload
- Document text extraction and chunking
- Semantic retrieval
- Keyword-based retrieval
- Hybrid retrieval using Reciprocal Rank Fusion
- Gemini-powered answer generation
- Source citations with page and chunk information
- RAG evaluation metrics:
  - Faithfulness
  - Answer Relevancy
  - Context Precision
- Automatic document expiration and cleanup
- Responsive React frontend
- Minimalist UI with light and dark themes

## Tech Stack

### Frontend

- React
- Vite
- JavaScript
- CSS
- Lucide React
- Epilogue
- Baskervville

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic

### AI / RAG

- Google Gemini API
- Embeddings
- Qdrant
- Semantic Retrieval
- Keyword Retrieval
- Reciprocal Rank Fusion
- RAG evaluation

## Project Structure

```text
gyaan_ai/
│
├── backend/
│   └── app/
│       ├── api/
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
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   └── index.html
│
├── data/
│
├── .env
├── .gitignore
└── README.md
````

## Backend Setup

Create and activate the virtual environment:

```bash
python -m venv venv
```

### Windows

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
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

Example:

```json
{
  "question": "Summarise the main points"
}
```

The response contains:

```json
{
  "document_id": "string",
  "question": "string",
  "answer": "string",
  "sources": [],
  "metrics": {
    "faithfulness": 0.0,
    "answer_relevancy": 0.0,
    "context_precision": 0.0
  }
}
```

## RAG Pipeline

```text
PDF Upload
    ↓
PDF Extraction
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
Semantic Retrieval + Keyword Retrieval
    ↓
Reciprocal Rank Fusion
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

### Answer Relevancy

Measures how directly the generated answer addresses the user's question.

### Context Precision

Measures how relevant the retrieved contexts are to answering the user's question.

All evaluation scores are normalized between `0` and `1`.

## Environment Variables

```env
GEMINI_API_KEY=
```

Never commit `.env` or API keys to the repository.

## Development

Run the backend:

```bash
uvicorn backend.app.main:app --reload
```

Run the frontend in a separate terminal:

```bash
cd frontend
npm run dev
```

## Deployment

The frontend and backend can be deployed separately and connected through the backend API URL.

Environment variables must be configured on the deployment platform.

## Deployed Link

```text
https://
```
