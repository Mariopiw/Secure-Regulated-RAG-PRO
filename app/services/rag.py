import re
from app.core.config import settings
from app.services.ollama import ollama
from app.services.parsing import looks_like_prompt_injection
from app.services.retrieval import RetrievedSource

SOURCE_ID = re.compile(r"^S[1-9][0-9]*$")

def build_context(sources: list[RetrievedSource]) -> str:
    return "\n\n".join(
        f"SOURCE {s.source_id}\nfilename: {s.filename}\nlocator: {s.locator}\nchunk_index: {s.chunk_index}\nCONTENT START\n{s.content}\nCONTENT END"
        for s in sources
    )

def citations_are_valid(citations: list[str], sources: list[RetrievedSource]) -> bool:
    available = {s.source_id for s in sources}
    normalized = {c.strip().strip("[]") for c in citations}
    return bool(normalized) and all(SOURCE_ID.match(c) and c in available for c in normalized)

def evidence_is_too_weak(sources: list[RetrievedSource]) -> bool:
    if not sources:
        return True
    if any(s.lexical_hit for s in sources):
        return False
    similarities = [s.vector_similarity for s in sources if s.vector_similarity is not None]
    return bool(similarities) and max(similarities) < settings.min_vector_similarity

async def grounded_answer(question: str, sources: list[RetrievedSource]):
    suspicious_sources = sum(looks_like_prompt_injection(s.content) for s in sources)
    if evidence_is_too_weak(sources):
        return "Insufficient evidence in the retrieved sources.", True, True, suspicious_sources, []
    result = await ollama.answer(question, build_context(sources))
    valid = result.abstained or citations_are_valid(result.citations, sources)
    if not valid:
        return "Answer suppressed because source citations could not be verified.", True, False, suspicious_sources, []
    normalized = [c.strip().strip("[]") for c in result.citations]
    return result.answer, result.abstained, True, suspicious_sources, normalized
