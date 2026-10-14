import uuid
from fastapi import FastAPI, Request
from fastapi.responses import Response
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api import audit, auth, documents, health, query, users
from app.core.logging import configure_logging
from app.core.telemetry import configure_tracing

configure_logging()
configure_tracing()

app = FastAPI(
    title="Secure Regulated RAG Platform",
    version="1.0.0",
    description="Production-oriented reference architecture for secure, auditable RAG.",
)

@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response

@app.get("/metrics", include_in_schema=False)
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(query.router)
app.include_router(audit.router)
app.include_router(health.router)

FastAPIInstrumentor.instrument_app(app)
