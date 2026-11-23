# Secure Regulated RAG Pro

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)
![pgvector](https://img.shields.io/badge/Retrieval-pgvector%20%2B%20FTS-4169E1)
![Security](https://img.shields.io/badge/Tenant%20Isolation-RLS%20%2B%20App%20Checks-168A67)
[![CI](https://github.com/Mariopiw/Secure-Regulated-RAG-PRO/actions/workflows/ci.yml/badge.svg)](https://github.com/Mariopiw/Secure-Regulated-RAG-PRO/actions/workflows/ci.yml)

A **multi-tenant, security-focused Retrieval-Augmented Generation (RAG) reference platform** for internal document question answering. It combines tenant-scoped PostgreSQL storage, hybrid search, local LLM inference, source validation, and auditability.

**Core principle:** Retrieved documents and model output are **untrusted data**. Authorization, tenant isolation, citation checks and audit decisions must be enforced by application/database code rather than prompt instructions.

## Architecture

~~~mermaid
flowchart LR
   U["Authenticated client"] --> API["FastAPI + JWT"]
   API --> DB[("PostgreSQL + pgvector")]
   DB --> R["Vector + full-text search"]
   R --> F["Reciprocal Rank Fusion"]
   F --> L["Local Ollama LLM"]
   L --> V["Source ID / citation validation"]
   V --> A["Tenant-scoped answer + audit"]
~~~

## Capabilities

- **Multi-tenant access:** tenant-aware API filtering and PostgreSQL row-level security (RLS).
- **Hybrid retrieval:** pgvector approximate similarity and PostgreSQL full-text search combined with Reciprocal Rank Fusion.
- **Grounded answers:** retrieval thresholds, source references, deterministic citation validation, and abstention when evidence is insufficient.
- **Document ingestion:** text/PDF/DOCX parsing with size limits and tenant ownership.
- **Local AI:** configurable Ollama chat and embedding models.
- **Security & telemetry:** Argon2 password hashing, JWT authentication, audit events, structured logging and OpenTelemetry hooks.
- **Validation:** automated unit tests and a small question-set evaluation script; results require independent review.

## Local setup

Requirements: **Python 3.12+** for standalone tests; **Docker Compose** and **Ollama** for the integrated stack.

~~~bash
git clone https://github.com/Mariopiw/Secure-Regulated-RAG-PRO.git
cd Secure-Regulated-RAG-PRO

cp .env.example .env
# Edit .env: replace all demo passwords and JWT secret.
# Keep DB URLs, runtime passwords and embedding settings consistent.
# Pull models matching CHAT_MODEL / EMBEDDING_MODEL in your .env.
ollama list
docker compose up --build
~~~

Model names in the example environment are configuration defaults, **not a guarantee that those exact tags are installed on your system**. When running Ollama on a Linux host and the API in Docker, verify the host-bridge address and model endpoint. Running a larger local model on a 16-GB laptop may be slow; use a smaller tested model if needed.

After startup, open **http://localhost:8000/docs**. Authentication: <code>POST /auth/token</code>. Document ingestion: <code>POST /documents</code>. Retrieval-grounded question answering: <code>POST /query</code>. Use only **synthetic or approved** documents in your first tests.

## Test and evaluate

~~~bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest -q
ruff check .
~~~

The repo also contains <code>eval/questions.json</code> and <code>eval/run_eval.py</code> for evaluation workflows. Run them only after confirming the environment and test data. Unit tests alone do not validate multi-tenant isolation under all production conditions or establish factual accuracy for every question.

## Security boundaries and limitations

| Risk | Mitigation in the reference architecture | Important limit |
|---|---|---|
| Cross-tenant disclosure | App checks + PostgreSQL RLS | Needs deployment-specific verification |
| Hallucination | Grounding / abstention | Cannot guarantee every response is correct |
| Invented citations | Source-ID validation | Does not independently prove the source text is true |
| Prompt injection | Treat retrieved text as data | No universal prompt-injection immunity |
| Sensitive data | Access control + minimal audit data | Requires retention, privacy and access review |

**Compliance disclaimer:** This repository is not legal advice, GDPR certification, a DPIA, an independent penetration test or a production compliance guarantee. Do not upload client/customer confidential data without a reviewed privacy and security design.

## Documentation

[Architecture](ARCHITECTURE.md) · [Controls](CONTROL_MAPPING.md) · [Security](SECURITY.md) · [Evaluation](eval/) · [Tests](tests/) · [Interview Q&A](INTERVIEW_QA.md)

## License

See the repository's existing [LICENSE](LICENSE).
