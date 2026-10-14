import uuid
from datetime import datetime
from pydantic import BaseModel, Field

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=120)
    password: str = Field(min_length=12, max_length=200)
    role: str = Field(default="analyst", pattern="^(admin|analyst)$")

class UserOut(BaseModel):
    id: uuid.UUID
    username: str
    tenant_id: uuid.UUID
    role: str
    model_config = {"from_attributes": True}

class DocumentOut(BaseModel):
    id: uuid.UUID
    filename: str
    content_type: str
    sha256: str
    chunk_count: int
    created_at: datetime
    model_config = {"from_attributes": True}

class IngestResponse(BaseModel):
    document_id: uuid.UUID
    filename: str
    chunks_created: int
    suspicious_chunks: int

class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)

class CitationOut(BaseModel):
    source_id: str
    document_id: uuid.UUID
    filename: str
    locator: str
    chunk_index: int
    vector_similarity: float | None = None
    rrf_score: float

class QueryResponse(BaseModel):
    query_id: uuid.UUID
    answer: str
    abstained: bool
    citation_valid: bool
    suspicious_question: bool
    suspicious_sources: int
    citations: list[CitationOut]

class AuditOut(BaseModel):
    id: uuid.UUID
    action: str
    object_type: str
    object_id: str
    detail: dict
    created_at: datetime
    model_config = {"from_attributes": True}
