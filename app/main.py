

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.databases import engine, Base
from app.routers import auth, documents


from app.models import user, document


app = FastAPI(
    title="SmartDoc NLP API",
    description="""
    ## Document Intelligence Platform
    Upload documents and get instant NLP analysis:
    - **Summarization** — extractive text summary
    - **Keywords** — top keywords by frequency
    - **Named Entities** — people, places, organizations
    - **Sentiment** — positive, negative, or neutral
    ## Authentication
    All endpoints except /health require a valid JWT Bearer token.
    Register at /api/v1/auth/register to get your token.
    """,
    version="1.0.0",
    docs_url="/docs",      
    redoc_url="/redoc"     
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


Base.metadata.create_all(bind=engine)


app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)
app.include_router(
    documents.router,
    prefix="/api/v1/documents",
    tags=["Documents"]
)

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "message": "SmartDoc NLP API is running"
    }

@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Welcome to SmartDoc NLP API",
        "docs": "/docs",
        "health": "/health"
    }