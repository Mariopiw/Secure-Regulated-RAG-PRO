import time
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.observability import RAG_LATENCY, RAG_QUERIES
from app.core.security import get_current_user, tenant_session
from app.models import User
from app.schemas import CitationOut, QueryRequest, QueryResponse
from app.services.audit import sha256_text, write_audit
from app.services.parsing import looks_like_prompt_injection
from app.services.rag import grounded_answer
from app.services.retrieval import hybrid_retrieve

router = APIRouter(prefix="/query", tags=["query"])

@router.post("", response_model=QueryResponse)
async def query_documents(payload: QueryRequest, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(tenant_session)):
    started = time.perf_counter()
    query_id = uuid.uuid4()
    suspicious_question = looks_like_prompt_injection(payload.question)
    sources = await hybrid_retrieve(session, current_user.tenant_id, payload.question)
    answer, abstained, citation_valid, suspicious_sources, cited_ids = await grounded_answer(payload.question, sources)
    source_map = {s.source_id: s for s in sources}
    cited_sources = [source_map[sid] for sid in cited_ids if sid in source_map]
    await write_audit(session, current_user, "rag.query", "query", query_id, {
        "question_sha256": sha256_text(payload.question),
        "question_length": len(payload.question),
        "retrieved_source_ids": [s.source_id for s in sources],
        "cited_source_ids": cited_ids,
        "abstained": abstained,
        "citation_valid": citation_valid,
        "suspicious_question": suspicious_question,
        "suspicious_sources": suspicious_sources,
    })
    await session.commit()
    outcome = "abstained" if abstained else ("ok" if citation_valid else "citation_failure")
    RAG_QUERIES.labels(outcome=outcome).inc()
    RAG_LATENCY.observe(time.perf_counter() - started)
    return QueryResponse(
        query_id=query_id,
        answer=answer,
        abstained=abstained,
        citation_valid=citation_valid,
        suspicious_question=suspicious_question,
        suspicious_sources=suspicious_sources,
        citations=[
            CitationOut(
                source_id=s.source_id,
                document_id=s.document_id,
                filename=s.filename,
                locator=s.locator,
                chunk_index=s.chunk_index,
                vector_similarity=round(s.vector_similarity, 4) if s.vector_similarity is not None else None,
                rrf_score=round(s.rrf_score, 6),
            )
            for s in cited_sources
        ],
    )
