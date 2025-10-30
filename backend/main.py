from backend.services.enhanced_rag_engine import Enhanced2025RAGEngine
from backend.services.enhanced_vector_store import EnhancedVectorStore
from backend.utils.enhanced_data_fetcher import Enhanced2025DataFetcher

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import time
import logging
from pathlib import Path
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Project Samarth API",
    description="🌾 Intelligent Q&A System for Indian Agricultural Data",
    version="2025.1.1",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vector_store = None
rag_engine = None
data_fetcher = None

class QueryRequest(BaseModel):
    question: str
    filters: Optional[Dict] = None
    include_policy_context: bool = True
    max_results: int = 5

class QueryResponse(BaseModel):
    answer: str
    citations: List[Dict]
    policy_context: List[Dict]
    processing_time: float
    confidence_score: float
    data_vintage: str

class DataUpdateRequest(BaseModel):
    source: str
    force_update: bool = False

@app.on_event("startup")
async def startup_event():
    global vector_store, rag_engine, data_fetcher
    logger.info("🚀 Starting Project Samarth API...")

    data_fetcher = Enhanced2025DataFetcher()
    logger.info("✅ Data fetcher initialized")

    # Initialize vector store
    vector_store = EnhancedVectorStore()

    # Try loading existing vectorstore; don't fail startup if missing
    vectorstore_path = Path("data/vectorstore_2025")
    if vectorstore_path.exists():
        try:
            vector_store.load_local(str(vectorstore_path))
            logger.info("✅ Vector store loaded from disk")
        except Exception as e:
            logger.warning(f"⚠️ Could not load vectorstore: {e}")
    else:
        logger.warning("⚠️ Vector store not found. You can create it with scripts/setup_data.py")

    use_openai = os.getenv("USE_OPENAI_EMBEDDINGS", "false").lower() == "true"
    rag_engine = Enhanced2025RAGEngine(vector_store=vector_store, use_local_llm=True)
    logger.info(f"✅ RAG engine initialized (USE_OPENAI_EMBEDDINGS={use_openai})")

@app.get("/")
def read_root():
    return {
        "message": "🌾 Project Samarth - Agricultural Data Q&A System",
        "version": "2025.1.1",
        "status": "operational",
        "endpoints": {"query": "/query", "health": "/health", "docs": "/docs"}
    }

@app.post("/query", response_model=QueryResponse)
async def query_system(request: QueryRequest):
    if not rag_engine:
        raise HTTPException(status_code=503, detail="System not ready")
    try:
        start = time.time()
        intent = rag_engine.parse_2025_query(request.question)
        context = rag_engine.retrieve_relevant_data(request.question, intent, k=request.max_results)
        result = rag_engine.generate_2025_enhanced_answer(request.question, context)
        processing_time = time.time() - start
        avg_score = sum(chunk.get('score', 0.5) for chunk in context) / len(context) if context else 0.5
        confidence_score = max(0.0, min(1.0, 1.0 - avg_score))
        return QueryResponse(
            answer=result['answer'],
            citations=result['citations'],
            policy_context=result.get('policy_context', []),
            processing_time=processing_time,
            confidence_score=confidence_score,
            data_vintage=result.get('data_vintage', '2025-edition')
        )
    except ImportError as ie:
        msg = str(ie)
        if 'sentence_transformers' in msg:
            raise HTTPException(
                status_code=500,
                detail=("Sentence Transformers not available. Run: "
                        "pip install -r requirements.txt -c constraints.txt. "
                        "Or set USE_OPENAI_EMBEDDINGS=true in .env with OPENAI_API_KEY.")
            )
        raise
    except Exception as e:
        logger.exception("Query failed")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {e}")

@app.get("/health")
def health_check():
    loaded = vector_store is not None and getattr(vector_store, 'vectorstore', None) is not None
    total = 0
    if loaded:
        try:
            total = vector_store.vectorstore.index.ntotal
        except Exception:
            total = 0
    return {"status": "healthy" if rag_engine else "degraded", "vectorstore_loaded": loaded, "total_documents": total}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
