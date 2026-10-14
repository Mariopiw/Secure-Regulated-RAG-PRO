import hashlib

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.observability import DOCUMENTS_INGESTED
from app.core.security import get_current_user, tenant_session
from app.models import Chunk, Document, User
from app.schemas import DocumentOut, IngestResponse
from app.services.audit import write_audit
from app.services.ollama import ollama
from app.services.parsing import chunk_text, extract_units, looks_like_prompt_injection

router = APIRouter(prefix="/documents", tags=["documents"])

async def embed_in_batches(texts: list[str], batch_size: int = 32) -> list[list[float]]:
    vectors = []
    for start in range(0, len(texts), batch_size):
        vectors.extend(await ollama.embed(texts[start:start + batch_size]))
    return vectors

@router.post("", response_model=IngestResponse, status_code=201)
async def ingest_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(tenant_session),
):
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(raw) > settings.max_file_bytes:
        raise HTTPException(status_code=413, detail="File exceeds configured limit")
    filename = file.filename or "upload.bin"
    if not filename.lower().endswith((".pdf", ".docx", ".txt")):
        raise HTTPException(status_code=415, detail="Supported formats: PDF, DOCX, TXT")

    digest = hashlib.sha256(raw).hexdigest()
    duplicate = await session.scalar(select(Document).where(Document.tenant_id == current_user.tenant_id, Document.sha256 == digest))
    if duplicate:
        raise HTTPException(status_code=409, detail=f"Already ingested as {duplicate.id}")

    try:
        units = extract_units(filename, raw)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Extraction failed: {exc}") from exc

    staged = []
    for unit in units:
        for chunk in chunk_text(unit.text):
            staged.append((unit.locator, chunk, looks_like_prompt_injection(chunk)))
    if not staged:
        raise HTTPException(status_code=422, detail="No extractable text. OCR is intentionally outside this reference MVP.")

    vectors = await embed_in_batches([content for _, content, _ in staged])
    suspicious_count = sum(flag for _, _, flag in staged)

    document = Document(
        tenant_id=current_user.tenant_id,
        filename=filename,
        content_type=file.content_type or "application/octet-stream",
        sha256=digest,
        uploaded_by=current_user.id,
        chunk_count=len(staged),
    )
    session.add(document)
    await session.flush()

    for index, ((locator, content, suspicious), vector) in enumerate(zip(staged, vectors)):
        session.add(Chunk(
            document_id=document.id,
            tenant_id=current_user.tenant_id,
            chunk_index=index,
            locator=locator,
            content=content,
            metadata_json={"prompt_injection_like_text": suspicious},
            embedding=vector,
        ))

    await write_audit(session, current_user, "document.ingested", "document", document.id, {
        "filename": filename,
        "sha256": digest,
        "chunks": len(staged),
        "suspicious_chunks": suspicious_count,
    })
    await session.commit()
    DOCUMENTS_INGESTED.inc()
    return IngestResponse(document_id=document.id, filename=filename, chunks_created=len(staged), suspicious_chunks=suspicious_count)

@router.get("", response_model=list[DocumentOut])
async def list_documents(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(tenant_session)):
    stmt = select(Document).where(Document.tenant_id == current_user.tenant_id).order_by(Document.created_at.desc())
    return list((await session.scalars(stmt)).all())
