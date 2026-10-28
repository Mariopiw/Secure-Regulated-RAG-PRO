# Secure Regulated RAG

A multi-tenant document question-answering reference application using retrieval-augmented generation (RAG), source citations, and access controls.

## Key features

- FastAPI, PostgreSQL/pgvector, and hybrid retrieval
- Local Ollama embeddings and response generation
- Citation validation and abstention when evidence is insufficient
- Authentication, tenant filtering, PostgreSQL row-level security, and audit logging
- Automated tests and evaluation tools

## Quick start

Requires Docker Compose and Ollama. Set strong local credentials and secrets in `.env`.

```bash
cp .env.example .env
# Edit .env before starting
ollama pull qwen3.5:4b
ollama pull embeddinggemma
docker compose up --build
```

API documentation: http://localhost:8000/docs

Authenticate using `POST /auth/token`, upload a sample document through `POST /documents`, and test whether answers cite the retrieved sources.

## Tests

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
ruff check .
```

**Scope:** A security-focused reference implementation, not a guarantee of regulatory compliance or immunity to prompt injection. See `SECURITY.md` and `CONTROL_MAPPING.md`.
