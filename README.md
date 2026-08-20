# GyaanAI

GyaanAI is an end-to-end Retrieval-Augmented Generation (RAG) application that lets users upload PDF documents, ask questions about their contents, and receive grounded answers with retrieved sources and response-quality metrics.

## Deployed Application

**Live URL:**  
https://gyaanai.onrender.com/

## What It Demonstrates

- End-to-end RAG pipeline design and implementation
- Hybrid retrieval combining semantic and keyword search
- Document-scoped vector retrieval using Qdrant
- Grounded answer generation with source attribution
- LLM-as-a-judge evaluation
- Temporary document lifecycle and automatic cleanup
- FastAPI backend and React/Vite frontend integration
- Production deployment on Render

## Key Features

- PDF upload and text extraction
- Overlapping document chunking
- Gemini embeddings
- Semantic retrieval with Qdrant
- Keyword-based retrieval
- Reciprocal Rank Fusion
- Query analysis before retrieval
- Grounded Gemini answer generation
- Page- and chunk-level source references
- Faithfulness, Answer Relevancy, and Context Precision metrics
- 30-minute temporary document lifecycle
- Automatic cleanup of expired PDFs, metadata, and vectors
- Document restoration after browser refresh
- Responsive light and dark UI

## Architecture

```text
PDF Upload
    ↓
Text Extraction → Chunking → Embeddings → Qdrant

User Question
    ↓
Query Analysis
    ↓
 ┌──────────────────────┐
 │ Semantic Retrieval   │
 │ Keyword Retrieval    │
 └──────────┬───────────┘
            ↓
 Reciprocal Rank Fusion
            ↓
     Relevant Context
            ↓
      Gemini Generation
            ↓
      Answer + Sources
            ↓
       RAG Evaluation
            ↓
Faithfulness / Relevancy / Precision
```

## Technical Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, JavaScript, CSS, Lucide React |
| Backend | Python, FastAPI, Uvicorn, Pydantic |
| LLM | Google Gemini API |
| Embeddings | Gemini embeddings |
| Vector Database | Qdrant |
| PDF Processing | PyMuPDF |
| Retrieval | Semantic + keyword retrieval + Reciprocal Rank Fusion |
| Evaluation | LLM-as-a-judge |
| Deployment | Render |

## RAG Pipeline

### 1. Document Ingestion

PDF pages are extracted and divided into overlapping chunks while retaining document, chunk, and page metadata.

### 2. Embedding and Indexing

Each chunk is embedded and stored in Qdrant. Retrieval is scoped to the selected document.

### 3. Query Understanding

The question is analyzed into a search-oriented query and keywords for the retrieval stages.

### 4. Hybrid Retrieval

Semantic and keyword result lists are combined with Reciprocal Rank Fusion to improve retrieval robustness.

### 5. Grounded Generation

Gemini receives the retrieved context and is instructed to answer only from that context and cite supporting pages.

### 6. Evaluation

The generated answer and retrieved context are evaluated for faithfulness, answer relevancy, and context precision.

## Evaluation Metrics

### Faithfulness

Measures how well the generated answer is supported by the retrieved context.

```text
0.0 → Unsupported, contradicted, or mostly hallucinated
1.0 → Completely supported by the retrieved context
```

### Answer Relevancy

Measures how directly the generated answer addresses the user's question.

```text
0.0 → Does not answer the question
1.0 → Directly and completely addresses the question
```

### Context Precision

Measures how relevant the retrieved contexts are to answering the question.

```text
0.0 → Retrieved context is mostly irrelevant
1.0 → Retrieved context is highly relevant
```

Scores are normalized between 0 and 1.

## Document Lifecycle

Uploaded documents expire after 30 minutes.

```text
Upload → Index → Query → Expiry → Cleanup
                         ├── local PDF
                         ├── metadata
                         └── Qdrant vectors
```

## API

### Upload Document

```http
POST /documents/upload
```

Upload and index a PDF.

### List Active Documents

```http
GET /documents
```

Return active, non-expired documents.

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

Example response:

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

## Project Structure

```text
gyaan_ai/
├── backend/app/
│   ├── api/
│   ├── core/
│   ├── documents/
│   ├── embeddings/
│   ├── generation/
│   ├── query/
│   ├── retrieval/
│   └── storage/
├── evaluation/
├── frontend/src/
├── data/
├── requirements.txt
├── README.md
└── test.py
```

## Local Development

### Backend

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
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

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

## Environment Variables

### Backend

```env
GEMINI_API_KEY=your_gemini_api_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
```

### Frontend

```env
VITE_API_URL=https://gyaan-ai-x60f.onrender.com/
```

Secrets are stored outside the repository. `.env` files, virtual environments, `node_modules`, build output, and temporary application data are excluded by `.gitignore`.

## Deployment

The application is deployed on Render as separate frontend and backend services.

### Frontend

```text
Root Directory: frontend
Build Command: npm install && npm run build
Publish Directory: dist
```

### Backend

```text
Build Command: pip install -r requirements.txt
Start Command: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
Python Version: 3.13
```

The frontend receives the deployed FastAPI backend URL through:

```env
VITE_API_URL=https://your-backend-url
```

CORS is configured for local development and the deployed frontend origin.

## Engineering Highlights

- Hybrid retrieval reduces dependence on a single retrieval strategy.
- Document-scoped retrieval prevents unrelated documents from entering the context.
- Source metadata is preserved through retrieval and returned by the API.
- Evaluation is separated from generation so response quality can be inspected independently.
- Temporary expiry reduces long-term retention of uploaded documents.
- The codebase separates ingestion, retrieval, generation, evaluation, and storage concerns.

## Security

- API keys are stored in environment variables.
- `.env` files are excluded from Git.
- Uploaded documents are temporary.
- Expired documents are removed from local storage, metadata storage, and Qdrant.
- API keys are not exposed through the frontend.

## Repository

https://github.com/tisya-ahuja/gyaan_ai

## Future Improvements

- Persistent or object storage for stronger cloud durability
- Automated unit and integration tests in CI
- Repeatable retrieval-quality benchmarks and evaluation datasets
- Structured logging and request-level observability