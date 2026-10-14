# Architecture

```text
Client
  -> FastAPI
  -> JWT identity + tenant
  -> PostgreSQL tenant context
  -> hybrid retrieval
       -> pgvector HNSW
       -> PostgreSQL FTS
       -> RRF
  -> local LLM
  -> deterministic citation validation
  -> audit + metrics
```

## Trust boundaries

1. Client -> API
2. API -> PostgreSQL
3. API -> Ollama/model provider
4. Uploaded files -> parser
5. Retrieved text -> model context

PostgreSQL remains authoritative for tenant metadata, document ownership, chunks, and audit records.
