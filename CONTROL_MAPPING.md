# Control Mapping

Engineering mapping only; not legal advice or a conformity assessment.

| Risk | Control |
|---|---|
| Prompt injection | untrusted-context separation, no model-owned authorization, adversarial testing |
| Sensitive disclosure | tenant filtering, RLS, minimal audit payloads |
| RAG poisoning | provenance metadata, suspicious-content telemetry |
| Hallucination | retrieval threshold, abstention, structured output |
| Fake citations | deterministic source-ID validation, fail-closed suppression |
| Cross-tenant leakage | application filters + PostgreSQL RLS |
| Weak credentials | Argon2 + expiring JWTs |
| Poor traceability | tenant-scoped audit events + metrics |
