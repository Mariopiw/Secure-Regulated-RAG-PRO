# Secure Regulated RAG PRO

Production-oriented reference implementation for **Applied AI + RAG + security + regulated industries**.

## What it proves

- FastAPI API engineering
- async SQLAlchemy
- PostgreSQL + pgvector
- HNSW vector search
- PostgreSQL full-text search
- hybrid retrieval with Reciprocal Rank Fusion
- local Ollama embeddings + generation
- deterministic citation validation
- abstention on weak evidence
- JWT + Argon2 authentication
- tenant filtering + PostgreSQL RLS
- audit logging with hashed questions
- Prometheus metrics
- optional OpenTelemetry tracing
- Alembic migrations
- tests + CI
- evaluation harness

## Architecture

```text
Documents
  -> parse
  -> chunk
  -> embeddings
  -> PostgreSQL/pgvector

Question
  -> authentication
  -> tenant isolation
  -> vector search + lexical search
  -> RRF fusion
  -> LLM over selected evidence
  -> deterministic citation validation
  -> answer / abstention
  -> audit + metrics
```

## Run

```bash
cp .env.example .env
openssl rand -hex 32
nano .env

ollama pull qwen3.5:4b
ollama pull embeddinggemma

docker compose up --build
```

Open:

```text
http://localhost:8000/docs
```

Then:

1. Login through `POST /auth/token`.
2. Upload `sample_data/company_ai_policy.txt` through `POST /documents`.
3. Ask: `How long are production AI audit records retained?`
4. Expected answer: 365 days with a verified source.
5. Ask an unanswerable question and verify abstention.

## Security model

The LLM is never the authorization boundary.

Tenant isolation exists at two levels:

```text
application query filters
+
PostgreSQL Row-Level Security
```

Retrieved content is treated as untrusted data. The system does not claim to eliminate prompt injection; it applies defense in depth and is designed to be tested with the companion red-team harness.

## Evaluation

```bash
export RAG_USERNAME=admin
export RAG_PASSWORD='YOUR_PASSWORD'
python eval/run_eval.py
```

The starter evaluation checks known answers, source correctness, citation validity, and abstention.

## Tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
ruff check .
```

## Interview story

> I built a multi-tenant regulated-document RAG platform using FastAPI, async SQLAlchemy, PostgreSQL and pgvector. I implemented hybrid lexical/vector retrieval with Reciprocal Rank Fusion, HNSW indexing, deterministic citation validation, explicit abstention, Argon2/JWT authentication, application-level tenant filtering plus PostgreSQL RLS, structured audit logging, Prometheus metrics, optional OpenTelemetry, migrations, CI and evaluation.

See also:

- `ARCHITECTURE.md`
- `SECURITY.md`
- `CONTROL_MAPPING.md`
- `INTERVIEW_QA.md`
