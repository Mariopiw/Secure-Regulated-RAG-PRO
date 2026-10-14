# Interview Q&A

1. **Why RAG instead of fine-tuning?** RAG updates factual knowledge without retraining; fine-tuning changes learned behavior.
2. **Why PostgreSQL + pgvector?** Relational metadata, transactions, RLS and vectors stay in one mature system.
3. **Why hybrid search?** Vector search captures meaning; lexical search catches exact identifiers and rare terms.
4. **What is RRF?** Reciprocal Rank Fusion combines rankings rather than incomparable raw scores.
5. **Why HNSW?** Fast approximate nearest-neighbor retrieval with a tunable speed/recall trade-off.
6. **How do you isolate tenants?** Explicit tenant filters plus PostgreSQL RLS.
7. **Does RAG eliminate hallucination?** No. I add abstention, citation checks and evaluation.
8. **How are citations verified?** The application checks that model-returned source IDs were actually supplied.
9. **Why fail closed?** Unverifiable answers should not silently look authoritative in regulated workflows.
10. **How do you reduce sensitive audit logging?** Store a hash and metadata rather than raw questions by default.
11. **What is prompt injection?** Attacker-controlled instructions alter model behavior contrary to application policy.
12. **Does the regex detector solve prompt injection?** No; it is telemetry only. Security relies on layered deterministic controls and testing.
13. **Why Alembic?** Production schemas require explicit versioned migrations.
14. **Why async SQLAlchemy?** Efficient concurrency for network-bound database/model calls.
15. **What metrics matter?** Recall@K, MRR, citation correctness, abstention accuracy, ASR, latency and error rates.
16. **What would you add before bank production?** Enterprise OIDC, secrets manager, TLS/mTLS, parser sandbox, malware scanning, rate limits, SIEM, retention/deletion workflows, load tests and independent review.

## 30-second pitch

I built a multi-tenant secure RAG platform for regulated document workflows using FastAPI, async SQLAlchemy, PostgreSQL/pgvector, HNSW and PostgreSQL full-text search. I fuse lexical and vector results with RRF, treat retrieved content as untrusted, require structured model output, verify citations deterministically, abstain on weak evidence, enforce tenant isolation in both application queries and PostgreSQL RLS, and include Argon2/JWT auth, audit logging, metrics, migrations, tests, CI and evaluation.
