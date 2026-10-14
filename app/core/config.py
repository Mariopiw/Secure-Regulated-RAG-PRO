from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://rag_app:change-runtime-db-password@db:5432/rag"
    migration_database_url: str = "postgresql+asyncpg://rag_admin:change-admin-db-password@db:5432/rag"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60
    ollama_base_url: str = "http://host.docker.internal:11434"
    chat_model: str = "qwen3.5:4b"
    embedding_model: str = "embeddinggemma"
    embedding_dim: int = 768
    top_k_vector: int = 20
    top_k_lexical: int = 20
    top_k_final: int = 6
    rrf_k: int = 60
    min_vector_similarity: float = 0.28
    max_file_bytes: int = 15 * 1024 * 1024
    chunk_size_chars: int = 1400
    chunk_overlap_chars: int = 180
    bootstrap_admin_username: str = "admin"
    bootstrap_admin_password: str = "change-this-now"
    bootstrap_tenant_slug: str = "demo-bank"
    otel_exporter_otlp_endpoint: str = ""
    log_level: str = "INFO"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
