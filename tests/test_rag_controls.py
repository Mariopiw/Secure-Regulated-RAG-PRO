import uuid
from app.services.rag import citations_are_valid, evidence_is_too_weak
from app.services.retrieval import RetrievedSource

def source(source_id: str, similarity: float = 0.8) -> RetrievedSource:
    return RetrievedSource(
        source_id=source_id,
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        filename="policy.txt",
        locator="page 1",
        chunk_index=0,
        content="Human approval is required.",
        vector_similarity=similarity,
        rrf_score=0.02,
        lexical_hit=False,
    )

def test_valid_citations_must_be_from_retrieved_sources():
    sources = [source("S1"), source("S2")]
    assert citations_are_valid(["S1"], sources)
    assert not citations_are_valid(["S9"], sources)
    assert not citations_are_valid([], sources)

def test_weak_evidence_abstains_early():
    assert evidence_is_too_weak([source("S1", similarity=0.01)])
    assert not evidence_is_too_weak([source("S1", similarity=0.80)])
