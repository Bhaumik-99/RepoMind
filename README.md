# RepoMind — AI-Powered GitHub Repository Assistant

RepoMind is a production-style GenAI starter that ingests a GitHub repository, indexes source code with embeddings, retrieves relevant code with vector search, and answers questions with source-level citations.

## Architecture

```text
GitHub URL
   ↓
Repository Fetch / File Filtering
   ↓
Language-aware Chunking
   ↓
Sentence-Transformer Embeddings
   ↓
FAISS Vector Index + Metadata
   ↓
Query → Retrieval → Prompt Construction
   ↓
LLM (OpenAI-compatible API or Ollama)
   ↓
Answer + File/Line Citations
```

## Features

- Public GitHub repository ingestion
- Python/Java/JavaScript/TypeScript/C++/Go/Rust/Markdown and common config formats
- Binary, dependency, generated-file and VCS filtering
- Line-aware code chunking
- Local embeddings using `sentence-transformers`
- FAISS vector search
- Repository-scoped RAG chat
- Source citations with file paths and line ranges
- AI code review endpoint
- Module documentation generation endpoint
- FastAPI backend with Pydantic schemas
- React + Vite frontend
- Docker Compose
- Pytest test suite
- GitHub Actions CI
- Simple retrieval evaluation harness

## Quick start

### 1. Clone the repository

Clone the actual RepoMind repository:

```bash
git clone https://github.com/Bhaumik-99/RepoMind.git
cd RepoMind
```

### 2. Configure environment

Create your local environment file:

```bash
cp .env.example .env
```

For hosted LLMs, set `OPENAI_API_KEY` and optionally `OPENAI_MODEL`.

For local inference, install Ollama and set:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.2
```

### 3. Run with Docker

From the project root:

```bash
docker compose up --build
```

Frontend: http://localhost:5173  
API docs: http://localhost:8000/docs

### 4. Run without Docker

Backend:

```bash
cd backend
python -m venv .venv
```

Windows:

```bash
.venv\\Scripts\\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies and start the API:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

In a second terminal, start the frontend:

```bash
cd frontend
npm install
npm run dev
```

## API

### Ingest repository

`POST /api/repos/ingest`

```json
{
  "repo_url": "https://github.com/tiangolo/fastapi",
  "branch": "master"
}
```

### Ask a question

`POST /api/chat`

```json
{
  "repo_id": "<returned-id>",
  "question": "Where is dependency injection handled?",
  "top_k": 6
}
```

### Review code

`POST /api/review`

### Generate module docs

`POST /api/docs/generate`

## Evaluation

RepoMind includes a small retrieval evaluation script. Replace the sample questions with a gold set from your selected repositories and measure Recall@K / MRR before making resume claims.

```bash
cd backend
python -m app.evaluation.run_eval
```

## Project structure

```text
repomind/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── evaluation/
│   │   ├── ingestion/
│   │   ├── llm/
│   │   ├── rag/
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
├── tests/
├── .github/workflows/ci.yml
├── docker-compose.yml
├── Dockerfile
└── .env.example
```

## Resume positioning

Do not claim benchmark numbers until you run an evaluation set. A defensible bullet is:

> Built a GenAI-powered GitHub codebase assistant using RAG, local embeddings, FAISS and an LLM, with line-level source citations, repository ingestion, AI code review and automated documentation generation.

## Next production upgrades

- PostgreSQL + pgvector metadata persistence
- Celery/RQ background ingestion jobs
- Redis caching and rate limiting
- OAuth GitHub App instead of cloning anonymous URLs
- Tree-sitter AST chunking for stronger code boundaries
- Streaming responses via SSE/WebSockets
- Ragas/DeepEval evaluation suite
- PR review comments through GitHub App permissions
- Multi-tenant auth and encrypted credential storage

## Current scope

The included starter supports public GitHub repository ingestion, RAG chat, file-level code review, generated module documentation, local embeddings, and CI. Full GitHub App OAuth and automatic PR comment publishing are deliberately left as production extensions rather than pretending they are implemented.
