from prometheus_client import Counter, Histogram

RAG_QUERIES = Counter("rag_queries_total", "Total RAG queries", ["outcome"])
RAG_LATENCY = Histogram("rag_query_latency_seconds", "End-to-end RAG query latency")
DOCUMENTS_INGESTED = Counter("rag_documents_ingested_total", "Documents successfully ingested")
