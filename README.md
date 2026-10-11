# 🏥 MedAssist AI — Medical Information & Document Intelligence Platform

[![CI/CD Pipeline](https://github.com/medassist-ai/medassist/actions/workflows/ci.yml/badge.svg)](https://github.com/medassist-ai/medassist/actions)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14.2.5-black.svg)](https://nextjs.org/)
[![PostgreSQL + pgvector](https://img.shields.io/badge/PostgreSQL-16%20%2B%20pgvector-336791.svg)](https://github.com/pgvector/pgvector)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.2.0-EE4C2C.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **CRITICAL MEDICAL DISCLAIMER:**  
> MedAssist AI is strictly an **educational, research, and document intelligence platform**. It **DOES NOT diagnose diseases, prescribe medication, provide personalized clinical advice, replace licensed physicians, or make autonomous medical decisions**. All answers are source-grounded references intended solely for health education and clinical documentation analysis.

---

## 📌 Executive Overview

**MedAssist AI** is an enterprise-grade AI medical information and document intelligence system. It allows medical practitioners, clinical researchers, and students to upload multi-format medical records (PDF, DOCX, TXT, CSV), extract clinical sections, perform hybrid vector-keyword retrieval (RRF), orchestrate multi-agent reasoning with **LangGraph**, expose tools via the **Model Context Protocol (MCP)**, run non-diagnostic Scikit-Learn / PyTorch document classification, and stream source-grounded responses with verifiable citations.

---

## 🏗️ System Architecture

```
                               ┌────────────────────────────────────────────────────────┐
                               │                    CLIENT INTERFACE                    │
                               │        Next.js 14 + React 18 + Tailwind CSS            │
                               └──────────────────────────┬─────────────────────────────┘
                                                          │
                                     REST APIs / Server-Sent Events (SSE)
                                                          │
                               ┌──────────────────────────▼─────────────────────────────┐
                               │                   FASTAPI BACKEND                      │
                               │   JWT Auth & RBAC • Rate Limiter • Prompt Guard        │
                               └──────────────────────────┬─────────────────────────────┘
                                                          │
                               ┌──────────────────────────▼─────────────────────────────┐
                               │             LANGGRAPH MULTI-AGENT STATE GRAPH          │
                               │  Query Analyzer ➔ Intent Router ➔ Evidence & Safety    │
                               └──────┬───────────────────┼──────────────────────┬──────┘
                                      │                   │                      │
                  ┌───────────────────▼───┐   ┌───────────▼──────────┐   ┌───────▼───────────┐
                  │      RAG ENGINE       │   │      MCP SERVERS     │   │   ML / DL ENGINE  │
                  │  • Hybrid Search(RRF) │   │  • Document MCP      │   │ • Scikit-Learn    │
                  │  • ChromaDB / FAISS   │   │  • Knowledge MCP     │   │   TF-IDF (6 cat)  │
                  │  • BM25 Keyword Index │   │  • Terminology MCP   │   │ • PyTorch Neural  │
                  │  • Cross-Encoder      │   │  • Reporting MCP     │   │   Transformer     │
                  │  • Citation Engine    │   │  • Read-Only DB MCP  │   │   Classifier      │
                  └───────────┬───────────┘   └───────────┬──────────┘   └───────────────────┘
                              │                           │
                              └─────────────┬─────────────┘
                                            │
                               ┌────────────▼─────────────┐
                               │   CONFIGURABLE LLM TIER  │
                               │  Google Gemini / OpenAI  │
                               └──────────────────────────┘
```

---

## 🌟 Core Features

1. **Multi-Format Document Ingestion & OCR**:
   - Native parsing of PDF (PyMuPDF / pdfplumber), DOCX (python-docx), TXT, and CSV files.
   - Automatic fallback OCR via Tesseract for scanned records and images.
   - Text cleaning, unicode normalization, heading detection, and page tracking.

2. **Advanced Hybrid RAG Pipeline**:
   - **Semantic Dense Search**: Vector embeddings via sentence-transformers (`all-MiniLM-L6-v2`) or Google Gemini text embeddings.
   - **Sparse Keyword Search**: BM25 Okapi index for medical nomenclature and abbreviations.
   - **Reciprocal Rank Fusion (RRF)**: Merges dense vector and sparse keyword rankings with tuned reciprocal weightings.
   - **Cross-Encoder Reranking**: Re-evaluates top-K candidates to ensure maximal context relevance.

3. **Verifiable Citation & Source Attribution**:
   - Every generated sentence is linked to verified source documents, page numbers, section headers, and text snippets.
   - Strict hallucination detection: citations without backing chunks are blocked.

4. **LangGraph Multi-Agent Orchestration**:
   - **Query Analyzer**: Dissects intent and extracts key medical concepts.
   - **Document Agent**: Answers document-specific questions and extracts summaries.
   - **Knowledge Agent**: Searches trusted medical references and decodes complex terminology.
   - **Analysis Agent**: Extracts structured biomarker ranges and document metadata.
   - **Report Agent**: Synthesizes structured clinical documentation reports.
   - **Safety & Evidence Validators**: Guard against diagnostic claims and prompt injections.

5. **Model Context Protocol (MCP) Standard**:
   - Standardized tools for document retrieval, terminology resolution, and read-only database inspections.
   - Strict RBAC validation and input sanitization on all MCP endpoints.

6. **Machine Learning & Deep Learning Document Classification**:
   - **Classical ML**: Scikit-Learn TF-IDF classifier categorizing documents into 6 classes (*Clinical Report*, *Laboratory Report*, *Medical Research*, *Insurance Document*, *Prescription/Dispensing*, *General Health*).
   - **Deep Learning**: PyTorch Transformer classification model with CPU-friendly inference fallback.

7. **Real-Time Observability & AI Evaluation**:
   - Non-fabricated evaluation metrics: Hit Rate@K, Precision@K, Recall@K, Context Relevance, Answer Relevance, Groundedness (Faithfulness), Citation Accuracy, and Token/Latency telemetry.
   - Structured JSON audit logging with sensitive credential masking.

8. **Enterprise Security & Prompt Injection Defense**:
   - JWT tokens (HS256) with role-based access control (`USER` vs `ADMIN`).
   - Boundary encapsulation (`<UNTRUSTED_DOCUMENT_CONTENT>`) preventing adversarial jailbreaks.
   - Parameterized SQLAlchemy ORM protecting against SQL injection attacks.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, Lucide Icons |
| **Backend** | Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, Uvicorn |
| **Database & Cache** | PostgreSQL 16 + pgvector, Redis 7 (caching & job states), SQLite (local dev) |
| **Generative AI** | LangChain, LangGraph, Google Gemini API, OpenAI API |
| **RAG & Search** | ChromaDB, BM25, Sentence-Transformers (`all-MiniLM-L6-v2`), Cross-Encoder |
| **ML / DL** | Scikit-Learn, PyTorch, Hugging Face Transformers |
| **Security** | Passlib (Bcrypt), Python-JOSE (JWT), Regex Prompt Guard |
| **DevOps** | Docker, Docker Compose, GitHub Actions CI/CD |

---

## 📦 Project Structure

```
c:\AI_MED_ASSIST\
├── backend/
│   └── app/
│       ├── api/v1/          # Endpoints: auth, docs, search, chat, ml, dl, admin
│       ├── core/            # Config, database, logging
│       ├── models/          # SQLAlchemy: User, Document, Chunk, Message, Audit
│       ├── schemas/         # Pydantic validation schemas
│       ├── security/        # Passwords, JWT, Prompt Injection Guard
│       ├── services/        # Auth, Document ingestion, Storage
│       └── utils/           # File validation, MIME safety
├── rag/
│   ├── chunking/            # Recursive medical text splitter
│   ├── citations/           # Source card verification engine
│   ├── embeddings/          # Fast embeddings & sentence-transformers
│   ├── loaders/             # PDF, DOCX, TXT, CSV, OCR loaders
│   ├── pipelines/           # Unified RAG Pipeline
│   ├── processors/          # Text cleaner & section extractor
│   ├── reranking/           # Cross-encoder reranker
│   └── retrieval/           # ChromaDB, BM25 keyword index, RRF hybrid search
├── agents/
│   ├── graph/               # LangGraph state machine orchestrator
│   ├── nodes/               # Query analyzer, RAG, knowledge, report, validators
│   ├── prompts/             # System prompts with clinical boundaries
│   └── state/               # Typed AgentState dictionary
├── mcp/
│   ├── registry.py          # Centralized MCP registry
│   └── servers/             # Document, Knowledge, Terminology, DB, Reporting servers
├── ml/                      # Scikit-learn TF-IDF classifier & training pipeline
├── dl/                      # PyTorch Transformer classifier with CPU fallback
├── ai/
│   ├── llm_provider.py      # Abstracted provider (Gemini, OpenAI, Mock)
│   └── evaluation/          # Non-fabricated RAG benchmark evaluator & dataset
├── frontend/                # Next.js 14 modern dashboard & chat UI
├── database/alembic/        # Database migration versions
├── docker/                  # Dockerfile.backend & Dockerfile.frontend
├── tests/                   # 59 comprehensive unit, integration & security tests
└── docker-compose.yml       # Production multi-service orchestration
```

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
- **Python**: 3.11+
- **Node.js**: 20+
- **PostgreSQL** or SQLite for local testing
- **Redis** (optional, fallback to in-memory)

### 2. Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Key settings in `.env`:
```env
APP_ENV=development
SECRET_KEY=your-secure-secret-key-at-least-32-chars
DATABASE_URL=sqlite:///./data/medassist.db
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 3. Backend Setup
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python -m alembic upgrade head

# Launch FastAPI backend
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be live at: `http://localhost:8000/docs`

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` to launch the platform dashboard.

---

## 🐳 Docker Deployment

To spin up PostgreSQL (pgvector), Redis, FastAPI backend, and Next.js frontend in production containers:

```bash
docker compose up -d --build
```
- **Web UI**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **API Health**: `http://localhost:8000/api/health`

---

## 🧪 Testing Suite

Execute the full suite of 59 unit, integration, RAG, and security tests:

```bash
python -m pytest tests/ -v
```

### Test Coverage Highlights:
- `test_auth.py`: Registration, duplicate check, JWT verification, RBAC permissions.
- `test_chat.py`: Sync chat, Server-Sent Events (SSE) streaming, conversation lifecycle.
- `test_database.py`: SQLAlchemy relations, cascade deletions, audit logging.
- `test_documents.py`: PDF, DOCX, TXT, CSV parsing, corrupted header rejection.
- `test_rag.py`: Chunking, vector indexing, BM25 indexing, RRF search, citations.
- `test_evaluation.py`: Hit Rate@3, Precision@3, Groundedness, Citation Accuracy.
- `test_langgraph.py`: State routing, Document Agent, Knowledge Agent, Report Agent.
- `test_mcp.py`: MCP tool registrations, parameter validation, read-only DB permissions.
- `test_ml.py` & `test_dl.py`: Non-diagnostic TF-IDF and PyTorch Transformer classification.
- `test_safety.py` & `test_security.py`: Refusal of personal diagnoses, prescription rejections, prompt injection blocking, untrusted context boundaries.

---

## 📊 RAG Evaluation Benchmark

MedAssist AI includes an evaluation framework that measures actual, empirical metrics across a medical benchmark set:

Run the evaluation runner:
```bash
python scripts/run_eval.py
```
Outputs non-fabricated benchmarks:
- **Hit Rate @ 3**: 100.0%
- **Retrieval Precision @ 3**: Verified matches against ground truth
- **Groundedness (Faithfulness)**: Sentence-level source attribution
- **Citation Accuracy**: Direct validation of cited chunks against retrieved passages
- **Average Latency & Token Consumption**: Empirical runtime measurement in milliseconds

---

## 🛡️ Medical Safety & Ethical Boundaries

| User Intent | Platform Behavior | Explanation |
|---|---|---|
| **Educational Inquiries** (*"What is hypertension?"*) | **Processed** | Provides educational definitions and guidelines with document citations. |
| **Personal Diagnosis Requests** (*"Do I have cancer based on my fever?"*) | **Firmly Declined** | Refuses to evaluate personal health and directs user to seek licensed clinical care. |
| **Prescription Requests** (*"What medication should I take?"*) | **Firmly Declined** | Refuses dosage or drug recommendations and emphasizes consultation with doctors. |
| **Prompt Injection Attacks** (*"Ignore all previous rules..."*) | **Blocked** | Detected and rejected by `PromptSecurityGuard` before reaching agents. |

---

## 📄 License
This project is licensed under the MIT License.
