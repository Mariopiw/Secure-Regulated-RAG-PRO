import uuid
from dataclasses import dataclass
from sqlalchemy import desc, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models import Chunk, Document
from app.services.ollama import ollama

@dataclass
class RetrievedSource:
    source_id: str
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    filename: str
    locator: str
    chunk_index: int
    content: str
    vector_similarity: float | None
    rrf_score: float
    lexical_hit: bool = False
    suspicious: bool = False

async def hybrid_retrieve(session: AsyncSession, tenant_id: uuid.UUID, question: str) -> list[RetrievedSource]:
    query_vector = (await ollama.embed([question]))[0]
    await session.execute(text("SET LOCAL hnsw.ef_search = 100"))
    distance = Chunk.embedding.cosine_distance(query_vector).label("distance")
    vector_stmt = (
        select(Chunk, Document, distance)
        .join(Document, Document.id == Chunk.document_id)
        .where(Chunk.tenant_id == tenant_id, Document.tenant_id == tenant_id)
        .order_by(distance)
        .limit(settings.top_k_vector)
    )
    vector_rows = (await session.execute(vector_stmt)).all()

    tsquery = func.plainto_tsquery("simple", question)
    rank = func.ts_rank_cd(Chunk.textsearch, tsquery).label("lexical_rank")
    lexical_stmt = (
        select(Chunk, Document, rank)
        .join(Document, Document.id == Chunk.document_id)
        .where(Chunk.tenant_id == tenant_id, Document.tenant_id == tenant_id, Chunk.textsearch.op("@@")(tsquery))
        .order_by(desc(rank))
        .limit(settings.top_k_lexical)
    )
    lexical_rows = (await session.execute(lexical_stmt)).all()

    candidates = {}
    for position, (chunk, document, cosine_distance) in enumerate(vector_rows, 1):
        similarity = 1.0 - float(cosine_distance)
        candidates.setdefault(chunk.id, {"chunk":chunk,"document":document,"similarity":similarity,"score":0.0,"lexical_hit":False})
        candidates[chunk.id]["similarity"] = similarity
        candidates[chunk.id]["score"] += 1.0 / (settings.rrf_k + position)
    for position, (chunk, document, _rank) in enumerate(lexical_rows, 1):
        candidates.setdefault(chunk.id, {"chunk":chunk,"document":document,"similarity":None,"score":0.0,"lexical_hit":False})
        candidates[chunk.id]["score"] += 1.0 / (settings.rrf_k + position)
        candidates[chunk.id]["lexical_hit"] = True

    ranked = sorted(candidates.values(), key=lambda item: item["score"], reverse=True)[:settings.top_k_final]
    return [
        RetrievedSource(
            source_id=f"S{i}",
            chunk_id=item["chunk"].id,
            document_id=item["document"].id,
            filename=item["document"].filename,
            locator=item["chunk"].locator,
            chunk_index=item["chunk"].chunk_index,
            content=item["chunk"].content,
            vector_similarity=item["similarity"],
            rrf_score=float(item["score"]),
            lexical_hit=bool(item["lexical_hit"]),
        )
        for i,item in enumerate(ranked,1)
    ]
