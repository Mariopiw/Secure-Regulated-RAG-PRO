# Security

Implemented controls:

- JWT authentication
- Argon2 password hashing
- tenant-scoped queries
- PostgreSQL Row-Level Security
- separate migration/runtime database roles
- file type and size limits
- duplicate detection with SHA-256
- prompt-like-content telemetry
- deterministic citation validation
- fail-closed suppression on invalid citations
- explicit abstention
- minimal audit logging using question hashes
- security headers
- structured logs and metrics

This is a production-oriented reference implementation, not a certification or claim that prompt injection or hallucination is solved.

Before real enterprise deployment add OIDC, secrets management, TLS/mTLS, malware scanning, parser sandboxing, rate limits, encrypted object storage, retention workflows, SIEM integration, load testing, backup/restore validation, and independent security/privacy review.
